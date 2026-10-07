from django import forms
from django.db.models import Q
from src.gestion.models.inventario import Objeto

class ObjetoUpdateCreateForm(forms.ModelForm):

	fuerza = forms.IntegerField(required=False, initial=0, min_value=0, label="Fuerza (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	destreza = forms.IntegerField(required=False, initial=0, min_value=0, label="Destreza (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	vigor = forms.IntegerField(required=False, initial=0, min_value=0, label="Vigor (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	inteligencia = forms.IntegerField(required=False, initial=0, min_value=0, label="Inteligencia (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	percepcion = forms.IntegerField(required=False, initial=0, min_value=0, label="Percepcion (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	carisma = forms.IntegerField(required=False, initial=0, min_value=0, label="Carisma (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	suerte = forms.IntegerField(required=False, initial=0, min_value=0, label="Suerte (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	
	hp_restore = forms.IntegerField(required=False, initial=0, min_value=0, label="Restaurar HP (Consumibles)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '1000', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
	mana_restore = forms.IntegerField(required=False, initial=0, min_value=0, label="Restaurar Maná (Consumibles)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '1000', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))

	class Meta:

		model = Objeto
		fields = ["nombre", "descripcion", "peso", "img", "es_equipable", "kit_inicial", "tipo_equipamiento"]

	def clean_nombre(self):
		nombre = self.cleaned_data.get('nombre', '').strip()
		if len(nombre) < 3:
			raise forms.ValidationError("El nombre del objeto debe contener al menos 3 caracteres.")
		qs = Objeto.objects.filter(nombre__iexact=nombre)
		if self.instance and self.instance.pk:
			qs = qs.exclude(pk=self.instance.pk)
		if qs.exists():
			raise forms.ValidationError(f"Ya existe un objeto con el nombre '{nombre}'. Elige otro.")
		return nombre

	def clean_img(self):
		img = self.cleaned_data.get('img')
		if img and getattr(img, 'size', 0) > 10 * 1024 * 1024:
			raise forms.ValidationError("La imagen no puede pesar más de 10 MB.")
		return img

	def clean(self):
		cleaned_data = super().clean()
		es_equipable = cleaned_data.get("es_equipable")
		tipo_equipamiento = cleaned_data.get("tipo_equipamiento")

		if es_equipable and not tipo_equipamiento:
			self.add_error('tipo_equipamiento', "Si el objeto es equipable, debes seleccionar un tipo de equipamiento (Arma, Casco, etc.).")
		
		if not es_equipable and tipo_equipamiento:
			cleaned_data['tipo_equipamiento'] = None
			
		return cleaned_data

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		if self.instance and self.instance.pk and self.instance.efectos:

			efectos = self.instance.efectos

			self.fields["fuerza"].initial = efectos.get("fuerza", 0)
			self.fields["destreza"].initial = efectos.get("destreza", 0)
			self.fields["vigor"].initial = efectos.get("vigor", 0)
			self.fields["inteligencia"].initial = efectos.get("inteligencia", 0)
			self.fields["percepcion"].initial = efectos.get("percepcion", 0)
			self.fields["carisma"].initial = efectos.get("carisma", 0)
			self.fields["suerte"].initial = efectos.get("suerte", 0)
			self.fields["hp_restore"].initial = efectos.get("hp_restore", 0)
			self.fields["mana_restore"].initial = efectos.get("mana_restore", 0)

	def save(self, commit = True):
		# Verificar si es una actualización y hubo cambios críticos en el equipamiento
		cambios_equipamiento = False
		if self.instance and self.instance.pk:
			if 'es_equipable' in self.changed_data or 'tipo_equipamiento' in self.changed_data:
				cambios_equipamiento = True

		instance = super().save(commit = False)

		efectos = {}
		for key in ["fuerza", "destreza", "vigor", "inteligencia", "percepcion", "carisma", "suerte", "hp_restore", "mana_restore"]:
			val = self.cleaned_data.get(key, 0)
			if val != 0:
				efectos[key] = val
		instance.efectos = efectos

		if commit:
			instance.save()
			
			# Desequipar forzosamente si el tipo de objeto cambió para evitar Permalocks
			if cambios_equipamiento:
				from src.gestion.models.personaje import Personaje
				slots = ['arma_equipada', 'casco_equipado', 'armadura_equipada', 
						 'zapatos_equipados', 'collar_equipado', 'brazalete_equipado', 'escudo_equipado']
				for slot in slots:
					Personaje.objects.filter(**{slot: instance}).update(**{slot: None})

		return instance