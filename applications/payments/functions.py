""" Funciones extras de python para la aplicacion users. 
    Aqui estan las funciones que no son parte de django. 
"""
import requests
from datetime import datetime, timedelta
from calendar import isleap, monthrange
import asyncio
# functions of django
from django.contrib import messages
# functions of applications
from applications.vps.metaapi import create_server_mt5, configure_copyfactory
from applications.vps.functions import decrypt_password
# import models
from applications.users.models import User
from applications.vps.models import AccountMt5, AccountManagement
"""Funciones de la app Payment"""


def reconnect_mt5_account(id_user: int, request):
    user = User.objects.get(id=id_user)
    account_mt5 = AccountMt5.objects.get(id_user=id_user)
    full_name = user.name + ' ' + user.last_name
    password_string = account_mt5.password
    # Convertimos el password_string de string a bytes para desencriptar con la función decrypt_password()
    password_bytes = eval(password_string)
    password = decrypt_password(password_bytes)

    try:
        account = asyncio.run(create_server_mt5(full_name, account_mt5.login, password, account_mt5.server))
        if account:
            try:
                suscriber = asyncio.run(configure_copyfactory(account['id']))
                if suscriber.status_code == 204:
                    AccountMt5.objects.update_status_account_mt5(id=account_mt5.id, status='1', id_client_metaapi=account['id'])
                    messages.add_message(request=request, level=messages.SUCCESS, message='La cuenta se ha reconectado con éxito.')
            except Exception as err:
                messages.add_message(request=request, level=messages.ERROR, message='Ha habido un error en la reconexión, por favor mande un mensaje en la página de contacto.')
                print("Error al suscribir la cuenta mt5 a la cuenta madre en metaapi. El error es: ", err)
    except Exception as err:
        messages.add_message(request=request, level=messages.ERROR, message='Ha habido un error en la reconexión, por favor mande un mensaje en la página de contacto.')
        print("Error al crear la cuenta mt5 en metaapi. El error es: ", err)


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


"""Funciones para usar la api de PAYPAL"""

def create_order(amount: float, description: str, ):

    url = 'https://api-m.sandbox.paypal.com/v2/checkout/orders'
    auth_user = ('AcdmHxGozWnFBLzScbP59mR8Nn3EADJz2ibstNgP4bAXbZ9QOoVDicHlaa5P4-66SvtR3Q0Zs4nEr4Av',
                 'EH9FJ_TzOwTIwl2ZBHTAMjtj4QuMuPcT_h3zxvZhBdle-FH0OCaRQ8ResUt7LuHZ1QQe6smeGITeio86')
    headers = {'Content-Type': 'application/json'}
    order = {
        'intent': 'CAPTURE',
        'purchase_units': [
            {
                'amount': {'currency_code': 'USD', 'value': str(amount)},
                'description': description,
                'custom_id': 'first_payment'
            }
        ],
        'application_context': {
            'brand_name': 'Fortuna 303',
            'payment_method': {'payee_preferred': 'IMMEDIATE_PAYMENT_REQUIRED'},
            'user_action': 'PAY_NOW',
            'return_url': 'http://127.0.0.1:8000/payments/',
            'cancel_url': 'http://127.0.0.1:8000/payments/'
        }
    }

    resp = requests.post(url, auth=auth_user, json=order, headers=headers)

    if resp.status_code == 201:
        data = resp.json()
        for link in data['links']:
            if link['rel'] == 'approve':
                return link['href']
    else:
        print('Lo sentimos, hubo un fallo en la conexión. La razón:', resp.content)


def create_renewal_order(case: str, payment_id: int, amount: float, description: str, ):

    url = 'https://api-m.sandbox.paypal.com/v2/checkout/orders'
    auth_user = ('AcdmHxGozWnFBLzScbP59mR8Nn3EADJz2ibstNgP4bAXbZ9QOoVDicHlaa5P4-66SvtR3Q0Zs4nEr4Av',
                 'EH9FJ_TzOwTIwl2ZBHTAMjtj4QuMuPcT_h3zxvZhBdle-FH0OCaRQ8ResUt7LuHZ1QQe6smeGITeio86')
    headers = {'Content-Type': 'application/json'}
    order = {
        'intent': 'CAPTURE',
        'purchase_units': [
            {
                'amount': {'currency_code': 'USD', 'value': str(amount)},
                'description': description,
                'custom_id': "{'%s': %s}" % (case, payment_id)
            }
        ],
        'application_context': {
            'brand_name': 'Fortuna 303',
            'payment_method': {'payee_preferred': 'IMMEDIATE_PAYMENT_REQUIRED'},
            'user_action': 'PAY_NOW',
            'return_url': 'http://127.0.0.1:8000/payments/',
            'cancel_url': 'http://127.0.0.1:8000/payments/'
        }
    }

    resp = requests.post(url, auth=auth_user, json=order, headers=headers)

    if resp.status_code == 201:
        data = resp.json()
        for link in data['links']:
            if link['rel'] == 'approve':
                return link['href']
    else:
        print('Lo sentimos, hubo un fallo en la conexión. La razón:', resp.content)


# Despues de que el usuario pague se debe capturar el pago para que se refleje en la cuenta paypal
def capture_order(id_order):
    url = 'https://api.sandbox.paypal.com/v2/checkout/orders/'+id_order+'/capture'
    auth_user = ('AcdmHxGozWnFBLzScbP59mR8Nn3EADJz2ibstNgP4bAXbZ9QOoVDicHlaa5P4-66SvtR3Q0Zs4nEr4Av',
                 'EH9FJ_TzOwTIwl2ZBHTAMjtj4QuMuPcT_h3zxvZhBdle-FH0OCaRQ8ResUt7LuHZ1QQe6smeGITeio86')
    headers = {'Content-Type': 'application/json'}

    resp = requests.post(url, auth=auth_user, headers=headers)

    if resp.status_code == 201:
        data = resp.json()
        details = data['purchase_units'][0]['payments']['captures'][0] # sacamos los detalles de pago

        data = {'id': details['id'], 'amount': details['amount']['value'], 'custom_id': details['custom_id']}

        return data
    else:
        #print('Lo sentimos, hubo un fallo en la conexión. La razón:', resp.content)
        return None
