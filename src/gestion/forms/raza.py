from django import forms
from ..models.personaje import Raza

class RazaForm(forms.ModelForm):
    class Meta:
        model = Raza
        fields = ['nombre', 'descripcion', 'img_body', 'img_head']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre de la raza debe contener al menos 3 caracteres.")
        return nombre

    def clean_img_body(self):
        img = self.cleaned_data.get('img_body')
        if img and getattr(img, 'size', 0) > 10 * 1024 * 1024:
            raise forms.ValidationError("La imagen no puede pesar más de 10 MB.")
        return img

    def clean_img_head(self):
        img = self.cleaned_data.get('img_head')
        if img and getattr(img, 'size', 0) > 10 * 1024 * 1024:
            raise forms.ValidationError("La imagen no puede pesar más de 10 MB.")
        return img

    b_fuerza = forms.IntegerField(required=False, initial=0, min_value=0, label="Bonificador Fuerza (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
    b_destreza = forms.IntegerField(required=False, initial=0, min_value=0, label="Bonificador Destreza (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
    b_vigor = forms.IntegerField(required=False, initial=0, min_value=0, label="Bonificador Vigor (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
    b_inteligencia = forms.IntegerField(required=False, initial=0, min_value=0, label="Bonificador Inteligencia (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
    b_percepcion = forms.IntegerField(required=False, initial=0, min_value=0, label="Bonificador Percepcion (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
    b_carisma = forms.IntegerField(required=False, initial=0, min_value=0, label="Bonificador Carisma (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))
    b_suerte = forms.IntegerField(required=False, initial=0, min_value=0, label="Bonificador Suerte (+)", widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100', 'class': 'stat-slider', 'oninput': 'this.nextElementSibling.innerText = this.value'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            bon = self.instance.r_bonificadores or {}
            
            for attr in ['fuerza', 'destreza', 'vigor', 'inteligencia', 'percepcion', 'carisma', 'suerte']:
                self.fields[f"b_{attr}"].initial = bon.get(attr, 0)

    def save(self, commit=True):
        instance = super().save(commit=False)
        bonificadores = {}
        
        for attr in ['fuerza', 'destreza', 'vigor', 'inteligencia', 'percepcion', 'carisma', 'suerte']:
            val = self.cleaned_data.get(f"b_{attr}", 0)
            if val != 0:
                bonificadores[attr] = val
                
        instance.r_bonificadores = bonificadores
        
        if commit:
            instance.save()
        return instance
