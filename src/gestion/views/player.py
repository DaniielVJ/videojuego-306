from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from src.gestion.models.personaje import Personaje, Raza

# ============================================================
# NOTA: Este archivo está pendiente de refactorización completa.
# Las vistas CrearPersonaje y ActualizarPersonaje dependían del
# archivo legacy formsPersonaje.py que fue eliminado.
# Se conservan ListarPersonajes y EliminarPersonaje que funcionan
# de forma independiente.
# ============================================================


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
