from django.db import models


class Objeto(models.Model):

	nombre = models.CharField(max_length = 100, null = False)
	descripcion = models.TextField(max_length = 500, null = False)
	peso = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, blank=False, null=False)
	efectos = models.JSONField(blank=True, null=True)
	activo = models.BooleanField(default = True)
	img = models.ImageField(upload_to='objetos/', null=False, blank=False)
	es_equipable = models.BooleanField(default=False)
	kit_inicial = models.BooleanField(default=False)

	def __str__(self):
		return self.nombre


