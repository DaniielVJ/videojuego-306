from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.db.models import Q
from django.urls import reverse_lazy
from django.db import transaction
from src.gestion.models.personaje import Personaje, Raza
from src.gestion.forms.formsPersonaje import PersonajeEditCreateFrom, AtributosEditCreateForm

class CrearPersonaje(LoginRequiredMixin, CreateView):

	model = Personaje
	form_class = PersonajeEditCreateFrom
	template_name = "gestion/CreateEdit.html"

	success_url = reverse_lazy("listar_personaje")

	def form_valid(self, form):

		with transaction.atomic():

			form.instance.usuario = self.request.user

			self.object = form.save()

			activas = form.cleaned_data.get("poderes")

			if activas:

				self.object.habilidades.add(*activas)

			objeto = form.cleaned_data.get("objetos")

			if objeto:

				InventarioObjetos.objects.create(

					personaje = self.object,
					objeto = objeto

				)

		return super().form_valid(form)

class ActualizarPersonaje(LoginRequiredMixin, UpdateView):

	model = Personaje
	form_class = PersonajeEditCreateFrom
	template_name = "gestion/CreateEdit.html"
	context_object_name = "Personaje"

	success_url = reverse_lazy("listar_personaje")

	def get_object(self):

		personaje = super().get_object()
		
		if personaje.usuario != self.request.user or personaje.estado not in [Personaje.Estado.MUERTO]:

			raise PermissionDenied("Acceso denegado")

		return personaje

	def get_form_kwargs(self):
		
		kwargs = super().get_form_kwargs()

		kwargs["user"] = self.request.user

		return kwargs

	def get_context_data(self, **kwargs):
		
		context = super().get_context_data(**kwargs)

		form_atributos = AtributosEditCreateForm(instance = self.object.atributos)

		context["form_atributos"] = form_atributos

		return context

	def post(self, request, *args, **kwargs):
		
		self.object = self.get_object()

		form_personaje = self.get_form()

		form_atributos = AtributosEditCreateForm(self.request.POST, instance = self.object.atributos)

		if form_personaje.is_valid() and form_atributos.is_valid():

			with transaction.atomic():

				form_personaje.save()
				form_atributos.save()

				return HttpResponseRedirect(self.success_url)

		return self.render_to_response(self.get_context_data(form=form_personaje, form_atributos=form_atributos))

class ListarPersonajes(LoginRequiredMixin, ListView):

	model = Personaje
	template_name = "gestion/listar_personajes_player.html"
	context_object_name = "personajes"
	
	# Ya no necesitamos paginación porque el límite es 5
	# paginate_by = 10 

	def get_queryset(self):
		# El jugador solo ve sus propios personajes activos
		# Eliminamos los filtros de búsqueda GET porque la lista es pequeña (máx 5)
		return Personaje.objects.select_related("raza").filter(
			activo=True, 
			usuario=self.request.user
		).order_by("nombre")

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		# Estadísticas rápidas para la vista (Vivos, Muertos, Congelados)
		context['vivos'] = self.object_list.filter(estado=Personaje.Estado.VIVO).count() 
		context['muertos'] = self.object_list.filter(estado=Personaje.Estado.MUERTO).count()
		context['congelados'] = self.object_list.filter(estado=Personaje.Estado.CONGELADO).count()

		return context

class EliminarPersonaje(LoginRequiredMixin, DeleteView):

	model = Personaje
	template_name = "gestion/Delete.html"
	context_object_name = "Personaje"

	success_url = reverse_lazy("listar_personaje")

	def get_object(self):

		personaje = super().get_object()

		if personaje.usuario != self.request.user or personaje.estado == Personaje.Estado.MUERTO:

			raise PermissionDenied("Acceso denegado")

		return personaje

	def post(self, *args, **kwargs):

		self.object = self.get_object()

		self.object.activo = False

		self.object.save()

		return HttpResponseRedirect(self.success_url)




