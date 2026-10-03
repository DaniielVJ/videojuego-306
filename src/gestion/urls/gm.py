from django.urls import path
from ..views import (
    ListarPersonajesView, CrearPersonajeView, DetallePersonajeView, ActualizarPersonajeView, EliminarPersonajeView,
    ListarRazasView, CrearRazaView, DetalleRazaView, ActualizarRazaView, EliminarRazaView
)

app_name = "gm"

urlpatterns = [
    # CRUD Personajes
    path('personajes/', ListarPersonajesView.as_view(), name='listar-personajes'),
    path('personajes/add/', CrearPersonajeView.as_view(), name='crear-personaje'),
    path('personajes/<int:pk>/detail/', DetallePersonajeView.as_view(), name='detalle-personaje'),
    path('personajes/<int:pk>/update/', ActualizarPersonajeView.as_view(), name='actualizar-personaje'),
    path('personajes/<int:pk>/delete/', EliminarPersonajeView.as_view(), name='eliminar-personaje'),

    # CRUD Razas
    path('razas/', ListarRazasView.as_view(), name='listar-razas'),
    path('razas/add/', CrearRazaView.as_view(), name='crear-raza'),
    path('razas/<int:pk>/detail/', DetalleRazaView.as_view(), name='detalle-raza'),
    path('razas/<int:pk>/update/', ActualizarRazaView.as_view(), name='actualizar-raza'),
    path('razas/<int:pk>/delete/', EliminarRazaView.as_view(), name='eliminar-raza'),
]