""" Funciones extras de python para la aplicacion users. 
    Aqui estan las funciones que no son parte de django. 
"""
import requests

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
                'amount': {'currency_code': 'USD', 'value': amount},
                'description': description
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
        print(data)
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

        data = {'id': details['id'], 'amount': details['amount']['value']}

        return data
    else:
        #print('Lo sentimos, hubo un fallo en la conexión. La razón:', resp.content)
        return None
