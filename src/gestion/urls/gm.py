from django.urls import path
from ..views import (
    ListarPersonajesView, CrearPersonajeView, DetallePersonajeView, ActualizarPersonajeView, EliminarPersonajeView,
    ApiEquiparObjetoView, ApiConsumirObjetoView,
    ListarRazasView, CrearRazaView, DetalleRazaView, ActualizarRazaView, EliminarRazaView,
    ListarHabilidadesView, CrearHabilidadView, DetalleHabilidadView, ActualizarHabilidadView, EliminarHabilidadView,
    ListarObjetosView, CrearObjetoView, DetalleObjetoView, ActualizarObjetoView, EliminarObjetoView
)

app_name = "gm"

urlpatterns = [
    # CRUD Personajes
    path('personajes/', ListarPersonajesView.as_view(), name='listar-personajes'),
    path('personajes/add/', CrearPersonajeView.as_view(), name='crear-personaje'),
    path('personajes/<int:pk>/detail/', DetallePersonajeView.as_view(), name='detalle-personaje'),
    path('personajes/<int:pk>/update/', ActualizarPersonajeView.as_view(), name='actualizar-personaje'),
    path('personajes/<int:pk>/delete/', EliminarPersonajeView.as_view(), name='eliminar-personaje'),
    path('personajes/<int:pk>/equipar/', ApiEquiparObjetoView.as_view(), name='api-equipar'),
    path('personajes/<int:pk>/consumir/', ApiConsumirObjetoView.as_view(), name='api-consumir'),

    # CRUD Razas
    path('razas/', ListarRazasView.as_view(), name='listar-razas'),
    path('razas/add/', CrearRazaView.as_view(), name='crear-raza'),
    path('razas/<int:pk>/detail/', DetalleRazaView.as_view(), name='detalle-raza'),
    path('razas/<int:pk>/update/', ActualizarRazaView.as_view(), name='actualizar-raza'),
    path('razas/<int:pk>/delete/', EliminarRazaView.as_view(), name='eliminar-raza'),

    # CRUD Habilidades
    path('habilidades/', ListarHabilidadesView.as_view(), name='listar-habilidades'),
    path('habilidades/add/', CrearHabilidadView.as_view(), name='crear-habilidad'),
    path('habilidades/<int:pk>/detail/', DetalleHabilidadView.as_view(), name='detalle-habilidad'),
    path('habilidades/<int:pk>/update/', ActualizarHabilidadView.as_view(), name='actualizar-habilidad'),
    path('habilidades/<int:pk>/delete/', EliminarHabilidadView.as_view(), name='eliminar-habilidad'),

    # CRUD Objetos
    path('objetos/', ListarObjetosView.as_view(), name='listar-objetos'),
    path('objetos/add/', CrearObjetoView.as_view(), name='crear-objeto'),
    path('objetos/<int:pk>/detail/', DetalleObjetoView.as_view(), name='detalle-objeto'),
    path('objetos/<int:pk>/update/', ActualizarObjetoView.as_view(), name='actualizar-objeto'),
    path('objetos/<int:pk>/delete/', EliminarObjetoView.as_view(), name='eliminar-objeto'),
]