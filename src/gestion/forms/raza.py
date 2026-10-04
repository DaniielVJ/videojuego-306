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

    b_fuerza = forms.IntegerField(initial = 0, label = "Bonificador/Handicap Fuerza (+/-)")
    b_destreza = forms.IntegerField(initial = 0, label = "Bonificador/Handicap Destreza (+/-)")
    b_vigor = forms.IntegerField(initial = 0, label = "Bonificador/Handicap Vigor (+/-)")
    b_inteligencia = forms.IntegerField(initial = 0, label = "Bonificador/Handicap Inteligencia (+/-)")
    b_percepcion = forms.IntegerField(initial = 0, label = "Bonificador/Handicap Percepcion (+/-)")
    b_carisma = forms.IntegerField(initial = 0, label = "Bonificador/Handicap Carisma (+/-)")
    b_suerte = forms.IntegerField(initial = 0, label = "Bonificador/Handicap Suerte (+/-)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            bon = self.instance.r_bonificadores or {}
            han = self.instance.r_handicap or {}
            
            for attr in ['fuerza', 'destreza', 'vigor', 'inteligencia', 'percepcion', 'carisma', 'suerte']:
                # Calculate net bonus: bonificador - handicap
                b_val = bon.get(attr, 0)
                h_val = han.get(attr, 0)
                self.fields[f"b_{attr}"].initial = b_val - h_val

    def save(self, commit=True):
        instance = super().save(commit=False)
        bonificadores = {}
        handicap = {}
        
        for attr in ['fuerza', 'destreza', 'vigor', 'inteligencia', 'percepcion', 'carisma', 'suerte']:
            val = self.cleaned_data.get(f"b_{attr}", 0)
            if val > 0:
                bonificadores[attr] = val
                handicap[attr] = 0
            elif val < 0:
                bonificadores[attr] = 0
                handicap[attr] = abs(val)
            else:
                bonificadores[attr] = 0
                handicap[attr] = 0
                
        instance.r_bonificadores = bonificadores
        instance.r_handicap = handicap
        
        if commit:
            instance.save()
        return instance
