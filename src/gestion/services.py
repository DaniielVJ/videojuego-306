"""Validaciones compartidas por las APIs de jugador y GM."""
import json
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Atributo, InventarioItem, Objeto, Personaje

ATRIBUTOS = ('fuerza', 'destreza', 'vigor', 'inteligencia', 'percepcion', 'carisma', 'suerte')


class AccionInvalida(Exception):
    def __init__(self, mensaje, status=400):
        self.mensaje, self.status = mensaje, status


def validar_id(value):
    if isinstance(value, str) and value.isascii() and value.isdigit() and len(value) <= 18:
        value = int(value)
    if type(value) is not int or not 0 < value < 2**63:
        raise AccionInvalida('El ID del objeto debe ser un entero positivo.')
    return value


def personaje_para_usuario(request, pk, gm=False, bloquear=False):
    qs = Personaje.objects.filter(activo=True)
    if bloquear:
        qs = qs.select_for_update()
    if not gm:
        qs = qs.filter(usuario=request.user)
    return get_object_or_404(qs, pk=pk)


def validar_uso(personaje, objeto=None):
    if personaje.estado != Personaje.Estado.VIVO:
        raise AccionInvalida('Solo los personajes vivos pueden realizar esta acción.', 403)
    if objeto is not None:
        if not objeto.activo:
            raise AccionInvalida('Este objeto está deshabilitado.', 403)
        if personaje.nivel < objeto.nivel:
            raise AccionInvalida(f'Necesitas nivel {objeto.nivel} para usar este objeto.', 403)


def datos_personaje(personaje):
    return {
        'hp_actual': personaje.hp_actual, 'hp_total': personaje.hp_total,
        'mana_actual': personaje.mana_actual, 'mana_total': personaje.mana_total,
        'stats_totales': personaje.stats_totales,
    }


def usar_objeto(request, pk, *, gm=False, consumir=False):
    try:
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise AccionInvalida('JSON inválido.')
        if not isinstance(data, dict):
            raise AccionInvalida('El JSON debe ser un objeto con los parámetros de la acción.')
        objeto_id = validar_id(data.get('objeto_id'))
        accion = 'consumir' if consumir else data.get('accion')
        if accion not in ('equipar', 'desequipar', 'consumir') or (not consumir and accion == 'consumir'):
            raise AccionInvalida("Acción inválida. Usa 'equipar' o 'desequipar'.")
        with transaction.atomic():
            personaje = personaje_para_usuario(request, pk, gm=gm, bloquear=True)
            objeto = get_object_or_404(Objeto, pk=objeto_id)
            item = InventarioItem.objects.select_for_update().filter(
                personaje=personaje, objeto=objeto, cantidad__gt=0).first()
            if item is None:
                raise AccionInvalida('El personaje no posee este objeto en su inventario.', 403)
            if accion != 'desequipar':
                validar_uso(personaje, objeto)
            if consumir:
                resultado = consumir_item(personaje, objeto, item)
            else:
                resultado = equipar_item(personaje, objeto, accion)
            personaje.hp_actual = min(personaje.hp_actual, personaje.hp_total)
            personaje.mana_actual = min(personaje.mana_actual, personaje.mana_total)
            personaje.save()
            return JsonResponse({'status': 'success', **resultado, **datos_personaje(personaje)})
    except AccionInvalida as error:
        return JsonResponse({'error': error.mensaje}, status=error.status)


def equipar_item(personaje, objeto, accion):
    tipo = (objeto.tipo_equipamiento or '').strip().lower()
    if tipo.endswith('s') and tipo != 'zapatos':
        tipo = tipo[:-1]
    slot = Personaje.SLOTS.get(tipo)
    if not slot or (accion == 'equipar' and not objeto.es_equipable):
        raise AccionInvalida('Este objeto no es equipable o no tiene un tipo definido.')
    if accion == 'desequipar' and getattr(personaje, f'{slot}_id') != objeto.pk:
        raise AccionInvalida('Este objeto no está equipado en ese espacio.')
    setattr(personaje, slot, objeto if accion == 'equipar' else None)
    return {'mensaje': 'Objeto equipado.' if accion == 'equipar' else 'Objeto desequipado.',
            'slot_modificado': tipo, 'bonificadores_actuales': personaje.obtener_bonificadores_equipo()}


def consumir_item(personaje, objeto, item):
    if objeto.es_equipable:
        raise AccionInvalida('No puedes consumir un objeto equipable.')
    efectos = objeto.efectos
    if not isinstance(efectos, dict) or not efectos:
        raise AccionInvalida('Este objeto no tiene efectos consumibles.')
    permitidos = {*ATRIBUTOS, 'hp_restore', 'mana_restore'}
    if any(key not in permitidos or type(value) is not int or value < 0 for key, value in efectos.items()):
        raise AccionInvalida('Los efectos del objeto no son válidos.')
    atributos = Atributo.objects.filter(personaje=personaje).first()
    if atributos is not None:
        # Usar la misma instancia en las estadísticas derivadas y en los
        # efectos permanentes, evitando respuestas con atributos en caché viejos.
        personaje.atributos = atributos
    aplicado = False
    for stat, amount in efectos.items():
        if not amount:
            continue
        if stat in ('hp_restore', 'mana_restore'):
            campo, limite = ('hp_actual', personaje.hp_total) if stat == 'hp_restore' else ('mana_actual', personaje.mana_total)
            anterior = getattr(personaje, campo)
            nuevo = min(limite, anterior + amount)
            if nuevo > anterior:
                setattr(personaje, campo, nuevo)
                aplicado = True
        else:
            if atributos is None:
                raise AccionInvalida('El personaje no tiene atributos asignados.')
            anterior = getattr(atributos, stat)
            nuevo = min(anterior + amount, 999)
            if nuevo > anterior:
                setattr(atributos, stat, nuevo)
                aplicado = True
    if not aplicado:
        raise AccionInvalida('Ya tienes tu vitalidad/maná al máximo.' if {'hp_restore', 'mana_restore'} & efectos.keys()
                             else 'No puedes usar este objeto ahora mismo.')
    if atributos is not None:
        atributos.save()
    item.cantidad -= 1
    restante = item.cantidad
    if restante:
        item.save(update_fields=['cantidad'])
    else:
        item.delete()
    return {'mensaje': f'Has consumido {objeto.nombre}.', 'cantidad_restante': restante}
