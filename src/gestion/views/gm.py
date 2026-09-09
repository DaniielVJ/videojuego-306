from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.db.models import Q
from django.urls import reverse_lazy
from django.db import transactions
from src.gestion.models.personaje import Raza, Habilidad, 