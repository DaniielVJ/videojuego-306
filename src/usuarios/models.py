from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    is_gm = models.BooleanField(default=False)
    
    # Campos de Perfil
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    descripcion = models.TextField(max_length=1000, null=True, blank=True, verbose_name="Descripción / Biografía")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Avatar del Jugador")

    def __str__(self):
        return self.username
