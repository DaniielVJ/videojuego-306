import json
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, View, DetailView, UpdateView, DeleteView, CreateView
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model


from src.usuarios.mixins import GmRequiredMixin
from ..models import Personaje, Raza, Atributo, Habilidad, Objeto
from ..forms import CrearPersonajeForm, ActualizarPersonajeForm
from ..forms.raza import RazaForm
from ..forms.habilidad import HabilidadUpdateCreateForm

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
        habilidades = Habilidad.objects.filter(activo=True)
        objetos = Objeto.objects.filter(kit_inicial=True, activo=True)
        razas_json = [
            {
                'id': r.id,
                'nombre': r.nombre,
                'descripcion': r.descripcion,
                'bonificadores': r.r_bonificadores or {},
                'handicap': r.r_handicap or {},
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


class DetallePersonajeView(DetailView):
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

        return {
            'personaje': personaje,
            'form': form or ActualizarPersonajeForm(instance=personaje, request_user=request.user),
            'razas': razas,
            'usuarios': usuarios,
            'habilidades': habilidades,
            'objetos': objetos,
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
# CRUD DE RAZAS
# ==========================================

class ListarRazasView(GmRequiredMixin, ListView):
    model = Raza
    template_name = "gestion/listar_razas.html"
    context_object_name = "razas"

    def get_queryset(self):
        return Raza.objects.all()

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
        return Habilidad.objects.all().order_by('nombre')

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
