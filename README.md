# El Reino — videojuego-306

Aplicación web de juego de rol en Django para gestionar personajes, razas, habilidades, inventario, tienda y trabajos. Los jugadores administran sus propios personajes; los Game Masters gestionan personajes y catálogos.

## Tecnología real

Python 3.13, Django 6.1, SQLite, plantillas Django y CSS/JavaScript propios. Dependencias en `requirements.txt`. No hay Tailwind, React, JWT ni servicios de nube implementados.

## Ejecutar comprobaciones

Desde PowerShell en la raíz, con el entorno existente:

```powershell
.\.venv\Scripts\python.exe manage.py check --settings=config.test_settings
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run --settings=config.test_settings
.\.venv\Scripts\python.exe manage.py test --settings=config.test_settings --noinput
```

Las pruebas usan SQLite y archivos en memoria, no leen `.env` ni usan las partidas locales. Resultado de la revisión: **79 pruebas aprobadas**. El entorno emite un aviso sobre la ubicación del Python original, aunque los comandos del entorno funcionan.

## Jugar y administrar

La configuración normal es `config/settings.py`; consultar [preparación del entorno y migraciones](docs/ENTORNO_Y_VERIFICACION.md) antes de crear una base o actualizar una copia existente.

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

El jugador comienza en nivel 1. Para pasar de nivel N a N+1 necesita `100 × N` XP. Los trabajos otorgan XP en el servidor; se conserva el excedente. Los objetos tienen un nivel mínimo para equipar o consumir, editable por GM. Se permite comprarlos antes de alcanzar ese nivel.

## Documentación del proyecto

- [Proyecto y alcance](docs/PROYECTO.md)
- [Arquitectura](docs/ARQUITECTURA_BASE.md)
- [Estado y pendientes](docs/ESTADO_PROYECTO.md)
- [Problemas encontrados](docs/OBSERVACIONES_BASE.md)
- [Verificación ejecutada](docs/VERIFICACION.md)
- [Especificación de niveles](specs/001-niveles-y-estabilidad/spec.md)
- [Índice de especificaciones](specs/README.md)
- [Manual SDD](MANUAL_SDD.md)

Los documentos generales describen este juego. `prompts/` y `specs/_templates/` siguen siendo ayudas reutilizables. La carpeta recibida no contenía historial `.git`; no se realizaron commits ni push. La base local fue respaldada y migrada con autorización del usuario; no se desplegó producción.
