from django.db import models
from .personaje import Personaje

class Objeto(models.Model):
	nombre = models.CharField(max_length = 100, null = False)
	descripcion = models.TextField(max_length = 500, null = False)
	peso = models.DecimalField(null = False)
	efectos = models.JSONField(null = False)
	activo = models.BooleanField(default = True)


class InventarioObjetos(models.Model):
	personaje = models.ForeignKey(Personaje, on_delete = models.PROTECT, related_name = "inventario")
	objeto = models.ForeignKey(Objeto, on_delete = models.PROTECT, related_name = "personajes")

