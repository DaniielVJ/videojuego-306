from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.db.models import Q
from django.urls import reverse_lazy
from django.db import transactions
from src.gestion.models.personaje import Personaje, Raza
from src.gestion.models.inventario import InventarioObjetos
from src.gestion.forms.formsPersonaje import PersonajeEditCreateFrom, AtributosEditCreateForm

class CrearPersonaje(LoginRequiredMixin, CreateView):

	model = Personaje
	form_class = PersonajeEditCreateFrom
	template_name = ""

	success_url = reverse_lazy("")

	def form_valid(self, form):

		with transactions.atomic():

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
	template_name = ""
	context_object_name = "Personaje"

	success_url = reverse_lazy()

	def get_object(self):

		personaje = super().get_object()
		
		if personaje.usuario != self.request.user or personaje.estado not in [Personaje.Estado.MUERTO]:

			pass

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

			with transactions.atomic():

				form_personaje.save()
				form_atributos.save()

				return reverse_lazy()

		return 

class ListarPersonajes(LoginRequiredMixin, ListView):

	model = Personaje
	template_name = ""
	context_object_name = "Personajes"
	paginate_by = 10

	succes_url = reverse_lazy()

	def get_queryset(self):

		if not self.request.user.is_gm

			queryset = Personaje.objects.select_related("raza").filter(activo = True)

		else:

			queryset = Personaje.objects.select_related("raza").filter(activo = True, usuario = self.request.user)
		
		query = self.request.GET.get("q", "").strip()
		raza_id = self.request.GET.get("raza", "").strip()
		estado = self.request.GET.get("estado", "").strip()
		nivel = self.request.GET.get("nivel", "").strip()

		if query:

			if query.isdigit():

				queryset = queryset.filter(Q(id = int(query)) | Q(nombre__icontains = query))

			else:

				queryset = queryset.filter(nombre__icontains = query)

		if raza_id:

			queryset = queryset.filter(raza = raza_id)

		if estado:

			queryset = queryset.filter(estado = estado)

		if nivel:

			queryset = queryset.filter(nivel = nivel)

		return queryset.order_by("-id")

	def get_context_data(self, **kwargs):
		
		context = super().get_context_data(**kwargs)

		context["razas"] = Raza.objects.filter(activo = True)
		context["estado"] = Personaje.Estado.choices

		context["filtros"] = {

			"query": self.request.GET.get("q", "").strip(),
			"raza_id": self.request.GET.get("raza", "").strip(),
			"estado": self.request.GET.get("estado", "").strip(),
			"nivel": self.request.GET.get("nivel", "").strip()


		}

		return context

class EliminarPersonaje(LoginRequiredMixin, DeleteView):

	model = Personaje
	success_url = ""
	context_object_name = "Personaje"

	def get_object(self):

		personaje = super().get_object()

		if personaje.usuario != self.request.user or personaje.estado == Personaje.Estado.MUERTO:

			pass

		return personaje

	def post(self, *args, **kwargs):

		self.object = self.get_object()

		if self.object:

			self.object.activo = False

			self.object.save()

			return

		return




