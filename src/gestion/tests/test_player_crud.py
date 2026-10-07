from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from src.gestion.models import Personaje, Raza, Habilidad, Objeto

User = get_user_model()

class PlayerPersonajeTests(TestCase):
    def setUp(self):
        # 1. Crear usuario jugador normal
        self.player1 = User.objects.create_user(username='player1', password='password123')
        # Crear un segundo usuario para pruebas de seguridad
        self.player2 = User.objects.create_user(username='player2', password='password123')
        
        # 2. Cliente y logueo
        self.client = Client()
        self.client.login(username='player1', password='password123')

        # 3. Crear datos base
        self.raza = Raza.objects.create(nombre='Elfo', descripcion='Ágil y sabio', activo=True)
        
        self.hab1 = Habilidad.objects.create(nombre='Tiro con arco', descripcion='Dispara una flecha', activo=True)
        self.hab2 = Habilidad.objects.create(nombre='Sigilo', descripcion='Te hace invisible', activo=True)
        
        # Opcional: configurar habilidades iniciales
        self.hab1.kit_inicial = True
        self.hab1.save()
        self.hab2.kit_inicial = True
        self.hab2.save()

        self.obj1 = Objeto.objects.create(nombre='Espada Corta', tipo_equipamiento='Arma', es_equipable=True, activo=True, kit_inicial=True)
        self.obj2 = Objeto.objects.create(nombre='Poción Menor', es_equipable=False, activo=True, kit_inicial=True)

    def test_listar_personajes_jugador(self):
        """El jugador solo debería ver sus personajes."""
        # Crear un personaje para player1
        p1 = Personaje.objects.create(nombre='Heroe 1', usuario=self.player1, raza=self.raza)
        # Crear un personaje para player2
        p2 = Personaje.objects.create(nombre='Heroe 2', usuario=self.player2, raza=self.raza)
        
        response = self.client.get(reverse('player:listar_personajes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Heroe 1')
        self.assertNotContains(response, 'Heroe 2')

    def test_limite_creacion_personajes(self):
        """El jugador no puede crear más de 5 personajes."""
        # Creamos 5 personajes primero
        for i in range(5):
            Personaje.objects.create(nombre=f'Soldado {i}', usuario=self.player1, raza=self.raza)
            
        # Intentar crear un sexto personaje
        response = self.client.get(reverse('player:crear_personaje'))
        self.assertEqual(response.status_code, 302) # Redirección
        self.assertRedirects(response, reverse('player:listar_personajes'))

    def test_creacion_personaje_exitoso(self):
        """El jugador puede crear un personaje y se le asigna automáticamente."""
        data = {
            'nombre': 'Aragorn',
            'raza': self.raza.pk,
            'fuerza': 20,
            'destreza': 0,
            'vigor': 0,
            'inteligencia': 0,
            'percepcion': 0,
            'carisma': 0,
            'suerte': 0,
            # Se requieren IDs de objetos y habilidades para el form (aunque sea crear para jugador, puede que requiera el form base)
            'habilidades': [self.hab1.pk, self.hab2.pk],
            'objetos': [self.obj1.pk, self.obj2.pk]
        }
        
        response = self.client.post(reverse('player:crear_personaje'), data)
        self.assertEqual(response.status_code, 302) # Redirige al listado
        
        personaje = Personaje.objects.get(nombre='Aragorn')
        self.assertEqual(personaje.usuario, self.player1) # Asegurar que se asignó a player1

    def test_detalle_personaje_propio(self):
        """Un jugador puede ver su propio personaje."""
        p1 = Personaje.objects.create(nombre='Legolas', usuario=self.player1, raza=self.raza)
        response = self.client.get(reverse('player:detalle_personaje', kwargs={'pk': p1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Legolas')

    def test_detalle_personaje_ajeno_denegado(self):
        """Un jugador no puede ver el personaje de otro."""
        p2 = Personaje.objects.create(nombre='Gimli', usuario=self.player2, raza=self.raza)
        response = self.client.get(reverse('player:detalle_personaje', kwargs={'pk': p2.pk}))
        self.assertEqual(response.status_code, 404) # get_object_or_404 por get_queryset

    def test_renombrar_personaje(self):
        """El jugador puede renombrar su personaje y solo renombrar."""
        p1 = Personaje.objects.create(nombre='Viejo Nombre', usuario=self.player1, raza=self.raza)
        
        # Enviamos un post a la ruta de actualizar (editar)
        response = self.client.post(reverse('player:actualizar_personaje', kwargs={'pk': p1.pk}), {
            'nombre': 'Nuevo Nombre'
        })
        
        self.assertEqual(response.status_code, 302) # Debe redirigir al detalle
        p1.refresh_from_db()
        self.assertEqual(p1.nombre, 'Nuevo Nombre')

    def test_hard_delete_personaje(self):
        """El jugador al eliminar su personaje hace un borrado físico de la BD."""
        p1 = Personaje.objects.create(nombre='Condenado', usuario=self.player1, raza=self.raza)
        
        # Petición DELETE a EliminarPersonaje
        response = self.client.post(reverse('player:eliminar_personaje', kwargs={'pk': p1.pk}))
        
        self.assertEqual(response.status_code, 302)
        # Verificamos que ya NO existe en BD (hard delete)
        self.assertFalse(Personaje.objects.filter(pk=p1.pk).exists())
