from django.contrib import admin
from src.gestion.models.personaje import Personaje, Atributo, Raza, Habilidad
from src.gestion.models.inventario import Objeto, InventarioObjetos

admin.site.register(Raza)
admin.site.register(Habilidad)
admin.site.register(Objeto)
admin.site.register(Personaje)
admin.site.register(Atributo)
admin.site.register(InventarioObjetos)