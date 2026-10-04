import os
import sys
import django

# Add src to python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from gestion.models import Objeto

bonos = {
    'arma': {'fuerza': 15, 'destreza': 5},
    'casco': {'vigor': 10, 'inteligencia': 2},
    'armadura': {'vigor': 25, 'fuerza': 5},
    'zapatos': {'destreza': 15, 'suerte': 5},
    'collar': {'inteligencia': 20, 'percepcion': 10},
    'brazalete': {'fuerza': 10, 'carisma': 5},
    'escudo': {'vigor': 15, 'suerte': 2},
}

for obj in Objeto.objects.all():
    if obj.es_equipable:
        tipo = obj.tipo_equipamiento
        if not tipo:
            n = obj.nombre.lower()
            if 'espada' in n or 'hacha' in n or 'arco' in n or 'bastón' in n: tipo = 'arma'
            elif 'casco' in n or 'yelmo' in n: tipo = 'casco'
            elif 'armadura' in n or 'cota' in n: tipo = 'armadura'
            elif 'bota' in n or 'zapato' in n: tipo = 'zapatos'
            elif 'collar' in n or 'amuleto' in n: tipo = 'collar'
            elif 'brazalete' in n or 'guante' in n: tipo = 'brazalete'
            elif 'escudo' in n: tipo = 'escudo'
        
        obj.tipo_equipamiento = tipo
        if tipo in bonos:
            obj.efectos = bonos[tipo]
            obj.save()
            print(f'Actualizado {obj.nombre} ({tipo}): {obj.efectos}')

