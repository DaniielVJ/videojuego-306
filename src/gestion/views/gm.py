from django.views.generic import ListView, View
from django.db.models import Q

from src.usuarios.mixins import GmRequiredMixin
from ..models import Personaje, Raza


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


class CrearPersonajeView(GmRequiredMixin, View):
    pass