from django import forms
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import Q
from ..models.personaje import Personaje, Raza, Habilidad, Atributo, InventarioItem
from ..models import Objeto

User = get_user_model()


class CrearPersonajeForm(forms.ModelForm):
    """
    Formulario de creación de personaje nuevo para el Game Master.
    Valida la identidad del héroe, los 7 atributos numéricos y hasta 2 habilidades.
    Ejecuta el guardado dentro de una transacción atómica.
    """

    # 7 Atributos numéricos para el modelo Atributo
    fuerza = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)
    destreza = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)
    vigor = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)
    inteligencia = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)
    percepcion = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)
    carisma = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)
    suerte = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)

    # Habilidades seleccionadas mediante Drag & Drop (máximo 2)
    habilidades = forms.ModelMultipleChoiceField(
        queryset=Habilidad.objects.none(),
        required=True
    )

    # Objetos de equipamiento seleccionables con checkboxes
    objetos = forms.ModelMultipleChoiceField(
        queryset=Objeto.objects.filter(kit_inicial=True, activo=True),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Personaje
        fields = ['nombre', 'raza', 'usuario']

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_user = request_user

        # Filtrar solo razas, habilidades y objetos activos en el reino
        self.fields['raza'].queryset = Raza.objects.filter(activo=True)
        self.fields['habilidades'].queryset = Habilidad.objects.filter(activo=True, kit_inicial=True)

        # Configurar usuarios activos para asignación del GM
        self.fields['usuario'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['usuario'].required = False

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre del héroe debe contener al menos 3 caracteres.")
        if Personaje.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError(f"Ya existe un guerrero con el nombre '{nombre}'. Elige otro.")
        return nombre

    def clean_habilidades(self):
        habilidades = self.cleaned_data.get('habilidades')
        if habilidades.count() != 2:
            raise forms.ValidationError("Debes seleccionar exactamente 2 habilidades")
        return habilidades


    def clean_objetos(self):
        objetos = self.cleaned_data.get('objetos')
        if objetos.count() != 2:
            raise forms.ValidationError("Debes seleccionar exactamente 2 objetos")
        return objetos
    

    def clean(self):
        puntos_base = 20
        cleaned_data = super().clean()
        atributos = (cleaned_data.get('fuerza'), cleaned_data.get('destreza'), cleaned_data.get('vigor'), 
        cleaned_data.get('inteligencia'), cleaned_data.get('percepcion'), cleaned_data.get('carisma'), cleaned_data.get('suerte'))

    
        # La suma de los atributos no pueden dar un valor diferente a 20 ya que debe asignar todos los atributos ni mas ni menos.
        if puntos_base != sum(atributo for atributo in atributos if atributo != None):
            raise forms.ValidationError("Debes otorgar todos los puntos que se te dio")
        return cleaned_data



        
    def save(self, commit=True):
        """
        Crea el Personaje, sus Atributos asociados y vincula las Habilidades
        dentro de una transacción atómica para garantizar integridad absoluta.
        """
        with transaction.atomic():
            personaje = super().save(commit=False)

            # Asignar usuario si no se seleccionó explícitamente
            if not personaje.usuario_id and self.request_user:
                personaje.usuario = self.request_user

            personaje.nivel = 1
            personaje.experiencia = 0
            personaje.exp_siguiente_nivel = 100
            personaje.estado = Personaje.Estado.VIVO
            personaje.activo = True

            if commit:
                personaje.save()

                # 1. Crear el registro OneToOne de Atributo
                Atributo.objects.create(
                    personaje=personaje,
                    fuerza=self.cleaned_data.get('fuerza', 0),
                    destreza=self.cleaned_data.get('destreza', 0),
                    vigor=self.cleaned_data.get('vigor', 0),
                    inteligencia=self.cleaned_data.get('inteligencia', 0),
                    percepcion=self.cleaned_data.get('percepcion', 0),
                    carisma=self.cleaned_data.get('carisma', 0),
                    suerte=self.cleaned_data.get('suerte', 0),
                )

                # 2. Asociar habilidades Many-to-Many mediante .add()
                habilidades = self.cleaned_data.get('habilidades')
                if habilidades:
                    personaje.habilidades.add(*habilidades)

                # 3. Asociar objetos de inventario seleccionados
                objetos = self.cleaned_data.get('objetos')
                if objetos:
                    for obj in objetos:
                        InventarioItem.objects.create(personaje=personaje, objeto=obj, cantidad=1)

        return personaje



class ActualizarPersonajeForm(forms.ModelForm):
    """
    Formulario de actualización y modificación de personaje para el Game Master.
    Permite modificar identidad, estado, nivel, experiencia, los 7 atributos
    numéricos del modelo Atributo, habilidades y objetos del inventario.
    """

    # 7 Atributos numéricos para el modelo Atributo
    fuerza = forms.IntegerField(min_value=0, required=True)
    destreza = forms.IntegerField(min_value=0, required=True)
    vigor = forms.IntegerField(min_value=0, required=True)
    inteligencia = forms.IntegerField(min_value=0, required=True)
    percepcion = forms.IntegerField(min_value=0, required=True)
    carisma = forms.IntegerField(min_value=0, required=True)
    suerte = forms.IntegerField(min_value=0, required=True)

    # Habilidades seleccionables mediante checkboxes
    habilidades = forms.ModelMultipleChoiceField(
        queryset=Habilidad.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    # Objetos de equipamiento seleccionables mediante checkboxes
    objetos = forms.ModelMultipleChoiceField(
        queryset=Objeto.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Personaje
        fields = [
            'nombre', 'raza', 'usuario', 'estado',
            'nivel', 'experiencia', 'exp_siguiente_nivel', 'activo'
        ]

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_user = request_user

        # Filtrar solo razas, habilidades y objetos activos en el reino
        if self.instance and self.instance.pk and self.instance.raza and not self.instance.raza.activo:
            self.fields['raza'].queryset = Raza.objects.filter(Q(activo=True) | Q(pk=self.instance.raza.pk))
        else:
            self.fields['raza'].queryset = Raza.objects.filter(activo=True)
            
        self.fields['habilidades'].queryset = Habilidad.objects.filter(activo=True)
        self.fields['objetos'].queryset = Objeto.objects.filter(activo=True)

        # Configurar usuarios activos para reasignación
        self.fields['usuario'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['usuario'].required = False

        # Si hay instancia existente, pre-cargar los 7 atributos numéricos
        if self.instance and self.instance.pk:
            if hasattr(self.instance, 'atributos') and self.instance.atributos:
                self.fields['fuerza'].initial = self.instance.atributos.fuerza
                self.fields['destreza'].initial = self.instance.atributos.destreza
                self.fields['vigor'].initial = self.instance.atributos.vigor
                self.fields['inteligencia'].initial = self.instance.atributos.inteligencia
                self.fields['percepcion'].initial = self.instance.atributos.percepcion
                self.fields['carisma'].initial = self.instance.atributos.carisma
                self.fields['suerte'].initial = self.instance.atributos.suerte

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre del héroe debe contener al menos 3 caracteres.")
        qs = Personaje.objects.filter(nombre__iexact=nombre)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Ya existe un guerrero con el nombre '{nombre}'. Elige otro.")
        return nombre

    def save(self, commit=True):
        """
        Guarda los cambios del personaje y actualiza o crea sus atributos
        asociados dentro de una transacción atómica.
        """
        with transaction.atomic():
            personaje = super().save(commit=commit)

            # Extraer valores de los 7 atributos
            fuerza = self.cleaned_data.get('fuerza', 0)
            destreza = self.cleaned_data.get('destreza', 0)
            vigor = self.cleaned_data.get('vigor', 0)
            inteligencia = self.cleaned_data.get('inteligencia', 0)
            percepcion = self.cleaned_data.get('percepcion', 0)
            carisma = self.cleaned_data.get('carisma', 0)
            suerte = self.cleaned_data.get('suerte', 0)

            # Actualizar o crear registro OneToOne de Atributo
            if hasattr(personaje, 'atributos') and personaje.atributos:
                atributo = personaje.atributos
                atributo.fuerza = fuerza
                atributo.destreza = destreza
                atributo.vigor = vigor
                atributo.inteligencia = inteligencia
                atributo.percepcion = percepcion
                atributo.carisma = carisma
                atributo.suerte = suerte
                if commit:
                    atributo.save()
            else:
                if commit:
                    Atributo.objects.create(
                        personaje=personaje,
                        fuerza=fuerza,
                        destreza=destreza,
                        vigor=vigor,
                        inteligencia=inteligencia,
                        percepcion=percepcion,
                        carisma=carisma,
                        suerte=suerte,
                    )

            # Actualizar Habilidades (many-to-many sin through)
            habilidades = self.cleaned_data.get('habilidades')
            if habilidades is not None:
                personaje.habilidades.set(habilidades)

            # Actualizar Objetos (many-to-many con through InventarioItem)
            objetos_seleccionados = self.cleaned_data.get('objetos')
            if objetos_seleccionados is not None:
                # Eliminar los que ya no están seleccionados y desequiparlos si estaban puestos
                items_a_eliminar = InventarioItem.objects.filter(personaje=personaje).exclude(objeto__in=objetos_seleccionados)
                objetos_a_eliminar = [item.objeto for item in items_a_eliminar]
                
                slots = ['arma_equipada', 'casco_equipado', 'armadura_equipada', 
                         'zapatos_equipados', 'collar_equipado', 'brazalete_equipado', 'escudo_equipado']
                personaje_modificado = False
                for obj in objetos_a_eliminar:
                    for slot in slots:
                        if getattr(personaje, slot) == obj:
                            setattr(personaje, slot, None)
                            personaje_modificado = True
                            
                if personaje_modificado and commit:
                    personaje.save()
                
                items_a_eliminar.delete()
                # Asegurar que los seleccionados existan con cantidad=1 por defecto si son nuevos
                for obj in objetos_seleccionados:
                    # Intentar obtener la cantidad enviada en el form, por defecto 1
                    try:
                        qty = int(self.data.get(f'cantidad_{obj.pk}', 1))
                    except (ValueError, TypeError):
                        qty = 1
                    if qty < 1:
                        qty = 1
                        
                    InventarioItem.objects.update_or_create(
                        personaje=personaje, 
                        objeto=obj, 
                        defaults={'cantidad': qty}
                    )

        return personaje
class CrearPersonajePlayerForm(forms.ModelForm):
    """
    Formulario de creación de personaje nuevo para el Jugador.
    No permite elegir usuario, se le asignará al que hace la request.
    """

    # 7 Atributos numéricos para el modelo Atributo
    fuerza = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)
    destreza = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)
    vigor = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)
    inteligencia = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)
    percepcion = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)
    carisma = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)
    suerte = forms.IntegerField(min_value=0, max_value=1000, initial=0, required=True)

    # Habilidades seleccionadas mediante Drag & Drop (máximo 2)
    habilidades = forms.ModelMultipleChoiceField(
        queryset=Habilidad.objects.none(),
        required=True
    )

    # Objetos de equipamiento seleccionables con checkboxes
    objetos = forms.ModelMultipleChoiceField(
        queryset=Objeto.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Personaje
        fields = ['nombre', 'raza']

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_user = request_user

        # Filtrar solo razas, habilidades y objetos activos en el reino
        self.fields['raza'].queryset = Raza.objects.filter(activo=True)
        self.fields['habilidades'].queryset = Habilidad.objects.filter(activo=True, kit_inicial=True)
        self.fields['objetos'].queryset = Objeto.objects.filter(activo=True, kit_inicial=True)


    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre del héroe debe contener al menos 3 caracteres.")
        if Personaje.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError(f"Ya existe un guerrero con el nombre '{nombre}'. Elige otro.")
        return nombre

    def clean_habilidades(self):
        habilidades = self.cleaned_data.get('habilidades')
        if habilidades.count() != 2:
            raise forms.ValidationError("Debes seleccionar exactamente 2 habilidades")
        return habilidades


    def clean_objetos(self):
        objetos = self.cleaned_data.get('objetos')
        if objetos.count() != 2:
            raise forms.ValidationError("Debes seleccionar exactamente 2 objetos")
        return objetos
    

    def clean(self):
        puntos_base = 20
        cleaned_data = super().clean()
        atributos = (cleaned_data.get('fuerza'), cleaned_data.get('destreza'), cleaned_data.get('vigor'), 
        cleaned_data.get('inteligencia'), cleaned_data.get('percepcion'), cleaned_data.get('carisma'), cleaned_data.get('suerte'))

    
        # La suma de los atributos no pueden dar un valor diferente a 20
        if puntos_base != sum(atributo for atributo in atributos if atributo != None):
            raise forms.ValidationError("Debes otorgar todos los puntos que se te dio")
        return cleaned_data


    def save(self, commit=True):
        """
        Crea el Personaje asignándolo forzosamente al usuario de la request.
        """
        with transaction.atomic():
            personaje = super().save(commit=False)

            # Forzamos el dueño del personaje al usuario actual
            if self.request_user:
                personaje.usuario = self.request_user

            personaje.nivel = 1
            personaje.experiencia = 0
            personaje.exp_siguiente_nivel = 100
            personaje.estado = Personaje.Estado.VIVO
            personaje.activo = True

            if commit:
                personaje.save()

                # 1. Crear el registro OneToOne de Atributo
                Atributo.objects.create(
                    personaje=personaje,
                    fuerza=self.cleaned_data.get('fuerza', 0),
                    destreza=self.cleaned_data.get('destreza', 0),
                    vigor=self.cleaned_data.get('vigor', 0),
                    inteligencia=self.cleaned_data.get('inteligencia', 0),
                    percepcion=self.cleaned_data.get('percepcion', 0),
                    carisma=self.cleaned_data.get('carisma', 0),
                    suerte=self.cleaned_data.get('suerte', 0),
                )

                # 2. Asociar habilidades Many-to-Many mediante .add()
                habilidades = self.cleaned_data.get('habilidades')
                if habilidades:
                    personaje.habilidades.add(*habilidades)

                # 3. Asociar objetos de inventario seleccionados
                objetos = self.cleaned_data.get('objetos')
                if objetos:
                    for obj in objetos:
                        InventarioItem.objects.create(personaje=personaje, objeto=obj, cantidad=1)

        return personaje

class ActualizarPersonajePlayerForm(forms.ModelForm):
    """
    Formulario de actualización de personaje para el Jugador.
    Solo permite modificar el nombre del héroe.
    """
    class Meta:
        model = Personaje
        fields = ['nombre']

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre del héroe debe contener al menos 3 caracteres.")
        
        # Verificar que el nombre no esté en uso por otro personaje (excluyendo el actual)
        # self.instance representa el objeto actual
        if Personaje.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(f"Ya existe un guerrero con el nombre '{nombre}'. Elige otro.")
        return nombre
