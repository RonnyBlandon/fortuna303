from django import forms


class ContactForm(forms.Form):
    # Campos de las contraseña para el formulario de registro de usuario
    name = forms.CharField(
        required = True,
    	widget = forms.TextInput(
            attrs= {
                'class': 'form__input--size', 
                'placeholder': 'Nombre'
            }
        )
    )
    last_name = forms.CharField(
        required = True,
    	widget = forms.TextInput(
            attrs= {
                'class': 'form__input--size', 
                'placeholder': 'Apellido'
            }
        )
    )
    email = forms.CharField(
        required = True,
    	widget = forms.EmailInput(
            attrs= {
                'class': 'form__input', 
                'placeholder': 'Correo Electrónico'
            }
        )
    )
    affair = forms.CharField(
        required = True,
    	widget = forms.TextInput(
            attrs= {
                'class': 'form__input', 
                'placeholder': 'Asunto'
            }
        )
    )
    message = forms.CharField(
        required = True,
    	widget = forms.Textarea(
            attrs= {
                'class': 'form__input', 
                'placeholder': 'Mensaje'
            }
        )
    )
    