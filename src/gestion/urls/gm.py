from django.urls import path
from ..views import ListarPersonajesView

app_name = "gm"

urlpatterns = [
    path('personajes/', ListarPersonajesView.as_view(), name='listar-personajes'),
]