from django.db import models
from django.conf import settings
from .inventario import Objeto


class InventarioItem(models.Model):
    personaje = models.ForeignKey('Personaje', on_delete=models.CASCADE)
    objeto = models.ForeignKey(Objeto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('personaje', 'objeto')
        verbose_name = "Item de Inventario"
        verbose_name_plural = "Items de Inventario"

    def __str__(self):
        return f"{self.cantidad}x {self.objeto.nombre} ({self.personaje.nombre})"


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
    hp_actual = models.IntegerField(default = 100)
    mana_base = models.PositiveIntegerField(default = 50)
    mana_actual = models.IntegerField(default = 50)
    activo = models.BooleanField(default = True)
    habilidades = models.ManyToManyField('Habilidad', related_name='personajes')
    objetos = models.ManyToManyField(Objeto, through='InventarioItem', related_name='personajes')

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
            # Vigor total (base + equipo) da 10 puntos de salud extra por cada punto
            vigor = self.stats_totales.get('vigor', self.atributos.vigor if hasattr(self, 'atributos') else 0)
            return self.hp_base + (vigor * 10)
        except Exception:
            return self.hp_base

    @property
    def mana_total(self):
        try:
            # Inteligencia total (base + equipo) da 10 puntos de mana extra por cada punto
            intel = self.stats_totales.get('inteligencia', self.atributos.inteligencia if hasattr(self, 'atributos') else 0)
            return self.mana_base + (intel * 10)
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
                    if val != 0:
                        clean_key = key[2:] if key.startswith('v_') else key
                        bonos[clean_key] = bonos.get(clean_key, 0) + val
        return bonos

    @property
    def stats_totales(self):
        bonos = self.obtener_bonificadores_equipo()
        bonos_raza = self.raza.r_bonificadores or {}
        try:
            attr = self.atributos
            return {
                'fuerza': attr.fuerza + bonos.get('fuerza', 0) + int(bonos_raza.get('fuerza', 0)),
                'destreza': attr.destreza + bonos.get('destreza', 0) + int(bonos_raza.get('destreza', 0)),
                'vigor': attr.vigor + bonos.get('vigor', 0) + int(bonos_raza.get('vigor', 0)),
                'inteligencia': attr.inteligencia + bonos.get('inteligencia', 0) + int(bonos_raza.get('inteligencia', 0)),
                'percepcion': attr.percepcion + bonos.get('percepcion', 0) + int(bonos_raza.get('percepcion', 0)),
                'carisma': attr.carisma + bonos.get('carisma', 0) + int(bonos_raza.get('carisma', 0)),
                'suerte': attr.suerte + bonos.get('suerte', 0) + int(bonos_raza.get('suerte', 0)),
            }
        except Exception:
            return {}



class Atributo(models.Model):

    class Meta:
        verbose_name = "Atributo"
        verbose_name_plural = "Atributos"

    personaje = models.OneToOneField(Personaje, on_delete=models.CASCADE, related_name="atributos")

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
        
