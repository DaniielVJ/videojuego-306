import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from src.gestion.models import Atributo, InventarioItem, Objeto, Personaje, Raza


class RegresionesTests(TestCase):
    def setUp(self):
        self.player = get_user_model().objects.create_user(username='revision')
        self.other = get_user_model().objects.create_user(username='otro')
        self.raza = Raza.objects.create(nombre='Humano')
        self.hero = Personaje.objects.create(nombre='Heroe', usuario=self.player, raza=self.raza)
        Atributo.objects.create(personaje=self.hero, fuerza=1, destreza=1, vigor=1,
                               inteligencia=1, percepcion=1, carisma=1, suerte=1)
        self.obj = Objeto.objects.create(nombre='Pocion', efectos={'hp_restore': 10})
        InventarioItem.objects.create(personaje=self.hero, objeto=self.obj)
        self.client.force_login(self.player)

    def test_trabajo_ajeno_devuelve_404(self):
        self.client.force_login(self.other)
        response = self.client.post(reverse('gameplay:trabajar', args=[self.hero.pk]), {'accion': 'mina'})
        self.assertEqual(response.status_code, 404)

    def test_tienda_id_invalido_no_es_500(self):
        response = self.client.post(reverse('gameplay:tienda', args=[self.hero.pk]),
                                    {'accion': 'comprar', 'objeto_id': 'abc'})
        self.assertEqual(response.status_code, 400)

    def test_json_lista_no_es_500(self):
        response = self.client.post(reverse('player:api_consumir', args=[self.hero.pk]),
                                    data='[]', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_jugador_no_renombra_muerto(self):
        self.hero.estado = Personaje.Estado.MUERTO
        self.hero.save()
        response = self.client.post(reverse('player:actualizar_personaje', args=[self.hero.pk]),
                                    {'nombre': 'Renombrado'})
        self.assertEqual(response.status_code, 403)
        self.hero.refresh_from_db()
        self.assertEqual(self.hero.nombre, 'Heroe')

    def test_no_equipar_consumible_con_tipo_residual(self):
        self.obj.tipo_equipamiento = 'arma'
        self.obj.save()
        response = self.client.post(reverse('player:api_equipar', args=[self.hero.pk]),
                                    json.dumps({'objeto_id': self.obj.pk, 'accion': 'equipar'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
