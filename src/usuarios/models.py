from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    is_gm = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    