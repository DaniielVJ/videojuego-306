from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

Usuario = get_user_model()
class CreacionUsuarioForm(UserCreationForm):
    email = forms.EmailField(max_length=100, required=True,
                             widget=forms.EmailInput(attrs={'placeholder': 'jugador@correo.com', 'class': 'input-email'}))
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            "username": forms.TextInput(attrs={'placeholder': 'Cree su username', 'class': 'input-username'}),
            }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = email.lower()

        # Validación A: Bloquear dominios de correo temporal
        dominios_prohibidos = ['@yopmail.com', '@tempmail.com']

        if any(dominio in email for dominio in dominios_prohibidos):
            raise forms.ValidationError("No se permiten correos temporales para registrar cuentas.")

        # Validación B: Comprobar que el correo no exista en la base de datos
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está asociado a otro jugador.")
        return email