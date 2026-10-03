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
