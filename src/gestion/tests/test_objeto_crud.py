import io
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from src.gestion.models import Objeto, Personaje, Raza
from src.gestion.forms.objeto import ObjetoUpdateCreateForm

User = get_user_model()

def create_dummy_image():
    file_obj = io.BytesIO()
    image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
    image.save(file_obj, 'png')
    file_obj.name = 'test.png'
    file_obj.seek(0)
    return file_obj

class ObjetoCRUDTests(TestCase):
    def setUp(self):
        self.gm_user = User.objects.create_user(username='gm_test_obj', password='password123')
        self.gm_user.is_gm = True
        self.gm_user.save()
        self.client = Client()
        self.client.login(username='gm_test_obj', password='password123')

        self.img_file = SimpleUploadedFile(name='test_obj.png', content=create_dummy_image().read(), content_type='image/png')
        
        self.objeto = Objeto.objects.create(
            nombre='Espada Larga',
            descripcion='Espada a dos manos.',
            peso=5.50,
            efectos={'v_fuerza': 5},
            activo=True,
            img=self.img_file,
            es_equipable=True,
            kit_inicial=False
        )

    def test_acceso_denegado_no_gm(self):
        normal_user = User.objects.create_user(username='player_obj', password='password123')
        self.client.login(username='player_obj', password='password123')
        url = reverse('gm:crear-objeto')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200, "Un usuario normal no debería ver el formulario de GM")

    def test_form_validation_nombre(self):
        form_data = {
            'nombre': 'Es',
            'descripcion': 'Espada',
            'peso': 2.0
        }
        form = ObjetoUpdateCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('El nombre del objeto debe contener al menos 3 caracteres.', form.errors['nombre'])

    def test_form_validation_img_size(self):
        """Verifica que la imagen no pueda pesar más de 10MB."""
        valid_img_bytes = create_dummy_image().read()
        huge_content = valid_img_bytes + (b'\x00' * (11 * 1024 * 1024))
        huge_img = SimpleUploadedFile(
            name='huge.png',
            content=huge_content, # 11 MB+
            content_type='image/png'
        )
        form_data = {
            'nombre': 'Espada Pesada',
            'descripcion': 'Una espada.',
            'peso': 10.0
        }
        file_data = {'img': huge_img}
        form = ObjetoUpdateCreateForm(data=form_data, files=file_data)
        self.assertFalse(form.is_valid())
        self.assertTrue(any('La imagen no puede pesar más de 10 MB.' in e for e in form.errors.get('img', [])) or any('Envíe una imagen válida' in e for e in form.errors.get('img', [])))

    def test_form_save_efectos(self):
        dummy_img = SimpleUploadedFile(name='dummy.png', content=create_dummy_image().read(), content_type='image/png')
        form_data = {
            'nombre': 'Escudo Divino',
            'descripcion': 'Protege mucho.',
            'peso': 10.0,
            'es_equipable': True,
            'tipo_equipamiento': 'escudo',
            'kit_inicial': False,
            'v_fuerza': 0,
            'v_destreza': 0,
            'v_vigor': 15,
            'v_inteligencia': 0,
            'v_percepcion': 0,
            'v_carisma': 0,
            'v_suerte': 0
        }
        file_data = {'img': dummy_img}
        form = ObjetoUpdateCreateForm(data=form_data, files=file_data)
        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save()
        self.assertEqual(obj.efectos['v_vigor'], 15)

    def test_creacion_objeto_view(self):
        url = reverse('gm:crear-objeto')
        dummy_img = SimpleUploadedFile(name='dummy2.png', content=create_dummy_image().read(), content_type='image/png')
        data = {
            'nombre': 'Anillo Único',
            'descripcion': 'Poder absoluto.',
            'peso': 0.1,
            'img': dummy_img,
            'es_equipable': True,
            'tipo_equipamiento': 'collar',
            'kit_inicial': False,
            'v_fuerza': 1, 'v_destreza': 1, 'v_vigor': 1,
            'v_inteligencia': 1, 'v_percepcion': 1, 'v_carisma': 1, 'v_suerte': 1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Objeto.objects.filter(nombre='Anillo Único').exists())

    def test_actualizar_objeto_view(self):
        url = reverse('gm:actualizar-objeto', kwargs={'pk': self.objeto.pk})
        data = {
            'nombre': 'Espada Larga Legendaria',
            'descripcion': 'Brilla.',
            'peso': 5.50,
            'es_equipable': True,
            'tipo_equipamiento': 'arma',
            'kit_inicial': False,
            'v_fuerza': 20, 'v_destreza': 0, 'v_vigor': 0,
            'v_inteligencia': 0, 'v_percepcion': 0, 'v_carisma': 0, 'v_suerte': 0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.objeto.refresh_from_db()
        self.assertEqual(self.objeto.nombre, 'Espada Larga Legendaria')
        self.assertEqual(self.objeto.efectos['v_fuerza'], 20)

    def test_eliminar_objeto_toggle_y_clear(self):
        raza = Raza.objects.create(nombre="TestRazaObj", descripcion="x", activo=True)
        pj = Personaje.objects.create(usuario=self.gm_user, nombre='GuerreroTest', raza=raza)
        pj.objetos.add(self.objeto)
        self.assertIn(self.objeto, pj.objetos.all())

        url = reverse('gm:eliminar-objeto', kwargs={'pk': self.objeto.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        
        self.objeto.refresh_from_db()
        self.assertFalse(self.objeto.activo)
        
        # Debe desvincularse
        pj.refresh_from_db()
        self.assertNotIn(self.objeto, pj.objetos.all())

        # Volver a habilitar
        response = self.client.post(url)
        self.objeto.refresh_from_db()
        self.assertTrue(self.objeto.activo)
