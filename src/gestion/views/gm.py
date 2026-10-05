import json
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, View, DetailView, UpdateView, DeleteView, CreateView
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth import get_user_model


from src.usuarios.mixins import GmRequiredMixin
from ..models import Personaje, Raza, Atributo, Habilidad, Objeto
from ..forms import CrearPersonajeForm, ActualizarPersonajeForm
from ..forms.raza import RazaForm
from ..forms.habilidad import HabilidadUpdateCreateForm
from ..forms.objeto import ObjetoUpdateCreateForm

User = get_user_model()

class ListarPersonajesView(GmRequiredMixin, ListView):
    model = Personaje
    template_name = "gestion/listar_personajes.html"
    context_object_name = "personajes"
    paginate_by = 10

    # Recordatorio:
    # get_context_data: define que datos se envian al template html, aqui podria cargar datos adicionales que no esten
    # en el query_set que listaremos
    # get_queryset: contiene la lista de datos que se obtienen de la DB para listar en el template


    def get_queryset(self):
        # Por defecto el metodo de la clase padre ListView retorna .all()
        qs =  Personaje.objects.select_related('raza', 'usuario').all()
        query, razas, orden = ( self.request.GET.get('q'), 
                        [ int(pk_raza) for pk_raza in self.request.GET.getlist('raza') if pk_raza.isdigit() ],
                        self.request.GET.get('orden', 'nombre'))


        
        if query:
            qs = qs.filter(Q(nombre__istartswith=query) | Q(usuario__username__istartswith=query))

        if razas:
            qs = qs.filter(raza__pk__in=razas)


        campos_validos = [ 'nombre', '-nombre', 'usuario__username', '-usuario__username', 
        'raza__nombre', '-raza__nombre',  'nivel', '-nivel', 'estado', '-estado']


        if orden in campos_validos:
            qs = qs.order_by(orden)
        else:
            qs = qs.order_by('nombre')

    
        return qs

    def get_context_data(self, **kwargs):
        context_data =  super().get_context_data(**kwargs)
        context_data['razas'] = Raza.objects.all()
        context_data['vivos'] = self.object_list.filter(estado=Personaje.Estado.VIVO).count() 
        context_data['muertos'] = self.object_list.filter(estado=Personaje.Estado.MUERTO).count()
        context_data['congelados'] = self.object_list.filter(estado=Personaje.Estado.CONGELADO).count()
        return context_data





# View para crear un personaje
class CrearPersonajeView(GmRequiredMixin, View):
    template_name = 'gestion/crear_personaje.html'


    # Implemento mi propio get context data como las view genericas para obtener los datos que mandaremos al template
    def get_context_data(self, request, form=None, error_msg=None):
        razas = list(Raza.objects.filter(activo=True))
        usuarios = User.objects.filter(is_active=True).order_by('username')
        habilidades = Habilidad.objects.filter(kit_inicial=True, activo=True)
        objetos = Objeto.objects.filter(kit_inicial=True, activo=True)
        razas_json = [
            {
                'id': r.id,
                'nombre': r.nombre,
                'descripcion': r.descripcion,
                'bonificadores': r.r_bonificadores or {}
            }
            for r in razas
        ]
        return {
            'form': form or CrearPersonajeForm(request_user=request.user),
            'razas': razas,
            'usuarios': usuarios,
            'habilidades': habilidades,
            'razas_json': json.dumps(razas_json),
            'error_message': error_msg,
            'objetos': objetos,
        }


    # Solo devolvemos el template para rellenar en el form
    def get(self, request):
        return render(request, self.template_name, self.get_context_data(request))


    def post(self, request):
        form = CrearPersonajeForm(request.POST, request_user=request.user)
        if form.is_valid():
            form.save()
            return redirect('gm:listar-personajes')

        # Extraer el primer error amigable para el banner superior
        error_msg = None
        if form.errors:
            first_err_list = next(iter(form.errors.values()))
            error_msg = first_err_list[0] if first_err_list else "Por favor verifica los campos del personaje."

        return render(request, self.template_name, self.get_context_data(request, form=form, error_msg=error_msg))


from django.contrib.auth.mixins import LoginRequiredMixin

class DetallePersonajeView(LoginRequiredMixin, DetailView):
    template_name="gestion/detalle_personaje.html"
    model=Personaje
    context_object_name='personaje'


    def get_queryset(self):
        if self.request.user.is_gm:
            queryset=self.model.objects.select_related('usuario', 'raza', 'atributos').prefetch_related('habilidades', 'objetos')
        else:
            queryset=self.model.objects.select_related('usuario', 'raza', 'atributos').prefetch_related('habilidades', 'objetos').filter(usuario=self.request.user)
        return queryset


class ActualizarPersonajeView(GmRequiredMixin, View):
    template_name = 'gestion/actualizar_personaje.html'

    def get_object(self, pk):
        if self.request.user.is_gm:
            return get_object_or_404(
                Personaje.objects.select_related('raza', 'usuario', 'atributos')
                .prefetch_related('habilidades', 'objetos'),
                pk=pk
            )
        return get_object_or_404(
            Personaje.objects.select_related('raza', 'usuario', 'atributos')
            .prefetch_related('habilidades', 'objetos'),
            pk=pk,
            usuario=self.request.user
        )

    def get_context_data(self, request, personaje, form=None, error_msg=None):
        razas = list(Raza.objects.filter(activo=True))
        if personaje.raza and personaje.raza not in razas:
            razas.append(personaje.raza)
        usuarios = User.objects.filter(is_active=True).order_by('username')
        habilidades = list(Habilidad.objects.filter(activo=True))
        objetos = list(Objeto.objects.filter(activo=True))
        
        cantidades_inventario = {}
        bonos = {}
        if personaje.pk:
            cantidades_inventario = {item.objeto_id: item.cantidad for item in personaje.inventarioitem_set.all()}
            for attr in ['fuerza', 'destreza', 'vigor', 'inteligencia', 'percepcion', 'carisma', 'suerte']:
                base = getattr(personaje.atributos, attr, 0) if hasattr(personaje, 'atributos') else 0
                total = personaje.stats_totales.get(attr, base)
                bonos[attr] = total - base

        return {
            'personaje': personaje,
            'form': form or ActualizarPersonajeForm(instance=personaje, request_user=request.user),
            'razas': razas,
            'cantidades_inventario': cantidades_inventario,
            'usuarios': usuarios,
            'habilidades': habilidades,
            'objetos': objetos,
            'bonos': bonos,
            'error_message': error_msg,
        }

    def get(self, request, pk):
        personaje = self.get_object(pk)
        return render(request, self.template_name, self.get_context_data(request, personaje))

    def post(self, request, pk):
        personaje = self.get_object(pk)
        form = ActualizarPersonajeForm(request.POST, instance=personaje, request_user=request.user)

        if form.is_valid():
            form.save()
            return redirect('gm:detalle-personaje', pk=personaje.pk)

        # Extraer el primer error amigable para el banner superior
        error_msg = None
        if form.errors:
            first_err_list = next(iter(form.errors.values()))
            error_msg = first_err_list[0] if first_err_list else "Por favor verifica los campos modificados."

        return render(request, self.template_name, self.get_context_data(request, personaje, form=form, error_msg=error_msg))


class EliminarPersonajeView(GmRequiredMixin, DeleteView):
    model = Personaje
    template_name = "gestion/eliminar_personaje.html"
    context_object_name = "personaje"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Borrado lógico: alternamos el estado
        self.object.activo = not self.object.activo
        self.object.save()
        return redirect('gm:listar-personajes')

# ==========================================
# API DE EQUIPAMIENTO
# ==========================================
class ApiEquiparObjetoView(GmRequiredMixin, View):
    def post(self, request, pk):
        personaje = get_object_or_404(Personaje, pk=pk)
        
        try:
            data = json.loads(request.body)
            objeto_id = data.get('objeto_id')
            accion = data.get('accion') # 'equipar' o 'desequipar'
            
            if not objeto_id or not accion:
                return JsonResponse({"error": "Faltan parámetros (objeto_id, accion)."}, status=400)
                
            objeto = get_object_or_404(Objeto, pk=objeto_id)
            
            # Verificamos si el personaje realmente posee este objeto en su inventario
            if not personaje.objetos.filter(pk=objeto_id).exists():
                return JsonResponse({"error": "El personaje no posee este objeto en su inventario."}, status=403)
                
            tipo = objeto.tipo_equipamiento
            if not tipo:
                return JsonResponse({"error": "Este objeto no es equipable o no tiene un tipo definido."}, status=400)
                
            # Mapeamos el tipo de equipamiento (de la base de datos) a nuestro Slot (ForeignKey)
            mapa_slots = {
                'arma': 'arma_equipada',
                'casco': 'casco_equipado',
                'armadura': 'armadura_equipada',
                'zapatos': 'zapatos_equipados',
                'collar': 'collar_equipado',
                'brazalete': 'brazalete_equipado',
                'escudo': 'escudo_equipado'
            }
            
            # Normalizamos el tipo a minúsculas y quitamos la 's' final si existe (ej. armas -> arma) para ser más tolerantes
            tipo_normalizado = tipo.lower().strip()
            if tipo_normalizado.endswith('s') and tipo_normalizado != 'zapatos':
                tipo_normalizado = tipo_normalizado[:-1]
                
            campo_slot = mapa_slots.get(tipo_normalizado)
            if not campo_slot:
                # Fallback si aún no coincide
                campo_slot = mapa_slots.get(tipo.lower().strip())
                if not campo_slot:
                    return JsonResponse({"error": f"Slot inválido o no reconocido: {tipo}"}, status=500)
                
            if accion == 'equipar':
                setattr(personaje, campo_slot, objeto)
            elif accion == 'desequipar':
                setattr(personaje, campo_slot, None)
            else:
                return JsonResponse({"error": "Acción inválida. Usa 'equipar' o 'desequipar'."}, status=400)
                
            personaje.save()
            return JsonResponse({
                "status": "success",
                "mensaje": f"Objeto {accion}do con éxito en el slot '{tipo}'.",
                "bonificadores_actuales": personaje.obtener_bonificadores_equipo(),
                "stats_totales": personaje.stats_totales,
                "hp_actual": personaje.hp_actual,
                "hp_total": personaje.hp_total,
                "mana_actual": personaje.mana_actual,
                "mana_total": personaje.mana_total,
                "slot_modificado": tipo
            })
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido."}, status=400)


class ApiConsumirObjetoView(GmRequiredMixin, View):
    @transaction.atomic
    def post(self, request, pk):
        personaje = get_object_or_404(Personaje, pk=pk)
        
        try:
            data = json.loads(request.body)
            objeto_id = data.get('objeto_id')
            
            if not objeto_id:
                return JsonResponse({"error": "Falta el ID del objeto a consumir."}, status=400)
                
            objeto = get_object_or_404(Objeto, pk=objeto_id)
            
            if not personaje.objetos.filter(pk=objeto_id).exists():
                return JsonResponse({"error": "El personaje no posee este objeto."}, status=403)
                
            if objeto.es_equipable:
                return JsonResponse({"error": "No puedes consumir un objeto equipable."}, status=400)
                
            # Validar y aplicar efectos
            efectos_aplicados = False
            if objeto.efectos:
                attr = personaje.atributos
                
                # Validación previa eliminada para simplificar. Siempre intenta consumir y aplicar.
                
                for stat, amount in objeto.efectos.items():
                    if stat == 'hp_restore':
                        if personaje.hp_actual < personaje.hp_total:
                            personaje.hp_actual = min(personaje.hp_total, personaje.hp_actual + amount)
                            efectos_aplicados = True
                    elif stat == 'mana_restore':
                        if personaje.mana_actual < personaje.mana_total:
                            personaje.mana_actual = min(personaje.mana_total, personaje.mana_actual + amount)
                            efectos_aplicados = True
                    # Elixires de atributos (cambio permanente)
                    elif hasattr(attr, stat):
                        nuevo_valor = getattr(attr, stat) + amount
                        nuevo_valor = min(nuevo_valor, 999)  # Cap máximo por atributo
                        setattr(attr, stat, nuevo_valor)
                        attr.save()
                        efectos_aplicados = True
                        
                if not efectos_aplicados:
                    # Si no aplicó efectos de stats puros ni restauró porque estaba full, pero es poción, la consume igual o rechaza amigable
                    if 'hp_restore' in objeto.efectos or 'mana_restore' in objeto.efectos:
                        return JsonResponse({"error": "Ya tienes tu vitalidad/maná al máximo."}, status=400)
                    return JsonResponse({"error": "No puedes usar este objeto ahora mismo."}, status=400)
            
            # Consumir el objeto (disminuir cantidad de InventarioItem)
            from ..models.personaje import InventarioItem
            inv_item = get_object_or_404(InventarioItem, personaje=personaje, objeto=objeto)
            
            if inv_item.cantidad > 1:
                inv_item.cantidad -= 1
                inv_item.save()
                cantidad_restante = inv_item.cantidad
            else:
                inv_item.delete()
                cantidad_restante = 0
                
            personaje.save()
            
            return JsonResponse({
                "status": "success",
                "mensaje": f"Has consumido {objeto.nombre}.",
                "hp_actual": personaje.hp_actual,
                "hp_total": personaje.hp_total,
                "mana_actual": personaje.mana_actual,
                "mana_total": personaje.mana_total,
                "stats_totales": personaje.stats_totales,
                "cantidad_restante": cantidad_restante
            })
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido."}, status=400)

# ==========================================
# CRUD DE RAZAS
# ==========================================

class ListarRazasView(GmRequiredMixin, ListView):
    model = Raza
    template_name = "gestion/listar_razas.html"
    context_object_name = "razas"
    paginate_by = 12

    def get_queryset(self):
        qs = Raza.objects.all().order_by('nombre')
        q = self.request.GET.get('q')
        estado = self.request.GET.get('estado', 'todos')
        
        if q:
            qs = qs.filter(nombre__icontains=q)
            
        if estado == 'activos':
            qs = qs.filter(activo=True)
        elif estado == 'deshabilitados':
            qs = qs.filter(activo=False)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['estado'] = self.request.GET.get('estado', 'todos')
        return context

class DetalleRazaView(GmRequiredMixin, DetailView):
    model = Raza
    template_name = "gestion/detalle_raza.html"
    context_object_name = "raza"

class CrearRazaView(GmRequiredMixin, CreateView):
    model = Raza
    form_class = RazaForm
    template_name = "gestion/crear_raza.html"
    success_url = reverse_lazy('gm:listar-razas')

class ActualizarRazaView(GmRequiredMixin, UpdateView):
    model = Raza
    form_class = RazaForm
    template_name = "gestion/actualizar_raza.html"
    
    def get_success_url(self):
        return reverse('gm:detalle-raza', kwargs={'pk': self.object.pk})

class EliminarRazaView(GmRequiredMixin, DeleteView):
    model = Raza
    template_name = "gestion/eliminar_raza.html"
    context_object_name = "raza"
    success_url = reverse_lazy('gm:listar-razas')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Borrado lógico: alternamos el estado
        self.object.activo = not self.object.activo
        self.object.save()
        return redirect(self.success_url)

# --- CRUD Habilidades ---
class ListarHabilidadesView(GmRequiredMixin, ListView):
    model = Habilidad
    template_name = "gestion/listar_habilidades.html"
    context_object_name = "habilidades"
    paginate_by = 12

    def get_queryset(self):
        qs = Habilidad.objects.all().order_by('nombre')
        q = self.request.GET.get('q')
        estado = self.request.GET.get('estado', 'todos')
        
        if q:
            qs = qs.filter(nombre__icontains=q)
            
        if estado == 'activos':
            qs = qs.filter(activo=True)
        elif estado == 'deshabilitados':
            qs = qs.filter(activo=False)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['estado'] = self.request.GET.get('estado', 'todos')
        return context

class DetalleHabilidadView(GmRequiredMixin, DetailView):
    model = Habilidad
    template_name = "gestion/detalle_habilidad.html"
    context_object_name = "habilidad"

class CrearHabilidadView(GmRequiredMixin, CreateView):
    model = Habilidad
    form_class = HabilidadUpdateCreateForm
    template_name = "gestion/crear_habilidad.html"
    success_url = reverse_lazy('gm:listar-habilidades')

class ActualizarHabilidadView(GmRequiredMixin, UpdateView):
    model = Habilidad
    form_class = HabilidadUpdateCreateForm
    template_name = "gestion/actualizar_habilidad.html"
    
    def get_success_url(self):
        return reverse('gm:detalle-habilidad', kwargs={'pk': self.object.pk})

class EliminarHabilidadView(GmRequiredMixin, DeleteView):
    model = Habilidad
    template_name = "gestion/eliminar_habilidad.html"
    context_object_name = "habilidad"
    success_url = reverse_lazy('gm:listar-habilidades')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Borrado lógico: alternamos el estado
        self.object.activo = not self.object.activo
        if not self.object.activo:
            # Si se deshabilita, quitamos la habilidad de todos los personajes
            self.object.personajes.clear()
        self.object.save()
        return redirect(self.success_url)

# --- CRUD Objetos ---
class ListarObjetosView(GmRequiredMixin, ListView):
    model = Objeto
    template_name = "gestion/listar_objetos.html"
    context_object_name = "objetos"
    paginate_by = 12

    def get_queryset(self):
        qs = Objeto.objects.all().order_by('nombre')
        q = self.request.GET.get('q')
        estado = self.request.GET.get('estado', 'todos')
        
        if q:
            qs = qs.filter(nombre__icontains=q)
            
        if estado == 'activos':
            qs = qs.filter(activo=True)
        elif estado == 'deshabilitados':
            qs = qs.filter(activo=False)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['estado'] = self.request.GET.get('estado', 'todos')
        return context

class DetalleObjetoView(GmRequiredMixin, DetailView):
    model = Objeto
    template_name = "gestion/detalle_objeto.html"
    context_object_name = "objeto"

class CrearObjetoView(GmRequiredMixin, CreateView):
    model = Objeto
    form_class = ObjetoUpdateCreateForm
    template_name = "gestion/crear_objeto.html"
    success_url = reverse_lazy('gm:listar-objetos')

class ActualizarObjetoView(GmRequiredMixin, UpdateView):
    model = Objeto
    form_class = ObjetoUpdateCreateForm
    template_name = "gestion/actualizar_objeto.html"
    
    def get_success_url(self):
        return reverse('gm:detalle-objeto', kwargs={'pk': self.object.pk})

class EliminarObjetoView(GmRequiredMixin, DeleteView):
    model = Objeto
    template_name = "gestion/eliminar_objeto.html"
    context_object_name = "objeto"
    success_url = reverse_lazy('gm:listar-objetos')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Borrado lógico: alternamos el estado
        self.object.activo = not self.object.activo
        if not self.object.activo:
            # Si se deshabilita, quitamos el objeto del inventario de todos los personajes
            self.object.personajes.clear()
            
            # Y lo desequipamos por la fuerza de todos los slots donde estuviera equipado
            from ..models.personaje import Personaje
            slots = ['arma_equipada', 'casco_equipado', 'armadura_equipada', 
                     'zapatos_equipados', 'collar_equipado', 'brazalete_equipado', 'escudo_equipado']
            for slot in slots:
                Personaje.objects.filter(**{slot: self.object}).update(**{slot: None})
                
        self.object.save()
        return redirect(self.success_url)
