from django.urls import path
from ..views import ListarPersonajesView, CrearPersonajeView, DetallePersonajeView

app_name = "gm"

urlpatterns = [
    path('personajes/', ListarPersonajesView.as_view(), name='listar-personajes'),
    path('personajes/add/', CrearPersonajeView.as_view(), name='crear-personaje'),
    path('personajes/<int:pk>/detail/', DetallePersonajeView.as_view(), name='detalle-personaje'),
]