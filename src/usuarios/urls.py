from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views


app_name = "usuarios"

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    # Defino este path que se encarga a que menu de inicio debe redirigir al usuario
    # dependiendo si es GM o Jugador
    path('inicio/', views.RedireccionInicioView.as_view(), name='inicio'),
    path('register/', views.RegistroUsuariosView.as_view(), name='registro')
]