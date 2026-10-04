from django.db import models


class Objeto(models.Model):

	class TipoEquipamiento(models.TextChoices):
		ARMA = 'arma', 'Arma'
		CASCO = 'casco', 'Casco'
		ARMADURA = 'armadura', 'Armadura'
		ZAPATOS = 'zapatos', 'Zapatos'
		COLLAR = 'collar', 'Collar'
		BRAZALETE = 'brazalete', 'Brazalete'
		ESCUDO = 'escudo', 'Escudo'

	nombre = models.CharField(max_length = 100, null = False, unique=True)
	descripcion = models.TextField(max_length = 500, null = False)
	peso = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, blank=False, null=False)
	efectos = models.JSONField(blank=True, null=True)
	activo = models.BooleanField(default = True)
	img = models.ImageField(upload_to='objetos/', null=False, blank=False)
	es_equipable = models.BooleanField(default=False)
	tipo_equipamiento = models.CharField(max_length=20, choices=TipoEquipamiento.choices, null=True, blank=True)
	kit_inicial = models.BooleanField(default=False)

	def __str__(self):
		return self.nombre


