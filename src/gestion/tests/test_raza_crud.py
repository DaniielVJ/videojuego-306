from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from src.gestion.models import Raza
from src.gestion.forms.raza import RazaForm

User = get_user_model()

class RazaCRUDTests(TestCase):
    def setUp(self):
        self.gm_user = User.objects.create_user(username='gm_test', password='password123')
        self.gm_user.is_gm = True
        self.gm_user.save()
        self.client = Client()
        self.client.login(username='gm_test', password='password123')

        self.raza = Raza.objects.create(
            nombre='Elfo de Sangre',
            descripcion='Adictos a la magia, pero nobles.',
            activo=True,
            img_body='razas/body/dummy.jpg',
            img_head='razas/head/dummy.jpg'
        )

    def test_form_validation_nombre_largo(self):
        """Verifica la regla de negocio: El nombre de la raza debe tener al menos 3 caracteres."""
        form_data = {
            'nombre': 'El',
            'descripcion': 'Muy corto'
        }
        form = RazaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('El nombre de la raza debe contener al menos 3 caracteres.', form.errors['nombre'])

    def test_form_validation_exito(self):
        """Verifica que un formulario con datos válidos es aceptado."""
        gif = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        dummy_img1 = SimpleUploadedFile(name='test_image1.gif', content=gif, content_type='image/gif')
        dummy_img2 = SimpleUploadedFile(name='test_image2.gif', content=gif, content_type='image/gif')
        form_data = {
            'nombre': 'Tauren',
            'descripcion': 'Seres pacíficos y fuertes.',
            'b_fuerza': 5, 'b_destreza': 0, 'b_vigor': 5,
            'b_inteligencia': 0, 'b_percepcion': 0, 'b_carisma': 0, 'b_suerte': 0,
            'h_fuerza': 0, 'h_destreza': -2, 'h_vigor': 0,
            'h_inteligencia': 0, 'h_percepcion': 0, 'h_carisma': 0, 'h_suerte': 0
        }
        file_data = {
            'img_body': dummy_img1,
            'img_head': dummy_img2
        }
        form = RazaForm(data=form_data, files=file_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_creacion_raza_view(self):
        """Prueba la vista de creación y que se apliquen las reglas."""
        url = reverse('gm:crear-raza')
        gif = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        dummy_img1 = SimpleUploadedFile(name='test_image1.gif', content=gif, content_type='image/gif')
        dummy_img2 = SimpleUploadedFile(name='test_image2.gif', content=gif, content_type='image/gif')
        data = {
            'nombre': 'Trol',
            'descripcion': '¡Por los Lanza Negra!',
            'b_fuerza': 2, 'b_destreza': 5, 'b_vigor': 2,
            'b_inteligencia': 0, 'b_percepcion': 0, 'b_carisma': 0, 'b_suerte': 0,
            'h_fuerza': 0, 'h_destreza': 0, 'h_vigor': 0,
            'h_inteligencia': -2, 'h_percepcion': 0, 'h_carisma': 0, 'h_suerte': 0,
            'img_body': dummy_img1,
            'img_head': dummy_img2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) # Redirecciona tras éxito
        self.assertTrue(Raza.objects.filter(nombre='Trol').exists())

    def test_toggle_estado_raza_view(self):
        """Prueba que el botón de eliminar funciona como un interruptor (toggle) de activo/inactivo."""
        url = reverse('gm:eliminar-raza', kwargs={'pk': self.raza.pk})
        
        # 1. Deshabilitar
        response = self.client.post(url)
        self.raza.refresh_from_db()
        self.assertFalse(self.raza.activo)
        
        # 2. Volver a habilitar
        response = self.client.post(url)
        self.raza.refresh_from_db()
        self.assertTrue(self.raza.activo)

    def test_actualizar_raza_view(self):
        """Verifica que se pueda actualizar la raza de manera segura."""
        url = reverse('gm:actualizar-raza', kwargs={'pk': self.raza.pk})
        gif = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        dummy_img1 = SimpleUploadedFile(name='test_image1.gif', content=gif, content_type='image/gif')
        dummy_img2 = SimpleUploadedFile(name='test_image2.gif', content=gif, content_type='image/gif')
        data = {
            'nombre': 'Sindorei (Elfos)',
            'descripcion': 'Renombrados en honor a los caídos.',
            'b_fuerza': 0, 'b_destreza': 0, 'b_vigor': 0,
            'b_inteligencia': 5, 'b_percepcion': 5, 'b_carisma': 2, 'b_suerte': 0,
            'h_fuerza': -2, 'h_destreza': 0, 'h_vigor': -2,
            'h_inteligencia': 0, 'h_percepcion': 0, 'h_carisma': 0, 'h_suerte': 0,
            'img_body': dummy_img1,
            'img_head': dummy_img2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.raza.refresh_from_db()
        self.assertEqual(self.raza.nombre, 'Sindorei (Elfos)')

    def test_listar_razas_view_shows_all(self):
        """Asegura que el listado de GM devuelve tanto las razas activas como las de legado (inactivas)."""
        Raza.objects.create(nombre='Goblin', descripcion='El tiempo es oro.', activo=False)
        url = reverse('gm:listar-razas')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Elfo de Sangre')
        self.assertContains(response, 'Goblin') # Debe estar presente aunque esté inactiva
