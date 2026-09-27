from django import forms
from django.db.models import Q
from src.gestion.models.personaje import Raza

class RazaUpdateCreateForm(forms.ModelForm):

	v_fuerza = forms.IntegerField(initial = 0, label = "Valor fuerza (puede ser positivo o negativo)")
	v_destreza = forms.IntegerField(initial = 0, label = "Valor destreza (puede ser positivo o negativo)")
	v_vigor = forms.IntegerField(initial = 0, label = "Valor vigor (puede ser positivo o negativo)")
	v_inteligencia = forms.IntegerField(initial = 0, label = "Valor inteligencia (puede ser positivo o negativo)")
	v_percepcion = forms.IntegerField(initial = 0, label = "Valor percepcion (puede ser positivo o negativo)")
	v_carisma = forms.IntegerField(initial = 0, label = "Valor carisma (puede ser positivo o negativo)")
	v_suerte = forms.IntegerField(initial = 0, label = "Valor suerte (puede ser positivo o negativo)")

	class Meta:

		model = Raza
		fields = ["nombre", "descripcion"]

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		if self.instance and self.instance.pk and self.instance.propiedades:

			props = self.instance.propiedades
			
			self.fields["v_fuerza"].initial = props.get("v_fuerza", 0)
			self.fields["v_destreza"].initial = props.get("v_destreza", 0)
			self.fields["v_vigor"].initial = props.get("v_vigor", 0)
			self.fields["v_inteligencia"].initial = props.get("v_inteligencia", 0)
			self.fields["v_percepcion"].initial = props.get("v_percepcion", 0)
			self.fields["v_carisma"].initial = props.get("v_carisma", 0)
			self.fields["v_suerte"].initial = props.get("v_suerte", 0)

		

	def save(self, commit = True):

		instance = super().save(commit = False)

		instance.propiedades = {

			"v_fuerza": self.cleaned_data.get("v_fuerza", 0),
			"v_destreza": self.cleaned_data.get("v_destreza", 0),
			"v_vigor": self.cleaned_data.get("v_vigor", 0),
			"v_inteligencia": self.cleaned_data.get("v_inteligencia", 0),
			"v_percepcion": self.cleaned_data.get("v_percepcion", 0),
			"v_carisma": self.cleaned_data.get("v_carisma", 0),
			"v_suerte": self.cleaned_data.get("v_suerte", 0),
		}

		if commit:

			instance.save()

		return instance
