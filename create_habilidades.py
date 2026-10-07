from src.gestion.models import Habilidad

habilidades_data = [
    {
        "nombre": "Golpe Devastador",
        "descripcion": "Un impacto físico brutal capaz de romper armaduras y quebrar defensas.",
        "efectos": {"daño_fisico": 50, "rompe_armadura": True},
        "costo": {"energia": 20}
    },
    {
        "nombre": "Bola de Fuego",
        "descripcion": "Lanza una esfera incandescente que explota al contacto, calcinando al enemigo.",
        "efectos": {"daño_magico": 60, "quemadura": 10},
        "costo": {"mana": 25}
    },
    {
        "nombre": "Sanación Rápida",
        "descripcion": "Recupera puntos de vida instantáneamente canalizando pura magia de luz.",
        "efectos": {"curacion": 40},
        "costo": {"mana": 20}
    },
    {
        "nombre": "Grito de Guerra",
        "descripcion": "Un rugido motivador que aumenta la fuerza de combate tuya y de tus aliados.",
        "efectos": {"buff_fuerza": 15, "duracion_turnos": 3},
        "costo": {"energia": 15}
    },
    {
        "nombre": "Sigilo Sombrío",
        "descripcion": "Te fundes con las sombras haciéndote indetectable para los sentidos comunes.",
        "efectos": {"invisibilidad": True, "bono_esquive": 30},
        "costo": {"energia": 10}
    },
    {
        "nombre": "Lluvia de Flechas",
        "descripcion": "Dispara una andanada de proyectiles que caen sobre un área castigando a múltiples enemigos.",
        "efectos": {"daño_area": 35},
        "costo": {"energia": 30}
    },
    {
        "nombre": "Escudo Arcano",
        "descripcion": "Crea una barrera rúnica que absorbe el daño entrante antes de lastimar al usuario.",
        "efectos": {"escudo_absorcion": 50},
        "costo": {"mana": 30}
    },
    {
        "nombre": "Robo de Vida",
        "descripcion": "Magia oscura que drena la vitalidad del enemigo para restaurar la propia.",
        "efectos": {"daño_magico": 30, "robo_vida": 15},
        "costo": {"mana": 25}
    },
    {
        "nombre": "Tormenta de Hielo",
        "descripcion": "Congela el ambiente en un área amplia, infligiendo daño y reduciendo la velocidad de movimiento.",
        "efectos": {"daño_magico": 40, "ralentizar_porcentaje": 50},
        "costo": {"mana": 45}
    },
    {
        "nombre": "Corte Relámpago",
        "descripcion": "Un tajo vertiginoso infundido con el poder del trueno, casi imposible de evadir.",
        "efectos": {"daño_fisico": 45, "daño_rayo": 15},
        "costo": {"energia": 25}
    }
]

for data in habilidades_data:
    Habilidad.objects.get_or_create(nombre=data["nombre"], defaults={
        "descripcion": data["descripcion"],
        "efectos": data["efectos"],
        "costo": data["costo"],
        "activo": True
    })

print("¡10 Habilidades Épicas insertadas en la base de datos!")
