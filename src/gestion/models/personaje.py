from django.db import models
from django.conf import settings

class Personaje(models.Model):
    class Estado(models.TextChoices):
        VIVO = "vivo", "Vivo",
        MUERTO = 'muerto', 'Muerto'
        CONGELADO = 'congelado', 'Congelado'


    class Meta:
        verbose_name = "Personaje"
        verbose_name_plural = "Personajes"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='personajes')
    nombre = models.CharField(max_length=50, null=False)
    raza = models.ForeignKey('Raza', on_delete=models.PROTECT, related_name='personajes')
    estado = models.CharField(max_length = 50, choices=Estado.choices, default=Estado.VIVO, null = False)
    nivel = models.PositiveIntegerField(default = 1)
    experiencia = models.PositiveIntegerField(default = 0)
    exp_siguiente_nivel = models.PositiveIntegerField(default = 100)
    activo = models.BooleanField(default = True)
    habilidades = models.ManyToManyField('Habilidad', related_name='personajes')


class Atributo(models.Model):

    class Meta:
        verbose_name = "Atributo"
        verbose_name_plural = "Atributos"

    personaje = models.OneToOneField(Personaje, on_delete=models.PROTECT, related_name="atributos")
    fuerza = models.PositiveIntegerField(null = False)
    destreza = models.PositiveIntegerField(null = False)
    vigor = models.PositiveIntegerField(null = False)
    inteligencia = models.PositiveIntegerField(null = False)
    percepcion = models.PositiveIntegerField(null = False)
    carisma = models.PositiveIntegerField(null = False)
    suerte = models.IntegerField(null = False)


class Raza(models.Model):
	nombre = models.CharField(max_length = 100, null = False)
	descripcion = models.TextField(max_length = 500, null = False)
	r_bonificadores = models.JSONField(null = False)
	r_handicap = models.JSONField(null = False)
	activo = models.BooleanField(default = True)


class Habilidad(models.Model):
	nombre = models.CharField(max_length = 100, null = False)
	descripcion = models.TextField(max_length = 500, null = False)
	efectos = models.JSONField(null = False)
	costo = models.JSONField(null = False)
	activo = models.BooleanField(default = True)