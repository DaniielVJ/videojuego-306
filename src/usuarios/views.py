from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from .forms import CreacionUsuarioForm

# Create your views here.
Usuario = get_user_model()


# Aqui programo la logica de si es gm redirija a el inicio GM si no al player.
class RedireccionInicioView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_gm:
            return redirect()
        return redirect()


# Encargada de registrar un usuario
class RegistroUsuariosView(CreateView):
    model = Usuario
    template_name = 'registration/crear_usuario.html'
    form_class = CreacionUsuarioForm
    success_url = reverse_lazy("usuarios:login")
