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
    nombre = models.CharField(max_length=50, null=False, unique=True)
    raza = models.ForeignKey('Raza', on_delete=models.PROTECT, related_name='personajes')
    estado = models.CharField(max_length = 50, choices=Estado.choices, default=Estado.VIVO, null = False)
    nivel = models.PositiveIntegerField(default = 1)
    experiencia = models.PositiveIntegerField(default = 0)
    exp_siguiente_nivel = models.PositiveIntegerField(default = 100)
    activo = models.BooleanField(default = True)
    habilidades = models.ManyToManyField('Habilidad', related_name='personajes')


    def __str__(self):
        return self.nombre

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

    def __str__(self):
        return self.personaje.nombre


class Raza(models.Model):
    nombre = models.CharField(max_length = 100, null = False)
    descripcion = models.TextField(max_length = 500, null = False)
    r_bonificadores = models.JSONField(blank=True, null=True)
    r_handicap = models.JSONField(blank=True, null=True)
    activo = models.BooleanField(default = True)
    img_body = models.ImageField(upload_to='razas/body/', null=False, blank=False)
    img_head = models.ImageField(upload_to='razas/head/', null=False, blank=False)
    
    def __str__(self):
        return self.nombre


class Habilidad(models.Model):
    nombre = models.CharField(max_length = 100, null = False)
    descripcion = models.TextField(max_length = 500, null = False)
    efectos = models.JSONField(blank=True, null=True)
    costo = models.JSONField(blank=True, null=True)
    activo = models.BooleanField(default = True)


    def __str__(self):
        return self.nombre
        