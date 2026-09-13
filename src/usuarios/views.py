from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import View, CreateView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages


from .forms import CreacionUsuarioForm

# Create your views here.
Usuario = get_user_model()


# Regresamos el inicio del juego que explica todo
class InicioJuegoView(TemplateView):
    template_name = 'index.html'


# Aqui programo la logica de si es gm redirija a el inicio GM si no al player.
class RedireccionInicioView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_gm:
            return redirect('index')
        return redirect('index')


# Encargada de registrar un usuario
class RegistroUsuariosView(CreateView):
    model = Usuario
    template_name = 'registration/crear_usuario.html'
    form_class = CreacionUsuarioForm
    success_url = reverse_lazy("usuarios:login")


# View encargada de mostrar el perfil del usuario
class PerfilUsuarioView(LoginRequiredMixin, DetailView):
    pass


# View para cambiar la contraseña del usuario
class CambiarPasswordView(PasswordChangeView):
    template_name = 'usuarios/cambiar_password.html'
    success_url = reverse_lazy('usuarios:inicio_usuario')

    def form_valid(self, form):
        messages.success(self.request, "Tu contraseña ha sido actualizada correctamente.")
        return super().form_valid(form)