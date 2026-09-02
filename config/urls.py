from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rpg/', include('src.gestion.urls')),
    path('users/', include('src.usuarios.urls'))
]
