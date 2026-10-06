from django.test import TestCase, Client
from django.contrib.auth import get_user_model
User = get_user_model()
from src.gestion.models import Personaje, Raza, Objeto, InventarioItem

class GameplayTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='pepino', password='password123')
        self.raza = Raza.objects.create(nombre='Humano', descripcion='Un humano común', activo=True)
        self.personaje = Personaje.objects.create(
            nombre='Guerrero',
            usuario=self.user,
            raza=self.raza,
            hp_actual=100,
            mana_actual=50,
            hp_base=100,
            mana_base=50,
            oro=0
        )
        self.client = Client()
        self.client.login(username='pepino', password='password123')
        
        self.espada = Objeto.objects.create(
            nombre='Espada Corta',
            descripcion='Una espada de hierro',
            peso=5.0,
            precio_compra=20,
            precio_venta=10,
            activo=True
        )

    def test_tienda_view_get(self):
        response = self.client.get(f'/gameplay/tienda/{self.personaje.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_tienda_comprar_sin_oro(self):
        response = self.client.post(f'/gameplay/tienda/{self.personaje.pk}/', {
            'accion': 'comprar',
            'objeto_id': self.espada.pk
        })
        self.personaje.refresh_from_db()
        self.assertEqual(self.personaje.oro, 0)
        
    def test_tienda_comprar_con_oro(self):
        self.personaje.oro = 50
        self.personaje.save()
        response = self.client.post(f'/gameplay/tienda/{self.personaje.pk}/', {
            'accion': 'comprar',
            'objeto_id': self.espada.pk
        })
        self.personaje.refresh_from_db()
        self.assertEqual(self.personaje.oro, 30)
        self.assertTrue(InventarioItem.objects.filter(personaje=self.personaje, objeto=self.espada).exists())

    def test_trabajo_view_get(self):
        response = self.client.get(f'/gameplay/trabajar/{self.personaje.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_trabajo_mina(self):
        self.personaje.hp_actual = 50
        self.personaje.save()
        response = self.client.post(f'/gameplay/trabajar/{self.personaje.pk}/', {
            'accion': 'mina'
        })
        self.personaje.refresh_from_db()
        self.assertEqual(self.personaje.hp_actual, 30)
        self.assertTrue(self.personaje.oro >= 15 and self.personaje.oro <= 30)
        
    def test_trabajo_posada(self):
        self.personaje.oro = 20
        self.personaje.hp_actual = 10
        self.personaje.save()
        response = self.client.post(f'/gameplay/trabajar/{self.personaje.pk}/', {
            'accion': 'posada'
        })
        self.personaje.refresh_from_db()
        self.assertEqual(self.personaje.oro, 10)
        self.assertEqual(self.personaje.hp_actual, 60)
