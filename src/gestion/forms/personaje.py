from django import forms
from django.db import transaction
from django.contrib.auth import get_user_model
from ..models.personaje import Personaje, Raza, Habilidad, Atributo

User = get_user_model()


class CrearPersonajeForm(forms.ModelForm):
    """
    Formulario de creación de personaje nuevo para el Game Master.
    Valida la identidad del héroe, los 7 atributos numéricos y hasta 2 habilidades.
    Ejecuta el guardado dentro de una transacción atómica.
    """

    # 7 Atributos numéricos para el modelo Atributo
    fuerza = forms.IntegerField(min_value=1, max_value=100, initial=5, required=True)
    destreza = forms.IntegerField(min_value=1, max_value=100, initial=5, required=True)
    vigor = forms.IntegerField(min_value=1, max_value=100, initial=5, required=True)
    inteligencia = forms.IntegerField(min_value=1, max_value=100, initial=5, required=True)
    percepcion = forms.IntegerField(min_value=1, max_value=100, initial=5, required=True)
    carisma = forms.IntegerField(min_value=1, max_value=100, initial=5, required=True)
    suerte = forms.IntegerField(min_value=1, max_value=100, initial=5, required=True)

    # Habilidades seleccionadas mediante Drag & Drop (máximo 2)
    habilidades = forms.ModelMultipleChoiceField(
        queryset=Habilidad.objects.none(),
        required=False
    )

    class Meta:
        model = Personaje
        fields = ['nombre', 'raza', 'usuario']

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_user = request_user

        # Filtrar solo razas y habilidades activas en el reino
        self.fields['raza'].queryset = Raza.objects.filter(activo=True)
        self.fields['habilidades'].queryset = Habilidad.objects.filter(activo=True)

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
        if habilidades and habilidades.count() > 2:
            raise forms.ValidationError("No puedes asignar más de 2 habilidades iniciales al personaje.")
        return habilidades

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
                    fuerza=self.cleaned_data['fuerza'],
                    destreza=self.cleaned_data['destreza'],
                    vigor=self.cleaned_data['vigor'],
                    inteligencia=self.cleaned_data['inteligencia'],
                    percepcion=self.cleaned_data['percepcion'],
                    carisma=self.cleaned_data['carisma'],
                    suerte=self.cleaned_data['suerte'],
                )

                # 2. Asociar habilidades Many-to-Many mediante .add()
                habilidades = self.cleaned_data.get('habilidades')
                if habilidades:
                    personaje.habilidades.add(*habilidades)

        return personaje
