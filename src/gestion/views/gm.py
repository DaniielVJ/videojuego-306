from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.db.models import Q
from django.urls import reverse_lazy
from django.db import transactions
from src.gestion.models.personaje import Raza, Habilidad
from src.gestion.models.inventario import Objeto
from src.gestion.forms.formsRaza import RazaUpdateCreateForm
from src.gestion.forms.formsObjeto import ObjetoUpdateCreateForm
from src.gestion.forms.formsHabilidad import HabilidadUpdateCreateForm

class CrearRaza(LoginRequiredMixin, UserPassesTestMixin, CreateView):

	model = Raza
	form_class = RazaUpdateCreateForm
	template_name = ""

	success_url = ""

	def test_func(self):

		return self.request.user.is_gm

class ActualizarRaza(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

	model = Raza
	form_class = RazaUpdateCreateForm
	template_name = ""

	success_url = ""

	def test_func(self):
		
		return self.request.user.is_gm

class EliminarRaza(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

	model = Raza
	succes_url = ""

	def post(self, *args, **kwargs):

		self.object = self.get_object()

		if self.object:

			self.object.activo = False

			self.object.save()

			return
		return

	def test_func(self):

		return self.request.user.is_gm


class CrearObjeto(LoginRequiredMixin, UserPassesTestMixin, CreateView):

	model = Objeto
	form_class = ObjetoUpdateCreateForm
	template_name = ""

	success_url = ""

	def test_func(self):

		return self.request.user.is_gm

class ActualizarObjeto(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

	model = Objeto
	form_class = ObjetoUpdateCreateForm
	template_name = ""

	success_url = ""

	def test_func(self):
		
		return self.request.user.is_gm

class EliminarObjeto(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

	model = Objeto
	succes_url = ""

	def post(self, *args, **kwargs):

		self.object = self.get_object()

		if self.object:

			self.object.activo = False

			self.object.save()

			return
		return

	def test_func(self):

		return self.request.user.is_gm


class CrearHabilidad(LoginRequiredMixin, UserPassesTestMixin, CreateView):

	model = Habilidad
	form_class = HabilidadUpdateCreateForm
	template_name = ""

	success_url = ""

	def test_func(self):

		return self.request.user.is_gm

class ActualizarHabilidad(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

	model = Habilidad
	form_class = HabilidadUpdateCreateForm
	template_name = ""

	success_url = ""

	def test_func(self):
		
		return self.request.user.is_gm

class EliminarHabilidad(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

	model = Habilidad
	succes_url = ""

	def post(self, *args, **kwargs):

		self.object = self.get_object()

		if self.object:

			self.object.activo = False

			self.object.save()

			return
		return

	def test_func(self):

		return self.request.user.is_gm