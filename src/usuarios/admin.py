from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Columnas visibles en la tabla principal
    list_display = ('username', 'email', 'is_gm', 'is_staff', 'is_active')
    
    # Filtros en la barra lateral derecha
    list_filter = ('is_gm', 'is_staff', 'is_active')
    
    # Habilitar barra de búsqueda por texto
    search_fields = ('username', 'email')
    
    # Inyectar tu campo personalizado en la vista de detalle
    fieldsets = UserAdmin.fieldsets + (
        ('Rol de Juego', {'fields': ('is_gm',)}),
    )
