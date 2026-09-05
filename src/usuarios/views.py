from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

# Aqui programo la logica de si es gm redirija a el inicio GM si no al player.
class RedireccionInicioView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_gm:
            return redirect()
        return redirect()


