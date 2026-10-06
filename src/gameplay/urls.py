from django.urls import path
from .views import TiendaView, TrabajoView

app_name = 'gameplay'

urlpatterns = [
    path('tienda/<int:personaje_id>/', TiendaView.as_view(), name='tienda'),
    path('trabajar/<int:personaje_id>/', TrabajoView.as_view(), name='trabajar'),
]
