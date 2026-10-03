# Contexto del Proyecto: Aplicación Web de Juego de Rol (videojuego-306)

## 1. Descripción General
Es una aplicación web desarrollada en **Django** que permite la gestión de personajes para un juego de rol. Está diseñada para dos tipos de usuarios:
- **Jugadores**: Pueden crear, ver y gestionar sus propios personajes.
- **Game Masters (GM)**: Tienen permisos elevados para visualizar todos los personajes, modificar sus estados, subir su nivel, y añadir nuevos elementos al juego (razas, habilidades, poderes).

## 2. Tecnologías y Estructura
- **Backend:** Django (Python).
- **Base de Datos:** SQLite (`db.sqlite3`), aunque el enunciado sugiere prepararlo para la nube (MySQL, Oracle, MongoDB).
- **Aplicaciones Django (`src/`):**
  - `usuarios`: Maneja la autenticación y el modelo de usuario personalizado.
  - `gestion`: Contiene la lógica central del juego (modelos de personajes, inventario, razas, habilidades).

## 3. Modelos de Base de Datos Principales
### App: `usuarios`
- **Usuario**: Extiende `AbstractUser` e incluye un campo booleano `is_gm` para diferenciar entre Jugador y Game Master.

### App: `gestion`
- **Personaje**: Relacionado a un `Usuario`. Contiene campos como `nombre`, `raza`, `estado` (Vivo, Muerto, Congelado), `nivel`, `experiencia`. Tiene relaciones ManyToMany con `Habilidad` y `Objeto`.
- **Atributo**: Relación OneToOne con `Personaje` (Fuerza, Destreza, Vigor, etc.).
- **Raza**: Define las razas seleccionables con bonificadores, handicap e imágenes.
- **Habilidad**: Define habilidades con sus efectos y costos.
- **Objeto**: Define los ítems, que pueden ser equipables y parte de un kit inicial.

## 4. Requerimientos Funcionales (Según `enunciado.txt`)
### Módulo de Inicio de Sesión y Roles
- Login diferenciado y autenticación para Jugadores y GMs.

## 4. Requerimientos Funcionales (Dirección Actual: "Super CRUD")
A pesar de las reglas originales, el proyecto se está enfocando en ser un **Super CRUD de personajes** completo y funcional, priorizando la operatividad de las vistas por sobre las restricciones estrictas del enunciado original (como la cantidad exacta de poderes/habilidades, a menos que se solicite específicamente).

### Módulo de Gestión (Player y GM)
- **Operaciones Completas:** Creación, lectura, actualización y eliminación (lógica o física) de personajes para los jugadores (con sus personajes) y GMs (con todos).
- **Atributos y Relaciones:** Manejo de Atributos, Habilidades, Objetos y Razas dentro del mismo flujo de creación y edición.

## 5. Estado Actual a Revisar
- Existen vistas generadas para Player y GM (`src/gestion/views/player.py` y `gm.py`).
- Hay posibles errores de lógica en `player.py` que deben corregirse (ej. en `ListarPersonajes` los permisos parecen estar invertidos para el GM, y en `ActualizarPersonaje` la condición del estado del personaje).
- La vista de eliminar en `gm.py` está vacía (`pass`), mientras que en `player.py` hace borrado lógico (`activo = False`).
- Debemos asegurar que todos los templates correspondientes al CRUD (listados, formularios, detalle) existan y apliquen la estética Épica de Warcraft definida en `CONTEXTO_FRONTEND.md`.
- La aplicación se encuentra actualmente en ejecución mediante `manage.py runserver`.

## 6. Pruebas Unitarias (Tests)
Se han comenzado a implementar tests automatizados para asegurar la integridad de este Super CRUD. Las pruebas actuales se encuentran en `src/gestion/tests/test_personaje_crud.py` e incluyen:
1.  **`test_creacion_personaje_modelo`**: Verifica que los personajes se insertan correctamente en la base de datos con sus atributos básicos, relaciones (usuario, raza) y que nacen con el estado `activo = True`.
2.  **`test_soft_delete_gm_view`**: Simula el comportamiento del Game Master autenticado ingresando al formulario de destierro (Eliminar) y disparando un POST. Valida que el sistema responde con una redirección HTTP 302, que el registro NO es borrado de la base de datos físicamente (el `count()` se mantiene), pero que el atributo `activo` cambia a `False` de forma exitosa (Borrado lógico).
3.  **`test_full_crud_gm`**: Ejecuta de manera secuencial e integral el ciclo completo para un Game Master:
    - **READ**: Ingreso exitoso (HTTP 200) al listado de personajes y verificación de que un personaje aparezca; acceso exitoso a la ficha detallada (`detalle_personaje`).
    - **UPDATE**: Envío de un payload POST al formulario de actualización de héroes modificando el nivel y nombre de un personaje existente, cumpliendo las reglas de atributos numéricos. Se valida redirección (HTTP 302) y que el registro actualice sus campos de forma persistente.
    - **CREATE**: Envío de un payload POST al formulario de creación para dar de alta a un personaje completamente nuevo, asignando exactamente los 20 puntos base obligatorios, 2 habilidades, y 2 objetos de equipo inicial obligatorios. Valida la creación limpia en la BD (HTTP 302).
