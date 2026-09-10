from django.urls import path
from src.gestion.views import gm

app_name = "gm"

urlpatterns = [

	path("razas/crear/", gm.CrearRaza.as_view(), name="crear_raza"),
	path("razas/listar/", gm.ListarRaza.as_view(), name="listar_raza"),
	path("razas/<int:pk>/editar/", gm.ActualizarRaza.as_view(), name="actualizar_raza"),
	path("razas/<int:pk>/eliminar/", gm.EliminarRaza.as_view(), name="eliminar_raza"),

	# Rutas para Objetos
	path("objetos/crear/", gm.CrearObjeto.as_view(), name="crear_objeto"),
	path("objetos/listar/", gm.ListarObjeto.as_view(), name="listar_objeto"),
	path("objetos/<int:pk>/editar/", gm.ActualizarObjeto.as_view(), name="actualizar_objeto"),
	path("objetos/<int:pk>/eliminar/", gm.EliminarObjeto.as_view(), name="eliminar_objeto"),

	# Rutas para Habilidades
	path("habilidades/crear/", gm.CrearHabilidad.as_view(), name="crear_habilidad"),
	path("habilidades/listar/", gm.ListarHabilidad.as_view(), name="listar_habilidad"),
	path("habilidades/<int:pk>/editar/", gm.ActualizarHabilidad.as_view(), name="actualizar_habilidad"),
	path("habilidades/<int:pk>/eliminar/", gm.EliminarHabilidad.as_view(), name="eliminar_habilidad"),
	
]