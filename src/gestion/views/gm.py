from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.db.models import Q
from django.urls import reverse_lazy
from django.db import transaction
from src.gestion.models.personaje import Raza, Habilidad
from src.gestion.models.inventario import Objeto
from src.gestion.forms.formsRaza import RazaUpdateCreateForm
from src.gestion.forms.formsObjeto import ObjetoUpdateCreateForm
from src.gestion.forms.formsHabilidad import HabilidadUpdateCreateForm

class CrearRaza(LoginRequiredMixin, UserPassesTestMixin, CreateView):

	model = Raza
	form_class = RazaUpdateCreateForm
	template_name = "gestion/CreateEdit.html"

	success_url = reverse_lazy("listar_personajes")

	def test_func(self):

		return self.request.user.is_gm

class ActualizarRaza(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

	model = Raza
	form_class = RazaUpdateCreateForm
	template_name = "gestion/CreateEdit.html"

	success_url = reverse_lazy("listar_raza")

	def test_func(self):
		
		return self.request.user.is_gm

class ListarRaza(LoginRequiredMixin, UserPassesTestMixin, ListView):

	model = Raza
	template_name = "gestion/List.html"

	context_object_name = "Lista de Razas"

	def get_queryset(self):

		return Raza.objects.filter(activo = True)

	def get_context_data(self, **kwargs):

		context = super().get_context_data(**kwargs)
		context["url_crear"] = reverse_lazy("gm:crear_raza")
		context["url_editar"] = "gm:actualizar_raza"
		context["url_eliminar"] = "gm:eliminar_raza"
		return context

	def test_func(self):
		
		return self.request.user.is_gm

class EliminarRaza(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

	model = Raza
	template_name = "gestion/Delete.html"
	success_url = reverse_lazy("listar_raza")

	def post(self, *args, **kwargs):

		self.object = self.get_object()

		self.object.activo = False

		self.object.save()

		return HttpResponseRedirect(self.success_url)
		


	def test_func(self):

		return self.request.user.is_gm


class CrearObjeto(LoginRequiredMixin, UserPassesTestMixin, CreateView):

	model = Objeto
	form_class = ObjetoUpdateCreateForm
	template_name = "gestion/CreateEdit.html"

	success_url = reverse_lazy("listar_objeto")

	def test_func(self):

		return self.request.user.is_gm

class ActualizarObjeto(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

	model = Objeto
	form_class = ObjetoUpdateCreateForm
	template_name = "gestion/CreateEdit.html"

	success_url = reverse_lazy("listar_objeto")

	def test_func(self):
		
		return self.request.user.is_gm

class ListarObjeto(LoginRequiredMixin, UserPassesTestMixin, ListView):

	model = Objeto
	template_name = "gestion/List.html"

	context_object_name = "Lista de objetos"

	def get_queryset(self):

		return Objeto.objects.filter(activo = True)

	def get_context_data(self, **kwargs):

		context = super().get_context_data(**kwargs)
		context["url_crear"] = reverse_lazy("gm:crear_objeto")
		context["url_editar"] = "gm:actualizar_objeto"
		context["url_eliminar"] = "gm:eliminar_objeto"
		return context

	def test_func(self):
		
		return self.request.user.is_gm

class EliminarObjeto(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

	model = Objeto
	template_name = "gestion/Delete.html"
	
	success_url = reverse_lazy("listar_objeto")


	def post(self, *args, **kwargs):

		self.object = self.get_object()

		self.object.activo = False

		self.object.save()

		return HttpResponseRedirect(self.success_url)
		

	def test_func(self):

		return self.request.user.is_gm


class CrearHabilidad(LoginRequiredMixin, UserPassesTestMixin, CreateView):

	model = Habilidad
	form_class = HabilidadUpdateCreateForm
	template_name = "gestion/CreateEdit.html"

	success_url = reverse_lazy("listar_habilidad")

	def test_func(self):

		return self.request.user.is_gm

class ActualizarHabilidad(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

	model = Habilidad
	form_class = HabilidadUpdateCreateForm
	template_name = "gestion/CreateEdit.html"

	success_url = "lista_habilidad"	

	def test_func(self):
		
		return self.request.user.is_gm


class ListarHabilidad(LoginRequiredMixin, UserPassesTestMixin, ListView):

	model = Habilidad
	template_name = "gestion/List.html"

	context_object_name = "Lista de habilidades"

	def get_queryset(self):

		return Habilidad.objects.filter(activo = True)

	def get_context_data(self, **kwargs):

		context = super().get_context_data(**kwargs)

		context["url_crear"] = reverse_lazy("gm:crear_habilidad")
		context["url_editar"] = "gm:actualizar_habilidad"
		context["url_eliminar"] = "gm:eliminar_habilidad"
		return context

	def test_func(self):
		
		return self.request.user.is_gm

class EliminarHabilidad(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

	model = Habilidad
	template_name = "gestion/Delete.html"
	success_url = reverse_lazy("lista_habilidad")

	def post(self, *args, **kwargs):

		self.object = self.get_object()

		self.object.activo = False

		self.object.save()

		return HttpResponseRedirect(self.success_url)

	def test_func(self):

		return self.request.user.is_gm