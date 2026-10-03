from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from src.gestion.models import Habilidad, Personaje, Raza
from src.gestion.forms.habilidad import HabilidadUpdateCreateForm

User = get_user_model()

class HabilidadCRUDTests(TestCase):
    def setUp(self):
        self.gm_user = User.objects.create_user(username='gm_test_hab', password='password123')
        self.gm_user.is_gm = True
        self.gm_user.save()
        self.client = Client()
        self.client.login(username='gm_test_hab', password='password123')

        self.habilidad = Habilidad.objects.create(
            nombre='Bola de Fuego',
            descripcion='Lanza fuego.',
            efectos={'v_inteligencia': 5},
            activo=True
        )

    def test_acceso_denegado_no_gm(self):
        """Verifica que un jugador normal no puede acceder a las vistas del GM."""
        # Creamos y logueamos un usuario normal (no es GM)
        normal_user = User.objects.create_user(username='player', password='password123')
        self.client.login(username='player', password='password123')
        
        # Intentamos acceder a la vista de crear habilidad
        url = reverse('gm:crear-habilidad')
        response = self.client.get(url)
        
        # GmRequiredMixin debería bloquearlo (generalmente redirige al login o a otra vista, o da 403)
        # Si redirige (302) porque no tiene permiso, lo verificamos.
        self.assertNotEqual(response.status_code, 200, "Un usuario normal no debería ver el formulario de GM")

    def test_form_validation_nombre(self):
        """El nombre no puede tener menos de 3 caracteres ni duplicarse."""
        form_data = {
            'nombre': 'Bo',
            'descripcion': 'Fuego'
        }
        form = HabilidadUpdateCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('El nombre de la habilidad debe contener al menos 3 caracteres.', form.errors['nombre'])

        form_data = {
            'nombre': 'Bola de Fuego',
            'descripcion': 'Lanza fuego otra vez.'
        }
        form = HabilidadUpdateCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Ya existe una habilidad con el nombre', form.errors['nombre'][0])

    def test_form_save_efectos(self):
        """Verifica que el formulario empaqueta bien los campos v_ en el JSON efectos."""
        form_data = {
            'nombre': 'Golpe Mortal',
            'descripcion': 'Pega fuerte.',
            'v_fuerza': 10,
            'v_destreza': 2,
            'v_vigor': -1,
            'v_inteligencia': 0,
            'v_percepcion': 0,
            'v_carisma': 0,
            'v_suerte': 5
        }
        form = HabilidadUpdateCreateForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        hab = form.save()
        self.assertEqual(hab.efectos['v_fuerza'], 10)
        self.assertEqual(hab.efectos['v_vigor'], -1)

    def test_creacion_habilidad_view(self):
        """Prueba la creación desde la vista."""
        url = reverse('gm:crear-habilidad')
        data = {
            'nombre': 'Rayo de Hielo',
            'descripcion': 'Congela.',
            'v_fuerza': 0, 'v_destreza': 0, 'v_vigor': 0,
            'v_inteligencia': 8, 'v_percepcion': 0, 'v_carisma': 0, 'v_suerte': 0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Habilidad.objects.filter(nombre='Rayo de Hielo').exists())

    def test_actualizar_habilidad_view(self):
        """Verifica la actualización."""
        url = reverse('gm:actualizar-habilidad', kwargs={'pk': self.habilidad.pk})
        data = {
            'nombre': 'Bola de Fuego Mayor',
            'descripcion': 'Lanza fuego brutal.',
            'v_fuerza': 0, 'v_destreza': 0, 'v_vigor': 0,
            'v_inteligencia': 15, 'v_percepcion': 0, 'v_carisma': 0, 'v_suerte': 0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.habilidad.refresh_from_db()
        self.assertEqual(self.habilidad.nombre, 'Bola de Fuego Mayor')
        self.assertEqual(self.habilidad.efectos['v_inteligencia'], 15)

    def test_eliminar_habilidad_toggle_y_clear(self):
        """Verifica que el Toggle funcione y que se elimine la habilidad de los personajes."""
        # Setup: Crear raza y personaje que posea esta habilidad
        raza = Raza.objects.create(nombre="TestRaza", descripcion="x", activo=True)
        pj = Personaje.objects.create(usuario=self.gm_user, nombre='MagoTest', raza=raza)
        pj.habilidades.add(self.habilidad)
        self.assertIn(self.habilidad, pj.habilidades.all())

        # Deshabilitar
        url = reverse('gm:eliminar-habilidad', kwargs={'pk': self.habilidad.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        
        self.habilidad.refresh_from_db()
        self.assertFalse(self.habilidad.activo)
        
        # Verificar que se desvinculó del personaje!
        pj.refresh_from_db()
        self.assertNotIn(self.habilidad, pj.habilidades.all())

        # Volver a habilitar
        response = self.client.post(url)
        self.habilidad.refresh_from_db()
        self.assertTrue(self.habilidad.activo)
