from django import forms
from django.db.models import Q
from src.gestion.models.personaje import Habilidad

class HabilidadUpdateCreateForm(forms.ModelForm):

	fuerza = forms.IntegerField(initial = 0, label = "Valor fuerza (puede ser positivo o negativo)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '-100', 'max': '1000', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	destreza = forms.IntegerField(initial = 0, label = "Valor destreza (puede ser positivo o negativo)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '-100', 'max': '1000', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	vigor = forms.IntegerField(initial = 0, label = "Valor vigor (puede ser positivo o negativo)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '-100', 'max': '1000', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	inteligencia = forms.IntegerField(initial = 0, label = "Valor inteligencia (puede ser positivo o negativo)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '-100', 'max': '1000', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	percepcion = forms.IntegerField(initial = 0, label = "Valor percepcion (puede ser positivo o negativo)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '-100', 'max': '1000', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	carisma = forms.IntegerField(initial = 0, label = "Valor carisma (puede ser positivo o negativo)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '-100', 'max': '1000', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	suerte = forms.IntegerField(initial = 0, label = "Valor suerte (puede ser positivo o negativo)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '-100', 'max': '1000', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))

	costo_hp = forms.IntegerField(initial = 0, min_value=0, label = "Costo de HP", widget=forms.NumberInput(attrs={'type': 'range', 'min': '-100', 'max': '1000', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	costo_mana = forms.IntegerField(initial = 0, min_value=0, label = "Costo de Maná", widget=forms.NumberInput(attrs={'type': 'range', 'min': '-100', 'max': '1000', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))

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
				self.fields["fuerza"].initial = efectos.get("fuerza", 0)
				self.fields["destreza"].initial = efectos.get("destreza", 0)
				self.fields["vigor"].initial = efectos.get("vigor", 0)
				self.fields["inteligencia"].initial = efectos.get("inteligencia", 0)
				self.fields["percepcion"].initial = efectos.get("percepcion", 0)
				self.fields["carisma"].initial = efectos.get("carisma", 0)
				self.fields["suerte"].initial = efectos.get("suerte", 0)
			
			if self.instance.costo:
				costo = self.instance.costo
				self.fields["costo_hp"].initial = costo.get("hp", 0)
				self.fields["costo_mana"].initial = costo.get("mana", 0)

	def save(self, commit = True):

		instance = super().save(commit = False)

		efectos = {}
		for key in ["fuerza", "destreza", "vigor", "inteligencia", "percepcion", "carisma", "suerte"]:
			val = self.cleaned_data.get(key, 0)
			if val != 0:
				efectos[key] = val
		instance.efectos = efectos

		instance.costo = {
			"hp": self.cleaned_data.get("costo_hp", 0),
			"mana": self.cleaned_data.get("costo_mana", 0)
		}

		if commit:
			instance.save()

		return instance