from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import DeleteView, View
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from src.gestion.models.personaje import Personaje, Raza

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
		
		# Limitar a 5 personajes por jugador
		context['puede_crear'] = self.object_list.count() < 5

		return context


import json
from django.shortcuts import render, redirect
from django.contrib import messages
from src.gestion.forms.personaje import CrearPersonajePlayerForm
from src.gestion.models import Habilidad, Objeto

class CrearPersonaje(LoginRequiredMixin, View):
	template_name = 'gestion/crear_personaje.html'

	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			if Personaje.objects.filter(usuario=request.user, activo=True).count() >= 5:
				messages.error(request, "Has alcanzado el límite máximo de 5 personajes. Debes eliminar uno para poder crear otro.")
				return redirect('player:listar_personajes')
		return super().dispatch(request, *args, **kwargs)

	def get_context_data(self, request, form=None, error_msg=None):
		razas = list(Raza.objects.filter(activo=True))
		habilidades = Habilidad.objects.filter(kit_inicial=True, activo=True)
		objetos = Objeto.objects.filter(kit_inicial=True, activo=True, nivel=1)
		razas_json = [
			{
				'id': r.id,
				'nombre': r.nombre,
				'descripcion': r.descripcion,
				'bonificadores': r.r_bonificadores or {}
			}
			for r in razas
		]
		return {
			'form': form or CrearPersonajePlayerForm(request_user=request.user),
			'razas': razas,
			'habilidades': habilidades,
			'razas_json': json.dumps(razas_json),
			'error_message': error_msg,
			'objetos': objetos,
		}

	def get(self, request):
		return render(request, self.template_name, self.get_context_data(request))

	def post(self, request):
		form = CrearPersonajePlayerForm(request.POST, request_user=request.user)
		if form.is_valid():
			form.save()
			messages.success(request, "¡Tu nuevo héroe ha sido forjado con éxito!")
			return redirect('player:listar_personajes')

		error_msg = None
		if form.errors:
			first_err_list = next(iter(form.errors.values()))
			error_msg = first_err_list[0] if first_err_list else "Por favor verifica los campos del personaje."

		return render(request, self.template_name, self.get_context_data(request, form=form, error_msg=error_msg))



class EliminarPersonaje(LoginRequiredMixin, DeleteView):

	model = Personaje
	template_name = "gestion/eliminar_personaje_player.html"
	context_object_name = "personaje"
	success_url = reverse_lazy("player:listar_personajes")

	def get_object(self):
		personaje = super().get_object()
		if personaje.usuario != self.request.user or personaje.estado == Personaje.Estado.MUERTO:
			raise PermissionDenied("Acceso denegado. No eres dueño de este personaje o está muerto.")
		return personaje

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		nombre = self.object.nombre
		# Hard delete: se borra definitivamente de la base de datos
		self.object.delete()
		messages.success(request, f"El héroe '{nombre}' ha sido borrado definitivamente de las crónicas.")
		return HttpResponseRedirect(self.success_url)

	def post(self, request, *args, **kwargs):
		return self.delete(request, *args, **kwargs)

from django.views.generic import DetailView, UpdateView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json

from src.gestion.forms.personaje import ActualizarPersonajePlayerForm

class ActualizarPersonaje(LoginRequiredMixin, UpdateView):
    model = Personaje
    form_class = ActualizarPersonajePlayerForm
    template_name = "gestion/detalle_personaje.html"
    context_object_name = 'personaje'

    def get_object(self, queryset=None):
        personaje = super().get_object(queryset)
        if personaje.estado != Personaje.Estado.VIVO:
            raise PermissionDenied('Solo puedes modificar personajes vivos.')
        return personaje

    def get_queryset(self):
        return self.model.objects.filter(usuario=self.request.user, activo=True)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['edit_mode'] = True
        return context

    def get_success_url(self):
        messages.success(self.request, "El nombre de tu héroe ha sido actualizado con éxito.")
        return reverse_lazy('player:detalle_personaje', kwargs={'pk': self.object.pk})

class DetallePersonaje(LoginRequiredMixin, DetailView):
	template_name = "gestion/detalle_personaje.html"
	model = Personaje
	context_object_name = 'personaje'

	def get_queryset(self):
		# El jugador solo puede ver sus propios personajes activos
		return self.model.objects.select_related('usuario', 'raza', 'atributos').prefetch_related('habilidades', 'objetos').filter(usuario=self.request.user, activo=True)


	def get(self, request, pk, *args, **kwargs):
		personaje = get_object_or_404(Personaje, pk=pk, usuario=request.user)
		if personaje.esta_muerto():
			messages.error(request, 'No puedes ver los detalles de tu personaje porque esta muerto.')
			return redirect('player:listar_personajes')
		return super().get(request, *args, **kwargs)

class ApiEquiparObjetoPlayerView(LoginRequiredMixin, View):
    def post(self, request, pk):
        from src.gestion.services import usar_objeto
        return usar_objeto(request, pk)


class ApiConsumirObjetoPlayerView(LoginRequiredMixin, View):
    def post(self, request, pk):
        from src.gestion.services import usar_objeto
        return usar_objeto(request, pk, consumir=True)
