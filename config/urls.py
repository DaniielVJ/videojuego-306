from django.contrib import admin
from django.urls import path, include

from src.usuarios.views import InicioJuegoView

urlpatterns = [
    path('', InicioJuegoView.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('rpg/', include('src.gestion.urls')),
    path('users/', include('src.usuarios.urls'))
]
