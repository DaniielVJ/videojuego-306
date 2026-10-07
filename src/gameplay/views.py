import random
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from src.gestion.models import Personaje, Objeto, InventarioItem
from src.gestion.services import AccionInvalida, personaje_para_usuario, validar_id, validar_uso


class TiendaView(LoginRequiredMixin, View):
    template_name = 'gameplay/tienda.html'

    def get(self, request, personaje_id):
        personaje = personaje_para_usuario(request, personaje_id)
        if personaje.esta_congelado():
            messages.error(request, 'No puedes realizar esta acción porque tu personaje está congelado.')
            return redirect('player:detalle_personaje', pk=personaje.pk)
        return render(request, self.template_name, {
            'personaje': personaje,
            'objetos_venta': Objeto.objects.filter(activo=True).order_by('precio_compra'),
            'inventario_items': InventarioItem.objects.filter(personaje=personaje, cantidad__gt=0).select_related('objeto'),
        })

    def post(self, request, personaje_id):
        try:
            with transaction.atomic():
                personaje = personaje_para_usuario(request, personaje_id, bloquear=True)
                validar_uso(personaje)
                accion = request.POST.get('accion')
                if accion not in ('comprar', 'vender'):
                    raise AccionInvalida('Acción de tienda inválida.')
                objeto_id = validar_id(request.POST.get('objeto_id'))
                objeto = get_object_or_404(Objeto, pk=objeto_id, activo=True)
                if accion == 'comprar':
                    if personaje.oro < objeto.precio_compra:
                        messages.error(request, f'Necesitas {objeto.precio_compra} de oro para comprar {objeto.nombre}.')
                    else:
                        item, _ = InventarioItem.objects.select_for_update().get_or_create(
                            personaje=personaje, objeto=objeto, defaults={'cantidad': 0})
                        item.cantidad += 1
                        item.save()
                        personaje.oro -= objeto.precio_compra
                        personaje.save()
                        messages.success(request, f'Has comprado {objeto.nombre}. Requiere nivel {objeto.nivel} para usarlo.')
                else:
                    item = InventarioItem.objects.select_for_update().filter(
                        personaje=personaje, objeto=objeto, cantidad__gt=0).first()
                    if item is None:
                        raise AccionInvalida('No tienes este objeto en tu inventario para venderlo.', 403)
                    item.cantidad -= 1
                    if item.cantidad:
                        item.save(update_fields=['cantidad'])
                    else:
                        for slot in Personaje.SLOTS.values():
                            if getattr(personaje, f'{slot}_id') == objeto.pk:
                                setattr(personaje, slot, None)
                        item.delete()
                    personaje.oro += objeto.precio_venta
                    personaje.hp_actual = min(personaje.hp_actual, personaje.hp_total)
                    personaje.mana_actual = min(personaje.mana_actual, personaje.mana_total)
                    personaje.save()
                    messages.success(request, f'Has vendido {objeto.nombre} por {objeto.precio_venta} de oro.')
        except AccionInvalida as error:
            return JsonResponse({'error': error.mensaje}, status=error.status)
        return redirect('gameplay:tienda', personaje_id=personaje.pk)


class TrabajoView(LoginRequiredMixin, View):
    template_name = 'gameplay/trabajo.html'

    def get(self, request, personaje_id):
        personaje = personaje_para_usuario(request, personaje_id)
        if personaje.esta_congelado():
            messages.error(request, 'No puedes realizar esta acción porque tu personaje está congelado.')
            return redirect('player:detalle_personaje', pk=personaje.pk)
        return render(request, self.template_name, {'personaje': personaje})

    def post(self, request, personaje_id):
        try:
            with transaction.atomic():
                personaje = personaje_para_usuario(request, personaje_id, bloquear=True)
                validar_uso(personaje)
                accion = request.POST.get('accion')
                if accion not in ('mina', 'biblioteca', 'posada'):
                    raise AccionInvalida('Acción de trabajo inválida.')
                if accion in ('mina', 'biblioteca'):
                    recurso = 'hp_actual' if accion == 'mina' else 'mana_actual'
                    if getattr(personaje, recurso) < 20:
                        messages.error(request, 'Necesitas al menos 20 HP.' if accion == 'mina' else 'Necesitas al menos 20 de maná.')
                    else:
                        setattr(personaje, recurso, getattr(personaje, recurso) - 20)
                        oro = random.randint(15, 30) if accion == 'mina' else random.randint(5, 10)
                        xp = random.randint(2, 5) if accion == 'mina' else random.randint(15, 25)
                        personaje.oro += oro
                        subidas = personaje.ganar_experiencia(xp)
                        personaje.save()
                        messages.success(request, f'Ganaste {oro} de oro y {xp} XP en {accion}.')
                        if subidas:
                            messages.success(request, f'¡Has subido al nivel {personaje.nivel}!')
                elif personaje.oro >= 10:
                    personaje.oro -= 10
                    personaje.hp_actual = min(personaje.hp_total, personaje.hp_actual + 50)
                    personaje.mana_actual = min(personaje.mana_total, personaje.mana_actual + 50)
                    personaje.save()
                    messages.success(request, 'Descansaste por 10 de oro y recuperaste salud y maná.')
                else:
                    messages.error(request, 'Necesitas 10 de oro para descansar en la posada.')
        except AccionInvalida as error:
            return JsonResponse({'error': error.mensaje}, status=error.status)
        return redirect('gameplay:trabajar', personaje_id=personaje.pk)
