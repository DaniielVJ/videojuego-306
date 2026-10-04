from django import forms
from django.db.models import Q
from src.gestion.models.personaje import Habilidad

class HabilidadUpdateCreateForm(forms.ModelForm):

	v_fuerza = forms.IntegerField(initial = 0, label = "Valor fuerza (puede ser positivo o negativo)")
	v_destreza = forms.IntegerField(initial = 0, label = "Valor destreza (puede ser positivo o negativo)")
	v_vigor = forms.IntegerField(initial = 0, label = "Valor vigor (puede ser positivo o negativo)")
	v_inteligencia = forms.IntegerField(initial = 0, label = "Valor inteligencia (puede ser positivo o negativo)")
	v_percepcion = forms.IntegerField(initial = 0, label = "Valor percepcion (puede ser positivo o negativo)")
	v_carisma = forms.IntegerField(initial = 0, label = "Valor carisma (puede ser positivo o negativo)")
	v_suerte = forms.IntegerField(initial = 0, label = "Valor suerte (puede ser positivo o negativo)")

	costo_hp = forms.IntegerField(initial = 0, min_value=0, label = "Costo de HP")
	costo_mana = forms.IntegerField(initial = 0, min_value=0, label = "Costo de Maná")

	class Meta:
		model = Habilidad
		fields = ["nombre", "descripcion", "kit_inicial"]

	def clean_nombre(self):
		nombre = self.cleaned_data.get('nombre', '').strip()
		if len(nombre) < 3:
			raise forms.ValidationError("El nombre de la habilidad debe contener al menos 3 caracteres.")
		qs = Habilidad.objects.filter(nombre__iexact=nombre)
		if self.instance and self.instance.pk:
			qs = qs.exclude(pk=self.instance.pk)
		if qs.exists():
			raise forms.ValidationError(f"Ya existe una habilidad con el nombre '{nombre}'. Elige otro.")
		return nombre

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		if self.instance and self.instance.pk:
			if self.instance.efectos:
				efectos = self.instance.efectos
				self.fields["v_fuerza"].initial = efectos.get("v_fuerza", 0)
				self.fields["v_destreza"].initial = efectos.get("v_destreza", 0)
				self.fields["v_vigor"].initial = efectos.get("v_vigor", 0)
				self.fields["v_inteligencia"].initial = efectos.get("v_inteligencia", 0)
				self.fields["v_percepcion"].initial = efectos.get("v_percepcion", 0)
				self.fields["v_carisma"].initial = efectos.get("v_carisma", 0)
				self.fields["v_suerte"].initial = efectos.get("v_suerte", 0)
			
			if self.instance.costo:
				costo = self.instance.costo
				self.fields["costo_hp"].initial = costo.get("hp", 0)
				self.fields["costo_mana"].initial = costo.get("mana", 0)

	def save(self, commit = True):

		instance = super().save(commit = False)

		instance.efectos = {

			"v_fuerza": self.cleaned_data.get("v_fuerza", 0),
			"v_destreza": self.cleaned_data.get("v_destreza", 0),
			"v_vigor": self.cleaned_data.get("v_vigor", 0),
			"v_inteligencia": self.cleaned_data.get("v_inteligencia", 0),
			"v_percepcion": self.cleaned_data.get("v_percepcion", 0),
			"v_carisma": self.cleaned_data.get("v_carisma", 0),
			"v_suerte": self.cleaned_data.get("v_suerte", 0),

		}

		instance.costo = {
			"hp": self.cleaned_data.get("costo_hp", 0),
			"mana": self.cleaned_data.get("costo_mana", 0)
		}

		if commit:
			instance.save()

		return instance