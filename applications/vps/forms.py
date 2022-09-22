from django import forms

# models
from .models import AccountMt5

class CreateAccountMt5Form(forms.ModelForm):
    class Meta:
        model = AccountMt5
        fields = ('login', 'password', 'server')
        widgets = {
            'login': forms.NumberInput(
                attrs={'class': 'form-register__input', 'placeholder': 'Usuario'}
            ),
            'password': forms.TextInput(
                attrs={'class': 'form-register__input', 'placeholder': 'Contraseña'}
            ),
            'server': forms.TextInput(
                attrs={'class': 'form-register__input', 'placeholder': 'Servidor'}
            )
        }
        