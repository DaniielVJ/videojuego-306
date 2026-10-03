import os
import django
import random

from django.contrib.auth import get_user_model
from src.gestion.models import Personaje, Raza, Habilidad, Objeto, Atributo

User = get_user_model()

# 1. Obtener un usuario válido o crearlo
user = User.objects.first()
if not user:
    user = User.objects.create_user(username='gm_seed', password='password123', is_gm=True)

# 2. Extraer dependencias de la BD (asumiendo que existen razas, etc.)
razas = list(Raza.objects.filter(activo=True))
habilidades = list(Habilidad.objects.filter(activo=True))
objetos = list(Objeto.objects.filter(activo=True))

if not razas:
    print("ERROR: No hay Razas en la base de datos.")
    exit(1)
if len(habilidades) < 2:
    print("ERROR: Hacen falta al menos 2 habilidades en la BD.")
    exit(1)
if len(objetos) < 2:
    print("ERROR: Hacen falta al menos 2 objetos en la BD.")
    exit(1)

# Lista de nombres épicos para los 15 personajes de prueba
nombres_epicos = [
    "Arthas", "Illidan", "Sylvanas", "Thrall", "Jaina",
    "Uther", "Grommash", "Malfurion", "Tyrande", "Gul'dan",
    "Kael'thas", "Varian", "Vol'jin", "Rexxar", "Garrosh"
]

print("Iniciando forja de héroes...")

personajes_creados = 0

for i in range(15):
    nombre_elegido = f"{nombres_epicos[i]} Test"
    raza_elegida = random.choice(razas)
    
    # Elegir exactamente 2 habilidades y 2 objetos
    habs_elegidas = random.sample(habilidades, 2)
    objs_elegidos = random.sample(objetos, 2)
    
    # Generar 20 puntos base distribuidos aleatoriamente
    # para no corromper la regla de los 20 puntos.
    atributos_vals = [0] * 7
    for _ in range(20):
        idx = random.randint(0, 6)
        atributos_vals[idx] += 1
        
    f, d, v, i_int, p, c, s = atributos_vals

    # Borramos si el nombre ya existiese por pruebas anteriores
    Personaje.objects.filter(nombre=nombre_elegido).delete()

    # 1. Crear el modelo Personaje
    pj = Personaje.objects.create(
        usuario=user,
        nombre=nombre_elegido,
        raza=raza_elegida,
        estado=Personaje.Estado.VIVO,
        nivel=random.randint(1, 20),
        experiencia=random.randint(0, 99),
        exp_siguiente_nivel=100,
        activo=True
    )
    
    # 2. Crear su registro asociado OneToOne Atributo
    Atributo.objects.create(
        personaje=pj,
        fuerza=f,
        destreza=d,
        vigor=v,
        inteligencia=i_int,
        percepcion=p,
        carisma=c,
        suerte=s
    )
    
    # 3. Asignar relaciones M2M
    pj.habilidades.set(habs_elegidas)
    pj.objetos.set(objs_elegidos)
    
    personajes_creados += 1
    print(f"[{personajes_creados}/15] Creado: {nombre_elegido} ({raza_elegida.nombre})")

print("¡15 Personajes de Prueba forjados y listos en la Base de Datos!")
