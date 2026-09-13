from django.contrib import admin
from ..models import Personaje, Atributo, Raza, Habilidad, InventarioObjetos, Objeto

@admin.register(Personaje)
class PersonajeAdmin(admin.ModelAdmin):
    # Columnas principales en la vista de lista
    list_display = ('nombre', 'usuario', 'raza', 'nivel', 'estado', 'activo')
    
    # Filtros laterales para agrupar rápidamente
    list_filter = ('estado', 'activo', 'raza')
    
    # Búsqueda por nombre de personaje o nombre del usuario dueño
    search_fields = ('nombre', 'usuario__username')
    
    # Permite editar estos campos directamente desde la tabla general
    list_editable = ('estado', 'activo')
    
    # Mejora visual drástica para el campo ManyToMany
    filter_horizontal = ('habilidades',)

@admin.register(Atributo)
class AtributoAdmin(admin.ModelAdmin):
    # Expone todas las estadísticas vitales de un vistazo
    list_display = ('personaje', 'fuerza', 'destreza', 'vigor', 'inteligencia', 'percepcion', 'carisma', 'suerte')
    
    # Búsqueda cruzada por nombre del personaje o del jugador dueño
    search_fields = ('personaje__nombre', 'personaje__usuario__username')
    
    # Fundamental para un Game Master: editar stats en bloque desde la tabla
    list_editable = ('fuerza', 'destreza', 'vigor', 'inteligencia', 'percepcion', 'carisma', 'suerte')

@admin.register(Raza)
class RazaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo',)

@admin.register(Habilidad)
class HabilidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo',)


@admin.register(Objeto)
class ObjetoAdmin(admin.ModelAdmin):
    # Vista general con datos clave para balancear la carga
    list_display = ('nombre', 'peso', 'activo')
    
    # Filtro rápido para aislar ítems deshabilitados
    list_filter = ('activo',)
    
    # Búsqueda por nombre o palabras clave en la descripción
    search_fields = ('nombre', 'descripcion')
    
    # Permite ajustar el peso de los ítems en masa desde la tabla
    list_editable = ('peso', 'activo')

@admin.register(InventarioObjetos)
class InventarioObjetosAdmin(admin.ModelAdmin):
    # Muestra exactamente qué personaje tiene qué ítem
    list_display = ('personaje', 'objeto')
    
    # Búsqueda cruzada relacional profunda
    search_fields = ('personaje__nombre', 'personaje__usuario__username', 'objeto__nombre')


class InventarioInline(admin.TabularInline):
    model = InventarioObjetos
    extra = 1  # Deja una fila vacía siempre lista para añadir un nuevo ítem
    
    # Habilita un buscador de ítems en lugar de un menú desplegable gigante
    autocomplete_fields = ['objeto']