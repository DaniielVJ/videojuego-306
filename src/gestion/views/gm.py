import json


from django.views.generic import ListView, View
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.db import transaction


from src.usuarios.mixins import GmRequiredMixin
from ..models import Personaje, Raza, Atributo, Habilidad


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


from ..forms import CrearPersonajeForm


# View para crear un personaje
class CrearPersonajeView(GmRequiredMixin, View):
    template_name = 'gestion/crear_personaje.html'


    # Implemento mi propio get context data como las view genericas para obtener los datos que mandaremos al template
    def get_context_data(self, request, form=None, error_msg=None):
        razas = list(Raza.objects.filter(activo=True))
        usuarios = User.objects.filter(is_active=True).order_by('username')
        habilidades = Habilidad.objects.filter(activo=True)
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

        return render(request, self.template_name, self._get_context(request, form=form, error_msg=error_msg))

