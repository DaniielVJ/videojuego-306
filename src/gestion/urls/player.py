from django.urls import path
from src.gestion.views import player

app_name = "player"

urlpatterns = [

	path("personajes/", player.ListarPersonajes.as_view(), name="listar_personajes"),
	
	path("personajes/crear/", player.CrearPersonaje.as_view(), name="crear_personaje"),
	
	
	path("personajes/<int:pk>/editar/", player.ActualizarPersonaje.as_view(), name="actualizar_personaje"),
	
	path("personajes/<int:pk>/eliminar/", player.EliminarPersonaje.as_view(), name="eliminar_personaje"),
]