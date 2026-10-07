import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from src.gestion.models import Personaje, Objeto, Raza, Atributo, InventarioItem

User = get_user_model()

class ConsumoObjetosTestCase(TestCase):
    def setUp(self):
        # Crear usuario
        self.user = User.objects.create_user(username='player1', password='password123', is_gm=True)
        
        # Crear raza
        self.raza = Raza.objects.create(nombre='Humano', descripcion='Versátil', activo=True)
        
        # Crear personaje (HP max=100, actual=50 para la prueba)
        self.personaje = Personaje.objects.create(
            usuario=self.user,
            nombre='Arthur',
            raza=self.raza,
            hp_base=100,
            hp_actual=50,
            mana_base=50,
            mana_actual=10,
            activo=True
        )
        Atributo.objects.create(
            personaje=self.personaje,
            fuerza=10, destreza=10, vigor=10,
            inteligencia=10, percepcion=10, carisma=10, suerte=10
        )
        
        # Crear objeto poción (cura 20 hp, no equipable)
        self.pocion_hp = Objeto.objects.create(
            nombre='Poción de Vida Menor',
            descripcion='Cura 20 HP.',
            peso=0.5,
            efectos={'hp_restore': 20},
            es_equipable=False,
            img='objetos/pocion.png'
        )
        
        # Asignar 2 pociones al personaje
        self.inv_item = InventarioItem.objects.create(
            personaje=self.personaje,
            objeto=self.pocion_hp,
            cantidad=2
        )
        
        # Cliente para hacer peticiones
        self.client = Client()
        self.client.login(username='player1', password='password123')
        
        # URL
        self.url = reverse('gm:api-consumir', kwargs={'pk': self.personaje.pk})

    def test_consumir_pocion_con_multiples_cargas(self):
        """Si consumimos una poción y tenemos más de 1, la cantidad debe bajar y curarnos."""
        payload = {'objeto_id': self.pocion_hp.pk, 'personaje_id': self.personaje.pk}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verificar curación
        self.personaje.refresh_from_db()
        self.assertEqual(self.personaje.hp_actual, 70)  # 50 + 20
        self.assertEqual(data['hp_actual'], 70)
        
        # Verificar cantidad restante en la BD y en la respuesta
        self.inv_item.refresh_from_db()
        self.assertEqual(self.inv_item.cantidad, 1)
        self.assertEqual(data['cantidad_restante'], 1)

    def test_consumir_ultima_pocion_elimina_item(self):
        """Si consumimos la última poción, el InventarioItem debe borrarse."""
        self.inv_item.cantidad = 1
        self.inv_item.save()
        
        payload = {'objeto_id': self.pocion_hp.pk, 'personaje_id': self.personaje.pk}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verificar curación
        self.personaje.refresh_from_db()
        self.assertEqual(self.personaje.hp_actual, 70)
        self.assertEqual(data['cantidad_restante'], 0)
        
        # Verificar que el item se eliminó
        existe = InventarioItem.objects.filter(personaje=self.personaje, objeto=self.pocion_hp).exists()
        self.assertFalse(existe)

    def test_no_consumir_si_salud_llena(self):
        """Si la salud está al máximo, no debe permitir gastar la poción."""
        self.personaje.hp_actual = self.personaje.hp_total
        self.personaje.save()
        
        payload = {'objeto_id': self.pocion_hp.pk, 'personaje_id': self.personaje.pk}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        
        # Validar el mensaje de error
        self.assertIn("Ya tienes tu vitalidad/maná al máximo.", data['error'])
        
        # Validar que la cantidad sigue siendo 2
        self.inv_item.refresh_from_db()
        self.assertEqual(self.inv_item.cantidad, 2)
