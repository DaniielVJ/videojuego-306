from django.urls import path
from django.contrib.auth.views import LoginView
from .views import RedireccionInicioView

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    # Defino este path que se encarga a que menu de inicio debe redirigir al usuario
    # dependiendo si es GM o Jugador
    path('inicio/', RedireccionInicioView.as_view(), name='inicio'),
]