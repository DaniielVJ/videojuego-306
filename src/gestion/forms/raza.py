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
