import random
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from src.gestion.models import Personaje, Objeto, InventarioItem


class TiendaView(LoginRequiredMixin, View):
    template_name = 'gameplay/tienda.html'

    def get(self, request, personaje_id):
        # Asegurar que el personaje pertenece al usuario logueado
        personaje = get_object_or_404(Personaje, pk=personaje_id, usuario=request.user)
        
        # Obtener objetos activos (Catálogo de la Tienda)
        objetos_venta = Objeto.objects.filter(activo=True).order_by('precio_compra')
        
        # Obtener los objetos que posee el personaje en su inventario para poder venderlos
        inventario_items = InventarioItem.objects.filter(personaje=personaje).select_related('objeto')
        
        return render(request, self.template_name, {
            'personaje': personaje,
            'objetos_venta': objetos_venta,
            'inventario_items': inventario_items,
        })
        
    def post(self, request, personaje_id):
        objeto_id = request.POST.get('objeto_id')
        accion = request.POST.get('accion') # 'comprar' o 'vender'
        
        try:
            with transaction.atomic():
                # select_for_update() bloquea la fila del personaje para evitar 'Race Conditions' (clonación de oro)
                personaje = get_object_or_404(Personaje.objects.select_for_update(), pk=personaje_id, usuario=request.user)
                objeto = get_object_or_404(Objeto, pk=objeto_id, activo=True)
                
                if accion == 'comprar':
                    if personaje.oro >= objeto.precio_compra:
                        personaje.oro -= objeto.precio_compra
                        personaje.save()
                        
                        inventario_item, created = InventarioItem.objects.get_or_create(
                            personaje=personaje,
                            objeto=objeto,
                            defaults={'cantidad': 0}
                        )
                        inventario_item.cantidad += 1
                        inventario_item.save()
                        
                        messages.success(request, f"Has comprado '{objeto.nombre}' por {objeto.precio_compra} monedas de oro.")
                    else:
                        messages.error(request, f"No tienes suficiente oro para comprar '{objeto.nombre}'. Necesitas {objeto.precio_compra} de oro.")
                
                elif accion == 'vender':
                    inventario_item = InventarioItem.objects.filter(personaje=personaje, objeto=objeto).first()
                    if inventario_item and inventario_item.cantidad > 0:
                        inventario_item.cantidad -= 1
                        
                        if inventario_item.cantidad == 0:
                            # CRÍTICO: Si la cantidad llega a 0, debemos desequipar el objeto para que no se beneficie de sus stats gratis
                            if personaje.arma_equipada == objeto: personaje.arma_equipada = None
                            if personaje.casco_equipado == objeto: personaje.casco_equipado = None
                            if personaje.armadura_equipada == objeto: personaje.armadura_equipada = None
                            if personaje.zapatos_equipados == objeto: personaje.zapatos_equipados = None
                            if personaje.collar_equipado == objeto: personaje.collar_equipado = None
                            if personaje.brazalete_equipado == objeto: personaje.brazalete_equipado = None
                            if personaje.escudo_equipado == objeto: personaje.escudo_equipado = None
                            inventario_item.delete()
                        else:
                            inventario_item.save()
                            
                        personaje.oro += objeto.precio_venta
                        personaje.save()
                        messages.success(request, f"Has vendido '{objeto.nombre}' por {objeto.precio_venta} monedas de oro.")
                    else:
                        messages.error(request, "No tienes este objeto en tu inventario para venderlo.")
                        
        except Exception as e:
            messages.error(request, "Ha ocurrido un error en la transacción.")
            
        return redirect('gameplay:tienda', personaje_id=personaje.pk)

class TrabajoView(LoginRequiredMixin, View):
    template_name = 'gameplay/trabajo.html'

    def get(self, request, personaje_id):
        personaje = get_object_or_404(Personaje, pk=personaje_id, usuario=request.user)
        return render(request, self.template_name, {'personaje': personaje})

    def post(self, request, personaje_id):
        accion = request.POST.get('accion')
        
        try:
            with transaction.atomic():
                personaje = get_object_or_404(Personaje.objects.select_for_update(), pk=personaje_id, usuario=request.user)
                
                if accion == 'mina':
                    if personaje.hp_actual >= 20:
                        personaje.hp_actual -= 20
                        oro_ganado = random.randint(15, 30)
                        xp_ganada = random.randint(2, 5)
                        personaje.oro += oro_ganado
                        personaje.experiencia += xp_ganada
                        personaje.save()
                        messages.success(request, f"¡Has trabajado duro en la mina! Perdiste 20 HP pero ganaste {oro_ganado} 💰 y {xp_ganada} XP.")
                    else:
                        messages.error(request, "Estás demasiado exhausto para picar piedra. Necesitas al menos 20 HP.")
                        
                elif accion == 'biblioteca':
                    if personaje.mana_actual >= 20:
                        personaje.mana_actual -= 20
                        oro_ganado = random.randint(5, 10)
                        xp_ganada = random.randint(15, 25)
                        personaje.oro += oro_ganado
                        personaje.experiencia += xp_ganada
                        personaje.save()
                        messages.success(request, f"¡Tradujiste unos pergaminos antiguos! Gastaste 20 Maná pero conseguiste {oro_ganado} 💰 y {xp_ganada} XP.")
                    else:
                        messages.error(request, "Tu mente está nublada. Necesitas al menos 20 de Maná para concentrarte.")
                        
                elif accion == 'posada':
                    if personaje.oro >= 10:
                        personaje.oro -= 10
                        # Curar HP
                        personaje.hp_actual += 50
                        if personaje.hp_actual > personaje.hp_base: personaje.hp_actual = personaje.hp_base
                        # Curar Mana
                        personaje.mana_actual += 50
                        if personaje.mana_actual > personaje.mana_base: personaje.mana_actual = personaje.mana_base
                        
                        personaje.save()
                        messages.success(request, "Descansaste en la posada por 10 💰. Has recuperado salud y maná.")
                    else:
                        messages.error(request, "El posadero te echa a patadas. Necesitas 10 de Oro para dormir aquí.")

        except Exception as e:
            messages.error(request, "Error al procesar la acción.")
            
        return redirect('gameplay:trabajar', personaje_id=personaje.pk)
