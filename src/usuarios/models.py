from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    is_gm = models.BooleanField(default=False)
    # Fecha de nacimiento por ahora no

    def __str__(self):
        return self.username

class CodigoVerificacionEmail(models.Model):
    user = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="codigos_email")
    code = models.PositiveBigIntegerField()
    create_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()