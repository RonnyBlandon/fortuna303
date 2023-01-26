"""Funciones extras de python para la aplicacion payments."""
from datetime import datetime, timedelta
from calendar import isleap, monthrange
# functions of django
from django.contrib import messages
# import models
from applications.vps.models import AccountMt5

"""Funciones de la app Payment"""

def enable_reconnection_mt5(id_user: int, request):
    account_mt5 = AccountMt5.objects.filter(id_user=id_user)
    account_mt5.update(reconnect=True)
    messages.add_message(request=request, level=messages.SUCCESS, message='Se ha agregado el botón para reconectar su cuenta mt5.')


def expiration_vps(date: datetime):
    days_of_month = monthrange(date.year, date.month)[1]  # calculamos cuantos dias tiene el mes
    # Agregamos la fecha de vencimiento
    match days_of_month:
        case 31:
            if date.month == 1:  # Preguntando si es enero
                if isleap(date.year):  # Preguntando si es año bisiesto
                    if date.day == 30:
                        expiration = date + timedelta(days=30)
                    elif date.day == 31:
                        expiration = date + timedelta(days=29)
                    else:
                        expiration = date + timedelta(days=31)
                else: 
                    if date.day == 29:
                        expiration = date + timedelta(days=30)
                    elif date.day == 30:
                        expiration = date + timedelta(days=29)
                    elif date.day == 3:
                        expiration = date + timedelta(days=28)
                    else:
                        expiration = date + timedelta(days=31)
            elif date.month == 7 or date.month == 12: # En caso de que sea Julio o Diciembre
                expiration = date + timedelta(days=31)
            else:
                if date.day == 31:
                    expiration = date + timedelta(days=30)
                else:
                    expiration = date + timedelta(days=31)
        case 30:
            expiration = date + timedelta(days=30)
        case 29:
            expiration = date + timedelta(days=29)
        case 28:
            expiration = date + timedelta(days=28)
        
    return expiration
