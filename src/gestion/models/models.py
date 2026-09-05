from django.db import models

class atributos(models.Model):

	fuerza = models.PositiveIntegerField(null = False)
	destreza = models.PositiveIntegerField(null = False)
	vigor = models.PositiveIntegerField(null = False)
	inteligencia = models.PositiveIntegerField(null = False)
	percepcion = models.PositiveIntegerField(null = False)
	carisma = models.PositiveIntegerField(null = False)
	suerte = models.IntegerField(null = False)

class objeto(models.Model):

	nombre = models.CharField(max_length = 100, null = False)
	descripcion = models.TextField(max_length = 500, null = False)
	peso = models.DoubleField(null = False)
	efectos = models.JSONField(null = False)

	activo = models.BooleanField(default = True)

class habilidad(models.Model):

	nombre = models.CharField(max_length = 100, null = False)
	descripcion = models.TextField(max_length = 500, null = False)
	efectos = models.JSONField(null = False)
	costo = models.JSONField(null = False)

	activo = models.BooleanField(default = True)

class raza(models.Model):

	nombre = models.CharField(max_length = 100, null = False)
	descripcion = models.TextField(max_length = 500, null = False)
	r_bonificadores = models.JSONField(null = False)
	r_handicap = models.JSONField(null = False)

	activo = models.BooleanField(default = True)

class personaje(models.Model):

	ESTADO = {

		"VIVO": "Vivo",
		"MUERTO": "Muerto",
		"CONGELADO": "Congelado",

	}

	nombre = models.CharField(max_length = 50, null = False)
	raza = models.Charfield(max_length = 50, null = False)
	estado = models.Charfield(max_length = 50, choices = ESTADO, null = False)
	nivel = models.PositiveIntegerField(default = 1)
	experiencia = models.PositiveIntegerField(default = 0)
	exp_siguiente_nivel = models.PositiveIntegerField(default = 100)

	atributos_personaje = models.ForeingKey(atributos, on_delete = models.PROTECT, related_name = "atributos")
	raza_personaje = models.ForeingKey(raza, on_delete = models.PROTECT, related_name = "raza")

	activo = models.BooleanField(default = True)

class inventario_objetos(models.Model):

	personaje = models.ForeingKey(personaje, on_delete = models.PROTECT, related_name = "inventario")
	objeto = moels.ForeingKey(objeto, on_delete = models.PROTECT, related_name = "Invetario de")

class inventario_habilidades(models.Model):

	personaje = models.ForeingKey(personaje, on_delete = models.PROTECT, related_name = "habilidades")
	habilidad = models.ForeingKey(habilidad, on_delete = models.PROTECT, related_name = "habilidad de")