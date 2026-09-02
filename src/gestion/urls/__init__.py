from django.urls import include, path

urlpatterns = [
    path('player/', include('src.gestion.urls.player')),
    path('gm/', include('src.gestion.urls.gm'))
]