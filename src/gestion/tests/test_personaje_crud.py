from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from src.gestion.models import Personaje, Raza, Habilidad, Objeto

User = get_user_model()

class PersonajeCRUDTests(TestCase):
    def setUp(self):
        # 1. Crear un usuario GM para pasar el GmRequiredMixin
        self.gm_user = User.objects.create_user(username='gm_test', password='password123')
        self.gm_user.is_gm = True
        self.gm_user.save()

        # 2. Crear una raza requerida por la relacion FK del personaje
        self.raza = Raza.objects.create(
            nombre='Orco',
            descripcion='Guerrero temible de Durotar',
            activo=True
        )

        # 3. Crear habilidades y objetos minimos para pasar las validaciones del form (2 de cada uno)
        self.hab1 = Habilidad.objects.create(nombre='Hab1', descripcion='d', activo=True)
        self.hab2 = Habilidad.objects.create(nombre='Hab2', descripcion='d', activo=True)
        
        self.obj1 = Objeto.objects.create(nombre='Obj1', descripcion='d', peso=1.0, activo=True, kit_inicial=True)
        self.obj2 = Objeto.objects.create(nombre='Obj2', descripcion='d', peso=1.0, activo=True, kit_inicial=True)

        # 4. Crear el personaje a testear
        self.personaje = Personaje.objects.create(
            usuario=self.gm_user,
            nombre='Thrall',
            raza=self.raza,
            estado=Personaje.Estado.VIVO,
            nivel=10,
            activo=True
        )
        self.personaje.habilidades.add(self.hab1, self.hab2)
        self.personaje.objetos.add(self.obj1, self.obj2)
        
        self.client = Client()

    def test_creacion_personaje_modelo(self):
        """Verifica que el modelo Personaje se crea e inserta bien en base de datos."""
        self.assertEqual(Personaje.objects.count(), 1)
        pj = Personaje.objects.first()
        self.assertEqual(pj.nombre, 'Thrall')
        self.assertTrue(pj.activo)

    def test_soft_delete_gm_view(self):
        """Verifica que la vista de eliminar del GM cambie el estado activo a False (Soft Delete)."""
        self.client.login(username='gm_test', password='password123')
        url = reverse('gm:eliminar-personaje', kwargs={'pk': self.personaje.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.personaje.refresh_from_db()
        self.assertEqual(Personaje.objects.count(), 1)
        self.assertFalse(self.personaje.activo)
        
        # Probar volver a habilitar (Toggle)
        response_habilitar = self.client.post(url)
        self.assertEqual(response_habilitar.status_code, 302)
        self.personaje.refresh_from_db()
        self.assertTrue(self.personaje.activo)

    def test_full_crud_gm(self):
        """Prueba el ciclo completo de Lectura, Creación, Modificación y Detalles por parte del GM."""
        self.client.login(username='gm_test', password='password123')
        
        # 1. READ (Listar)
        response_list = self.client.get(reverse('gm:listar-personajes'))
        self.assertEqual(response_list.status_code, 200)
        self.assertContains(response_list, 'Thrall') # Thrall debe aparecer en la lista
        
        # 2. READ (Detalle)
        response_detail = self.client.get(reverse('gm:detalle-personaje', kwargs={'pk': self.personaje.pk}))
        self.assertEqual(response_detail.status_code, 200)
        self.assertContains(response_detail, 'Thrall')
        
        # 3. UPDATE (Actualizar)
        update_url = reverse('gm:actualizar-personaje', kwargs={'pk': self.personaje.pk})
        # Actualizamos el nombre y el nivel
        update_data = {
            'usuario': self.gm_user.id,
            'nombre': 'Thrall el Jefe',
            'raza': self.raza.id,
            'estado': Personaje.Estado.VIVO,
            'nivel': 12,
            'experiencia': 0,
            'exp_siguiente_nivel': 100,
            'habilidades': [self.hab1.id, self.hab2.id],
            'objetos': [self.obj1.id, self.obj2.id],
            'fuerza': 5, 'destreza': 3, 'vigor': 3, 'inteligencia': 3,
            'percepcion': 2, 'carisma': 2, 'suerte': 2
        }
        response_update = self.client.post(update_url, data=update_data)
        self.assertEqual(response_update.status_code, 302) # Redirige al exito
        self.personaje.refresh_from_db()
        self.assertEqual(self.personaje.nombre, 'Thrall el Jefe')
        self.assertEqual(self.personaje.nivel, 12)
        
        # 4. CREATE (Crear Nuevo)
        create_url = reverse('gm:crear-personaje')
        create_data = {
            'usuario': self.gm_user.id,
            'nombre': 'Garrosh',
            'raza': self.raza.id,
            'estado': Personaje.Estado.VIVO,
            'nivel': 1,
            'experiencia': 0,
            'exp_siguiente_nivel': 100,
            'habilidades': [self.hab1.id, self.hab2.id],
            'objetos': [self.obj1.id, self.obj2.id],
            'fuerza': 5, 'destreza': 3, 'vigor': 3, 'inteligencia': 3,
            'percepcion': 2, 'carisma': 2, 'suerte': 2
        }
        response_create = self.client.post(create_url, data=create_data)
        self.assertEqual(response_create.status_code, 302) # Redirige al listado
        self.assertEqual(Personaje.objects.count(), 2)
        self.assertTrue(Personaje.objects.filter(nombre='Garrosh').exists())
