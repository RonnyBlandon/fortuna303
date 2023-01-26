from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
# Importar modelos de la app users
from .models import User

# Formulario de Registro de usuario
class UserRegisterForm(forms.ModelForm):
    # Campos de las contraseña para el formulario de registro de usuario
    password1 = forms.CharField(
        required = True,
    	widget = forms.PasswordInput(
            attrs= {
                'class': 'form-register__input', 
                'placeholder': 'Contraseña'
            }
        )
    )

    password2 = forms.CharField(
        required = True,
    	widget = forms.PasswordInput(
            attrs= {
                'class': 'form-register__input', 
                'placeholder': 'Repetir Contraseña'
            }
        )
    )
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    #captcha = ReCaptchaField(widget=ReCaptchaV3)
    # clases Meta del formulario
    class Meta:
        model = User
        fields = [
            'name',
            'last_name',
            'email',
        ]
        widgets = {'name': forms.TextInput(
            attrs = {'class': 'form-register__input', 'placeholder': 'Nombre'}
        ),
        'last_name': forms.TextInput(
            attrs = {'class': 'form-register__input', 'placeholder': 'Apellido'}
        ),
        'email': forms.EmailInput(
            attrs = {'class': 'form-register__input', 'placeholder': 'Correo Electronico'}
        )}
    
    # Validacion de las contraseñas al crear usuario
    def validate_password(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        espacio = False
        minuscula = False
        mayuscula = False
        numeros = False

        for c in password1:
            if c.isspace():
                espacio = True
            if c.islower():
                minuscula = True
            if c.isupper():
                mayuscula = True
            if c.isnumeric():
                numeros = True

        if password1 != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        if len(password1) < 8:
            self.add_error('password2', 'La contraseña debe contener al menos 8 caracteres.')
        if espacio == True:
            self.add_error('password2', 'La contraseña no debe contener espacios.')
        if minuscula == False:
            self.add_error('password2', 'La contraseña debe contener al menos una letra minúscula.')
        if mayuscula == False:
            self.add_error('password2', 'La contraseña debe contener al menos una letra mayúscula.')
        if numeros == False:
            self.add_error('password2', 'La contraseña debe contener al menos un numero.')
    
    def clean(self):
        # Validando si existe ya el correo electronico en la base de datos
        email = self.cleaned_data['email']
        email_exists = User.objects.email_exists(email)
        if email_exists:
            self.add_error('email', 'Ya existe una cuenta con este correo electrónico.')

        UserRegisterForm.validate_password(self)

    
# Formulario de Inicio de Sesión
class UserLoginForm(forms.Form):

    email = forms.CharField(
        required = True,
        widget = forms.EmailInput(
            attrs= {
                'class': 'form-register__input', 
                'placeholder': 'Correo Electronico'
            }
        )
    )

    password = forms.CharField(
        required = True,
        widget = forms.PasswordInput(
            attrs= {
                'class': 'form-register__input', 
                'placeholder': 'Contraseña'
            }
        )
    )


    """ la funcion llamada clean es la primera validacion que hace django en un form por eso es que cada
    funcion que sea para validar datos de un formulario debe tener el nombre "clean"  o "clean_Filename "
    """

    # Validacion del correo y contraseña del usuario para el inicio de sesión
    def clean(self):
        cleaned_data = super(UserLoginForm, self).clean()
        email = cleaned_data['email']
        password = cleaned_data['password']

        if not authenticate(email=email, password=password):
            raise forms.ValidationError('Los datos de ususario no son correctos.')

        return self.cleaned_data


class UpdatePasswordForm(forms.Form):
    password1 = forms.CharField(
        required = True,
        widget = forms.PasswordInput(
            attrs= {
                'class': 'form-register__input',
                'placeholder': 'Contraseña Nueva'
            }
        )
    )
    password2 = forms.CharField(
        required = True,
        widget = forms.PasswordInput(
            attrs= {
                'class': 'form-register__input',
                'placeholder': ' Repetir Contraseña Nueva'
            }
        )
    )
    password3 = forms.CharField(
        required = True,
        widget = forms.PasswordInput(
            attrs= {
                'class': 'form-register__input',
                'placeholder': 'Contraseña Vieja'
            }
        )
    )

    # Reescribimos la funcion __init__ para pasarle el email de usuario al formulario desde el view
    def __init__(self, email, *args, **kwargs):
        self.email = email
        super(UpdatePasswordForm, self).__init__(*args, **kwargs)

    # Validacion de las contraseñas para el cambio de las mismas
    def clean(self):
        password3 = self.cleaned_data['password3']
        
        # recuperamos el password vieja del usuario y verificamos su vieja contrtaseña sea correcta
        user = User.objects.get(email=self.email)
        if not check_password(password3, user.password):
            raise forms.ValidationError('La contraseña vieja no es correcta.')

        # Validando los passwords
        UserRegisterForm.validate_password(self)


class VerificationForm(forms.Form):
    validation_code = forms.CharField(
        max_length=6, 
        required=True,
        widget= forms.TextInput(
            attrs={'class': 'form-register__input', 'placeholder': 'Código Verificación'}
        )
    )

    # Reescribimos la funcion __init__ para pasarle el pk al formulario desde el view
    def __init__(self, pk, *args, **kwargs):
        self.id_user = pk
        super(VerificationForm, self).__init__(*args, **kwargs)

    def clean(self):
        codigo = self.cleaned_data['validation_code']

        if len(codigo) == 6:
            # verificamos si el codigo y el id del usuario son validos:
            activo = User.objects.cod_validation(
                self.id_user,
                codigo
            )
            if not activo:
                raise forms.ValidationError('El codigo es incorrecto')
        else:
            raise forms.ValidationError('El codigo es incorrecto')


class EmailPasswordForm(forms.Form):
    email = forms.CharField( 
        required=True,
        widget= forms.EmailInput(
            attrs={'class': 'form-register__input', 'placeholder': 'Correo Electrónico'}
        )
    )

    def clean(self):
        email = self.cleaned_data['email']
        print("Esto es lo que me recupera el self.cleaned_data['email'] en forms.py: ", email)
        user = User.objects.email_exists(email)

        if not user:
            raise forms.ValidationError('Ningún usuario está ligado a este correo.')


class ChangePasswordForm(forms.Form):
    validation_code = forms.CharField(
        max_length=6, 
        required=True,
        widget= forms.TextInput(
            attrs={'class': 'form-register__input', 'placeholder': 'Código Verificación'}
        )
    )
    password1 = forms.CharField( 
        required=True,
        widget= forms.PasswordInput(
            attrs={'class': 'form-register__input', 'placeholder': 'Contraseña nueva'}
        )
    )
    password2 = forms.CharField( 
        required=True,
        widget= forms.PasswordInput(
            attrs={'class': 'form-register__input', 'placeholder': 'Repetir nueva contraseña'}
        )
    )

    # Reescribimos la funcion __init__ para pasarle el pk al formulario desde el view
    def __init__(self, pk, *args, **kwargs):
        self.id_user = pk
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):

        codigo = self.cleaned_data['validation_code']

        if len(codigo) == 6:
            # verificamos si el codigo y el id del usuario son validos:
            activo = User.objects.cod_validation(
                self.id_user,
                codigo
            )
            if not activo:
                raise forms.ValidationError('El codigo es incorrecto')
        else:
            raise forms.ValidationError('El codigo es incorrecto')
        
        UserRegisterForm.validate_password(self)
