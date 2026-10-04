import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from src.gestion.models import Personaje, Objeto, Raza, Atributo, InventarioItem

User = get_user_model()

class EquipamientoObjetosTestCase(TestCase):
    def setUp(self):
        # Crear usuario GM
        self.user = User.objects.create_user(username='gm1', password='password123', is_gm=True)
        
        # Crear raza
        self.raza = Raza.objects.create(nombre='Elfo', descripcion='Ágil', activo=True)
        
        # Crear personaje
        self.personaje = Personaje.objects.create(
            usuario=self.user,
            nombre='Legolas',
            raza=self.raza,
            hp_base=100, hp_actual=100,
            mana_base=50, mana_actual=50,
            activo=True
        )
        Atributo.objects.create(
            personaje=self.personaje,
            fuerza=10, destreza=10, vigor=10,
            inteligencia=10, percepcion=10, carisma=10, suerte=10
        )
        
        # Crear objeto equipable (Arma)
        self.espada = Objeto.objects.create(
            nombre='Espada de Hierro',
            descripcion='Una espada simple.',
            peso=5.0,
            efectos={'fuerza': 5},
            es_equipable=True,
            tipo_equipamiento='arma',
            img='objetos/espada.png'
        )
        
        # Asignar espada al inventario del personaje
        self.inv_item = InventarioItem.objects.create(
            personaje=self.personaje,
            objeto=self.espada,
            cantidad=1
        )
        
        # Cliente para hacer peticiones
        self.client = Client()
        self.client.login(username='gm1', password='password123')
        
        # URL de la vista de equipamiento
        self.url = reverse('gm:api-equipar', kwargs={'pk': self.personaje.pk})

    def test_equipar_objeto_exitosamente(self):
        """Probar que un objeto válido se equipa en el slot correcto."""
        payload = {'objeto_id': self.espada.pk, 'accion': 'equipar'}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.personaje.refresh_from_db()
        self.assertEqual(self.personaje.arma_equipada, self.espada)
        self.assertEqual(data['slot_modificado'], 'arma')
        self.assertIn('mensaje', data)

    def test_desequipar_objeto_exitosamente(self):
        """Probar que un objeto se desequipa correctamente y el slot queda vacío."""
        # Equipar primero manualmente
        self.personaje.arma_equipada = self.espada
        self.personaje.save()
        
        payload = {'objeto_id': self.espada.pk, 'accion': 'desequipar'}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.personaje.refresh_from_db()
        self.assertIsNone(self.personaje.arma_equipada)
        self.assertEqual(data['slot_modificado'], 'arma')

    def test_equipar_objeto_no_en_inventario(self):
        """Probar que no se puede equipar un objeto que no está en el inventario."""
        # Crear otra espada y no asignarla al personaje
        espada_legendaria = Objeto.objects.create(
            nombre='Espada Legendaria',
            descripcion='Demasiado buena.',
            peso=3.0,
            efectos={'fuerza': 50},
            es_equipable=True,
            tipo_equipamiento='arma',
            img='objetos/espada2.png'
        )
        
        payload = {'objeto_id': espada_legendaria.pk, 'accion': 'equipar'}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('error', data)
        self.personaje.refresh_from_db()
        self.assertNotEqual(self.personaje.arma_equipada, espada_legendaria)

    def test_equipar_objeto_no_equipable(self):
        """Probar que un objeto consumible no se puede equipar."""
        pocion = Objeto.objects.create(
            nombre='Poción',
            descripcion='Cura.',
            peso=0.5,
            efectos={'hp_restore': 10},
            es_equipable=False,
            img='objetos/pocion.png'
        )
        InventarioItem.objects.create(personaje=self.personaje, objeto=pocion, cantidad=1)
        
        payload = {'objeto_id': pocion.pk, 'accion': 'equipar'}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("Este objeto no es equipable", data['error'])
