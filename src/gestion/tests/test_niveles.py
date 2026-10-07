import json
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from django.test import TestCase, TransactionTestCase, Client
from django.urls import reverse
from src.gestion.forms.objeto import ObjetoUpdateCreateForm
from src.gestion.forms.personaje import CrearPersonajePlayerForm
from src.gestion.models import Atributo, InventarioItem, Objeto, Personaje, Raza


class NivelesTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.player = User.objects.create_user(username='jugador')
        self.other = User.objects.create_user(username='otro')
        self.gm = User.objects.create_user(username='director', is_gm=True)
        self.raza = Raza.objects.create(nombre='Humano')
        self.hero = Personaje.objects.create(nombre='Heroe', usuario=self.player, raza=self.raza)
        Atributo.objects.create(personaje=self.hero, **{k: 1 for k in
            ('fuerza', 'destreza', 'vigor', 'inteligencia', 'percepcion', 'carisma', 'suerte')})
        self.weapon = Objeto.objects.create(nombre='Espada avanzada', nivel=2,
            es_equipable=True, tipo_equipamiento='arma', efectos={'fuerza': 4})
        self.potion = Objeto.objects.create(nombre='Pocion avanzada', nivel=2, efectos={'hp_restore': 20})
        for obj in (self.weapon, self.potion):
            InventarioItem.objects.create(personaje=self.hero, objeto=obj, cantidad=2)
        self.client.force_login(self.player)

    def api(self, obj, accion='equipar', gm=False, data=None):
        route = ('gm:api-consumir' if gm else 'player:api_consumir') if accion == 'consumir' else (
            'gm:api-equipar' if gm else 'player:api_equipar')
        return self.client.post(reverse(route, args=[self.hero.pk]),
            json.dumps(data if data is not None else {'objeto_id': obj.pk, 'accion': accion}),
            content_type='application/json')

    def test_fronteras_y_excedentes_xp(self):
        for xp, level, residual, threshold in [(0, 1, 0, 100), (99, 1, 99, 100),
                (100, 2, 0, 200), (299, 2, 199, 200), (300, 3, 0, 300), (350, 3, 50, 300)]:
            with self.subTest(xp=xp):
                self.hero.nivel, self.hero.experiencia = 1, 0
                self.hero.ganar_experiencia(xp)
                self.hero.save()
                self.hero.refresh_from_db()
                self.assertEqual((self.hero.nivel, self.hero.experiencia, self.hero.exp_siguiente_nivel),
                                 (level, residual, threshold))

    def test_progreso_se_conserva_en_varias_recompensas(self):
        self.assertEqual(self.hero.ganar_experiencia(80), 0)
        self.assertEqual(self.hero.ganar_experiencia(270), 2)
        self.assertEqual((self.hero.nivel, self.hero.experiencia), (3, 50))

    def test_guardado_parcial_no_pierde_subida(self):
        self.hero.experiencia = 350
        self.hero.save(update_fields=['experiencia'])
        self.hero.refresh_from_db()
        self.assertEqual((self.hero.nivel, self.hero.experiencia, self.hero.exp_siguiente_nivel), (3, 50, 300))

    def test_xp_invalida_no_cambia_personaje(self):
        for xp in (-1, True, 1.5, '100'):
            with self.subTest(xp=xp), self.assertRaises(ValidationError):
                self.hero.ganar_experiencia(xp)
        self.assertEqual(self.hero.experiencia, 0)

    def test_nivel_cero_invalido_y_restringido_en_bd(self):
        self.hero.nivel = 0
        with self.assertRaises(ValidationError):
            self.hero.save()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Personaje.objects.filter(pk=self.hero.pk).update(nivel=0)

    def test_objeto_nivel_cero_invalido_y_restringido_en_bd(self):
        self.weapon.nivel = 0
        with self.assertRaises(ValidationError):
            self.weapon.full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Objeto.objects.filter(pk=self.weapon.pk).update(nivel=0)

    def test_nivel_insuficiente_equipar_y_consumir_player_y_gm(self):
        for user, gm in [(self.player, False), (self.gm, True)]:
            self.client.force_login(user)
            for obj, action in [(self.weapon, 'equipar'), (self.potion, 'consumir')]:
                with self.subTest(gm=gm, action=action):
                    self.assertEqual(self.api(obj, action, gm=gm).status_code, 403)
                    self.assertEqual(InventarioItem.objects.get(personaje=self.hero, objeto=obj).cantidad, 2)
        self.hero.refresh_from_db()
        self.assertIsNone(self.hero.arma_equipada)
        self.assertEqual(self.hero.hp_actual, 100)

    def test_subir_desbloquea_equipo_y_consumibles(self):
        self.hero.ganar_experiencia(100)
        self.hero.hp_actual = 50
        self.hero.save()
        self.assertEqual(self.api(self.weapon).status_code, 200)
        self.assertEqual(self.api(self.potion, 'consumir').status_code, 200)
        self.hero.refresh_from_db()
        self.assertEqual(self.hero.stats_totales['fuerza'], 5)
        self.assertEqual(self.hero.hp_actual, 70)

    def test_consumible_mixto_actualiza_stats_y_maximo_en_respuesta(self):
        self.hero.nivel = 2
        self.hero.hp_actual = 50
        self.hero.save()
        self.potion.efectos = {'hp_restore': 20, 'vigor': 2}
        self.potion.save()
        response = self.api(self.potion, 'consumir')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['stats_totales']['vigor'], 3)
        self.assertEqual(response.json()['hp_total'], 130)
        self.hero.refresh_from_db()
        self.assertEqual(self.hero.atributos.vigor, 3)

    def test_ajuste_gm_reduce_nivel_y_desequipa(self):
        self.hero.nivel = 2
        self.hero.arma_equipada = self.weapon
        self.hero.save()
        self.hero.nivel = 1
        self.hero.save(update_fields=['nivel'])
        self.hero.refresh_from_db()
        self.assertIsNone(self.hero.arma_equipada)

    def test_formulario_gm_normaliza_xp_e_ignora_umbral_enviado(self):
        data = {'nombre': self.hero.nombre, 'raza': self.raza.pk, 'usuario': self.player.pk,
                'estado': 'vivo', 'activo': True, 'nivel': 2, 'experiencia': 250, 'exp_siguiente_nivel': 1,
                **{k: 1 for k in ('fuerza', 'destreza', 'vigor', 'inteligencia', 'percepcion', 'carisma', 'suerte')}}
        self.client.force_login(self.gm)
        response = self.client.post(reverse('gm:actualizar-personaje', args=[self.hero.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.hero.refresh_from_db()
        self.assertEqual((self.hero.nivel, self.hero.experiencia, self.hero.exp_siguiente_nivel), (3, 50, 300))

    def test_editar_gm_conserva_copias_sin_cantidad_enviada(self):
        self.client.force_login(self.gm)
        data = {'nombre': self.hero.nombre, 'raza': self.raza.pk, 'usuario': self.player.pk,
                'estado': 'vivo', 'activo': True, 'nivel': 2, 'experiencia': 0, 'objetos': [self.weapon.pk],
                **{k: 1 for k in ('fuerza', 'destreza', 'vigor', 'inteligencia', 'percepcion', 'carisma', 'suerte')}}
        response = self.client.post(reverse('gm:actualizar-personaje', args=[self.hero.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InventarioItem.objects.get(personaje=self.hero, objeto=self.weapon).cantidad, 2)
        for cantidad in ['abc', '-1', '0', '9' * 40]:
            data[f'cantidad_{self.weapon.pk}'] = cantidad
            self.assertEqual(self.client.post(reverse('gm:actualizar-personaje', args=[self.hero.pk]), data).status_code, 200)
            self.assertEqual(InventarioItem.objects.get(personaje=self.hero, objeto=self.weapon).cantidad, 2)
        data.pop(f'cantidad_{self.weapon.pk}')
        data['fuerza'] = '9' * 40
        self.assertEqual(self.client.post(reverse('gm:actualizar-personaje', args=[self.hero.pk]), data).status_code, 200)
        self.hero.atributos.refresh_from_db()
        self.assertEqual(self.hero.atributos.fuerza, 1)

    def test_jugador_no_inventa_nivel_xp_ni_propietario(self):
        response = self.client.post(reverse('player:actualizar_personaje', args=[self.hero.pk]),
            {'nombre': 'Nuevo heroe', 'nivel': 999, 'experiencia': 9999, 'usuario': self.other.pk})
        self.assertEqual(response.status_code, 302)
        self.hero.refresh_from_db()
        self.assertEqual((self.hero.nivel, self.hero.experiencia, self.hero.usuario_id), (1, 0, self.player.pk))

    def test_form_objeto_rechaza_nivel_invalido_y_kit_avanzado(self):
        for nivel, kit in [(0, False), (-1, False), (2, True)]:
            with self.subTest(nivel=nivel, kit=kit):
                form = ObjetoUpdateCreateForm(instance=self.weapon, data={'nombre': self.weapon.nombre,
                    'descripcion': 'Objeto de prueba', 'peso': 1, 'nivel': nivel, 'kit_inicial': kit})
                self.assertFalse(form.is_valid())
                self.assertIn('nivel', form.errors)

    def test_kit_inicial_excluye_objetos_avanzados(self):
        self.weapon.kit_inicial = True
        self.weapon.save()
        form = CrearPersonajePlayerForm(request_user=self.player)
        self.assertNotIn(self.weapon, form.fields['objetos'].queryset)
        response = self.client.get(reverse('player:crear_personaje'))
        self.assertNotContains(response, self.weapon.nombre)

    def test_editar_requisito_objeto_desequipa_personajes_insuficientes(self):
        self.hero.nivel = 2
        self.hero.arma_equipada = self.weapon
        self.hero.save()
        form = ObjetoUpdateCreateForm(instance=self.weapon, data={'nombre': self.weapon.nombre,
            'descripcion': 'Objeto de prueba', 'peso': 1, 'nivel': 3, 'es_equipable': True,
            'tipo_equipamiento': 'arma'}, files={})
        # Usar una imagen existente sintética sin subir archivos.
        self.weapon.img = 'prueba.png'
        form = ObjetoUpdateCreateForm(instance=self.weapon, data=form.data)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.hero.refresh_from_db()
        self.assertIsNone(self.hero.arma_equipada)

    def test_inventario_cero_no_otorga_uso(self):
        self.weapon.nivel = 1
        self.weapon.save()
        InventarioItem.objects.filter(personaje=self.hero, objeto=self.weapon).update(cantidad=0)
        self.assertEqual(self.api(self.weapon).status_code, 403)

    def test_objeto_desactivado_no_se_usa(self):
        self.hero.nivel = 2
        self.hero.save()
        for obj, action in [(self.weapon, 'equipar'), (self.potion, 'consumir')]:
            obj.activo = False
            obj.save()
            self.assertEqual(self.api(obj, action).status_code, 403)

    def test_desequipar_id_distinto_no_quita_equipo(self):
        self.hero.nivel = 2
        self.hero.arma_equipada = self.weapon
        self.hero.save()
        otro = Objeto.objects.create(nombre='Otra espada', es_equipable=True, tipo_equipamiento='arma')
        InventarioItem.objects.create(personaje=self.hero, objeto=otro)
        self.assertEqual(self.api(otro, 'desequipar').status_code, 400)
        self.hero.refresh_from_db()
        self.assertEqual(self.hero.arma_equipada, self.weapon)

    def test_json_e_ids_invalidos_en_ambas_apis(self):
        for gm, user in [(False, self.player), (True, self.gm)]:
            self.client.force_login(user)
            for value in [None, [], {}, True, -1, 0, 1.2, 'abc', '9' * 40]:
                for action in ['equipar', 'consumir']:
                    with self.subTest(gm=gm, value=value, action=action):
                        self.assertEqual(self.api(self.weapon, action, gm=gm,
                            data={'objeto_id': value, 'accion': action}).status_code, 400)

    def test_efectos_invalidos_no_consumen_ni_modifican(self):
        self.hero.nivel = 2
        self.hero.save()
        for effects in [{'fuerza': 2, 'hp_restore': 'mucho'}, {'usuario': 1}, [], {}, {'fuerza': -1}]:
            self.potion.efectos = effects
            self.potion.save()
            self.assertEqual(self.api(self.potion, 'consumir').status_code, 400)
            self.assertEqual(InventarioItem.objects.get(personaje=self.hero, objeto=self.potion).cantidad, 2)
            self.hero.atributos.refresh_from_db()
            self.assertEqual(self.hero.atributos.fuerza, 1)

    def test_muerto_y_congelado_no_usan_trabajos_tienda_ni_objetos(self):
        for state in ('muerto', 'congelado'):
            self.hero.estado = state
            self.hero.save()
            for route, data in [('gameplay:trabajar', {'accion': 'mina'}),
                                ('gameplay:tienda', {'accion': 'comprar', 'objeto_id': self.weapon.pk})]:
                self.assertEqual(self.client.post(reverse(route, args=[self.hero.pk]), data).status_code, 403)
            self.assertEqual(self.api(self.weapon).status_code, 403)
            self.assertEqual(self.api(self.potion, 'consumir').status_code, 403)
        self.hero.refresh_from_db()
        self.assertEqual((self.hero.experiencia, self.hero.oro, self.hero.hp_actual), (0, 0, 100))

    def test_ajeno_o_inactivo_no_accede_gameplay_ni_apis(self):
        for ajeno in (True, False):
            self.client.force_login(self.other if ajeno else self.player)
            if not ajeno:
                self.hero.activo = False
                self.hero.save()
            for route in ('gameplay:tienda', 'gameplay:trabajar'):
                self.assertEqual(self.client.get(reverse(route, args=[self.hero.pk])).status_code, 404)
                self.assertEqual(self.client.post(reverse(route, args=[self.hero.pk]), {'accion': 'mina'}).status_code, 404)
            self.assertEqual(self.api(self.weapon).status_code, 404)
            self.assertEqual(self.api(self.potion, 'consumir').status_code, 404)

    def test_jugador_no_accede_mutaciones_gm(self):
        for route in ('gm:actualizar-personaje', 'gm:api-equipar', 'gm:api-consumir'):
            self.assertEqual(self.client.post(reverse(route, args=[self.hero.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('gm:crear-objeto')).status_code, 403)

    def test_anonimo_redirigido_y_csrf_requerido(self):
        self.client.logout()
        self.assertEqual(self.api(self.weapon).status_code, 302)
        secure = Client(enforce_csrf_checks=True)
        secure.force_login(self.player)
        self.assertEqual(secure.post(reverse('player:api_equipar', args=[self.hero.pk]),
            json.dumps({'objeto_id': self.weapon.pk, 'accion': 'equipar'}), content_type='application/json').status_code, 403)

    @patch('src.gameplay.views.random.randint', side_effect=[10, 25])
    def test_biblioteca_sube_nivel_con_recompensa_servidor(self, random_mock):
        self.hero.experiencia = 90
        self.hero.save()
        response = self.client.post(reverse('gameplay:trabajar', args=[self.hero.pk]),
            {'accion': 'biblioteca', 'xp': 99999, 'nivel': 999}, follow=True)
        self.assertContains(response, 'Has subido al nivel 2')
        self.hero.refresh_from_db()
        self.assertEqual((self.hero.nivel, self.hero.experiencia, self.hero.mana_actual, self.hero.oro), (2, 15, 30, 10))

    def test_trabajo_insuficiente_no_da_recompensa(self):
        self.hero.hp_actual, self.hero.mana_actual = 19, 19
        self.hero.save()
        for action in ('mina', 'biblioteca'):
            self.client.post(reverse('gameplay:trabajar', args=[self.hero.pk]), {'accion': action})
        self.hero.refresh_from_db()
        self.assertEqual((self.hero.oro, self.hero.experiencia, self.hero.hp_actual, self.hero.mana_actual), (0, 0, 19, 19))

    def test_acciones_inventadas_rechazadas(self):
        self.assertEqual(self.api(self.weapon, 'inventar').status_code, 400)
        for route in ('gameplay:trabajar', 'gameplay:tienda'):
            self.assertEqual(self.client.post(reverse(route, args=[self.hero.pk]), {'accion': 'inventar'}).status_code, 400)

    def test_comprar_avanzado_permitido_sin_usarlo(self):
        self.hero.oro = 100
        self.hero.save()
        response = self.client.post(reverse('gameplay:tienda', args=[self.hero.pk]),
            {'accion': 'comprar', 'objeto_id': self.weapon.pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InventarioItem.objects.get(personaje=self.hero, objeto=self.weapon).cantidad, 3)
        self.assertEqual(self.api(self.weapon).status_code, 403)

    def test_vender_ultima_copia_desequipa(self):
        self.hero.nivel = 2
        self.hero.arma_equipada = self.weapon
        self.hero.save()
        InventarioItem.objects.filter(personaje=self.hero, objeto=self.weapon).update(cantidad=1)
        response = self.client.post(reverse('gameplay:tienda', args=[self.hero.pk]),
            {'accion': 'vender', 'objeto_id': self.weapon.pk})
        self.assertEqual(response.status_code, 302)
        self.hero.refresh_from_db()
        self.assertIsNone(self.hero.arma_equipada)
        self.assertFalse(InventarioItem.objects.filter(personaje=self.hero, objeto=self.weapon).exists())
        self.assertEqual(self.hero.oro, self.weapon.precio_venta)

    def test_ui_muestra_nivel_y_bloqueo(self):
        response = self.client.get(reverse('player:detalle_personaje', args=[self.hero.pk]))
        self.assertContains(response, 'REQUIERE NIVEL 2')
        self.assertContains(response, 'Nivel mínimo: 2')
        self.assertContains(self.client.get(reverse('gameplay:tienda', args=[self.hero.pk])), 'aún no usarlo')
        self.client.force_login(self.gm)
        self.assertContains(self.client.get(reverse('gm:crear-objeto')), 'Nivel mínimo para equipar o consumir')


class MigracionNivelesTests(TransactionTestCase):
    def test_normaliza_datos_anteriores_y_objetos_en_nivel_uno(self):
        executor = MigrationExecutor(connection)
        previous = [('gestion', '0001_initial')]
        latest = [('gestion', '0002_objeto_nivel_alter_personaje_nivel_and_more')]
        try:
            executor.migrate(previous)
            apps = executor.loader.project_state(previous).apps
            User = apps.get_model('usuarios', 'Usuario')
            user = User.objects.create(username='migracion')
            raza = apps.get_model('gestion', 'Raza').objects.create(nombre='Raza migracion')
            personaje = apps.get_model('gestion', 'Personaje').objects.create(
                usuario=user, raza=raza, nombre='Anterior', nivel=0, experiencia=350, exp_siguiente_nivel=1)
            objeto = apps.get_model('gestion', 'Objeto').objects.create(nombre='Anterior')
            executor = MigrationExecutor(connection)
            executor.migrate(latest)
            hero = Personaje.objects.get(pk=personaje.pk)
            self.assertEqual((hero.nivel, hero.experiencia, hero.exp_siguiente_nivel), (3, 50, 300))
            self.assertEqual(Objeto.objects.get(pk=objeto.pk).nivel, 1)
        finally:
            MigrationExecutor(connection).migrate(latest)
