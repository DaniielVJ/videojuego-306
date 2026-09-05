from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    is_gm = models.BooleanField(default=False)
    # Fecha de nacimiento por ahora no

    def __str__(self):
        return self.username

    