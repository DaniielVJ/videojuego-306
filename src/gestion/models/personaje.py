from django.db import models
from django.conf import settings
from .inventario import Objeto


class Personaje(models.Model):

    class Estado(models.TextChoices):

        VIVO = "vivo", "Vivo"
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
    hp_base = models.PositiveIntegerField(default = 100)
    mana_base = models.PositiveIntegerField(default = 50)
    activo = models.BooleanField(default = True)
    habilidades = models.ManyToManyField('Habilidad', related_name='personajes')
    objetos = models.ManyToManyField(Objeto, related_name='personajes')

    # Slots de Equipamiento
    arma_equipada = models.ForeignKey(Objeto, related_name='equipada_como_arma', on_delete=models.SET_NULL, null=True, blank=True)
    casco_equipado = models.ForeignKey(Objeto, related_name='equipada_como_casco', on_delete=models.SET_NULL, null=True, blank=True)
    armadura_equipada = models.ForeignKey(Objeto, related_name='equipada_como_armadura', on_delete=models.SET_NULL, null=True, blank=True)
    zapatos_equipados = models.ForeignKey(Objeto, related_name='equipada_como_zapatos', on_delete=models.SET_NULL, null=True, blank=True)
    collar_equipado = models.ForeignKey(Objeto, related_name='equipada_como_collar', on_delete=models.SET_NULL, null=True, blank=True)
    brazalete_equipado = models.ForeignKey(Objeto, related_name='equipada_como_brazalete', on_delete=models.SET_NULL, null=True, blank=True)
    escudo_equipado = models.ForeignKey(Objeto, related_name='equipada_como_escudo', on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def hp_total(self):
        try:
            # Vigor da 10 puntos de salud extra por cada punto
            return self.hp_base + (self.atributos.vigor * 10)
        except Exception:
            return self.hp_base

    @property
    def mana_total(self):
        try:
            # Inteligencia da 10 puntos de mana extra por cada punto
            return self.mana_base + (self.atributos.inteligencia * 10)
        except Exception:
            return self.mana_base

    def __str__(self):
        return self.nombre

    @property
    def equipo_actual(self):
        return [
            self.arma_equipada,
            self.casco_equipado,
            self.armadura_equipada,
            self.zapatos_equipados,
            self.collar_equipado,
            self.brazalete_equipado,
            self.escudo_equipado
        ]

    def obtener_bonificadores_equipo(self):
        # Esto acumula los bonos para atributos del personaje
        # que otorga cada objeto, permitiendo tener el total de fuerza, int, etc
        # que da cada objeto.
        bonos = {}
        for obj in self.equipo_actual:
            if obj and obj.efectos:
                for key, val in obj.efectos.items():
                    bonos[key] = bonos.get(key, 0) + val
        return bonos



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
    nombre = models.CharField(max_length = 100, null = False, unique=True)
    descripcion = models.TextField(max_length = 500, null = False)
    r_bonificadores = models.JSONField(blank=True, null=True)
    r_handicap = models.JSONField(blank=True, null=True)
    activo = models.BooleanField(default = True)
    img_body = models.ImageField(upload_to='razas/body/', null=False, blank=False)
    img_head = models.ImageField(upload_to='razas/head/', null=False, blank=False)
    
    def __str__(self):
        return self.nombre


class Habilidad(models.Model):
    nombre = models.CharField(max_length = 100, null = False, unique=True)
    descripcion = models.TextField(max_length = 500, null = False)
    efectos = models.JSONField(blank=True, null=True)
    costo = models.JSONField(blank=True, null=True)
    kit_inicial = models.BooleanField(default=False)
    activo = models.BooleanField(default = True)


    def __str__(self):
        return self.nombre
        
