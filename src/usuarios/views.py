from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import View, CreateView, TemplateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
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
            return redirect('gm:listar-personajes')
        return redirect('player:listar_personajes')


# Encargada de registrar un usuario
class RegistroUsuariosView(CreateView):
    model = Usuario
    template_name = 'registration/crear_usuario.html'
    form_class = CreacionUsuarioForm
    success_url = reverse_lazy("usuarios:login")


class PerfilUsuarioView(LoginRequiredMixin, DetailView):
    model = Usuario
    template_name = 'usuarios/mi_perfil.html'
    context_object_name = 'perfil_user'
    
    def get_object(self):
        return self.request.user

class ActualizarPerfilView(LoginRequiredMixin, UpdateView):
    model = Usuario
    template_name = 'usuarios/actualizar_perfil.html'
    fields = ['first_name', 'last_name', 'fecha_nacimiento', 'descripcion', 'avatar']
    success_url = reverse_lazy('usuarios:mi_perfil')
    
    def get_object(self):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Custom styling to fields
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-input'})
        if 'fecha_nacimiento' in form.fields:
            form.fields['fecha_nacimiento'].widget.input_type = 'date'
        if 'descripcion' in form.fields:
            form.fields['descripcion'].widget.attrs.update({'rows': 4})
        return form

    def form_valid(self, form):
        messages.success(self.request, "Tu perfil ha sido actualizado exitosamente.")
        return super().form_valid(form)


# View para cambiar la contraseña del usuario
class CambiarPasswordView(PasswordChangeView):
    template_name = 'usuarios/cambiar_password.html'
    success_url = reverse_lazy('usuarios:inicio_usuario')

    def form_valid(self, form):
        messages.success(self.request, "Tu contraseña ha sido actualizada correctamente.")
        return super().form_valid(form)