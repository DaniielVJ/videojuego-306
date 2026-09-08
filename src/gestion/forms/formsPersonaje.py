from django import forms
from django.db.models import Q
from src.gestion.models.personaje import Personaje, Habilidad, Atributo
from src.gestion.models.invetario import Objeto

class PersonajeEditCreateFrom(forms.ModelForm):

	poderes = forms.ModelMultipleChoiceField(

		queryset = Habilidad.objects.none(),
		widget = forms.CheckboxSelectMultiple(),
		required = True,
		label = "Poderes (Activas)"

	)

	objetos = forms.ModelChoiceField(

		queryset = Objeto.objects.none(),
		required = True,
		label = "Objeto inicial",
		empty_label = "Selecciona un objeto inicial"

	)

	class Meta:

		model = Personaje
		fields = ["nombre", "raza", "habilidades", "objetos"]
		labels = {"habilidades": "Habilidades (Pasivas)",}
		widgets = {"habilidades": forms.CheckboxSelectMultiple(),}

	def __init__(self, *args, **kwargs):

		self.user = kwargs.pop("user", None)

		super().__init__(*args, **kwargs)

		self.fields["habilidades"].queryset = Habilidad.objects.filter(Q(activo = True) & Q(tipo = "pasiva"))
		self.fields["poderes"].queryset = Habilidad.objects.filter(Q(activo = True) & Q(tipo = "activa"))
		self.fields["objetos"].queryset = Objeto.objects.filter(Q(activo = True))

		if self.instance and self.instance.pk:

			self.fields["poderes"].initial = self.instance.habilidades.filter(Q(activo = True) & Q(tipo = "activa"))

			is_gm = True #Falta agregar como se identifica quien es GM

			if not is_gm:

				del self.fields["habilidades"]
				del self.fields["poderes"]
				del self.fields["objetos"]



	def clean(self):

		cleaned_data = super().clean()

		pasivas = cleaned_data.get("habilidades")
		activas = cleaned_data.get("poderes")
		obj = cleaned_data.get("objetos")

		if pasivas and pasivas.count() != 2:

			self.add_error("habilidades", "Debes elegir exactamente 2 habilidades (pasivas)")

		if activas and activas.count() != 1:

			self.add_error("poderes", "Debes elegir solo un poder (activas)")

		if obj and obj.count() != 1:

			self.add_error("objeto", "Debes elegir solo un objeto")

		return cleaned_data

class AtributosEditCreateForm(forms.ModelForm):

	class Meta:

		model = Atributo
		fields = ["fuerza", "destreza", "vigor", "inteligencia", "percepcion", "carisma", "suerte"]

		widgets = {

			"fuerza": forms.NumberInput(attrs = {"step": "1"}),
			"destreza": forms.NumberInput(attrs = {"step": "1"}),
			"vigor": forms.NumberInput(attrs = {"step": "1"}),
			"inteligencia": forms.NumberInput(attrs = {"step": "1"}),
			"percepcion": forms.NumberInput(attrs = {"step": "1"}),
			"carisma": forms.NumberInput(attrs = {"step": "1"}),
			"suerte": forms.NumberInput(attrs = {"step": "1"}),

		}

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		if self.instance and self.instance.pk:

			c_stat = ["fuerza", "destreza", "vigor", "inteligencia", "percepcion", "carisma", "suerte"]


			for d in c_stat:

				v_a = getattr(self.instance, d)
				self.fields[d].widgets.attrs["min"] = v_a


	def clean(self):

		c_data = super().clean()

		if self.instance and self.instance.pk:

			c_stat = ["fuerza", "destreza", "vigor", "inteligencia", "percepcion", "carisma", "suerte"]

			s_stat = 0

			for d in c_stat:

				n_v = c_data.get(d)
				a_v = getattr(self.instance, d)

				if n_v is not None and n_v < a_v:

					self.add_error(d, f"No se puede reducir el campo {d}")
				
				if n_v is not None and n_v > a_v:
            		
            		s_stat = s_stat + (n_v - a_v)
			
			if(s_stat > self.instance.personaje.ptos_atributos):

				self.add_error(None, f"No puede exceder los puntos de atributos disponible")

		return c_data
