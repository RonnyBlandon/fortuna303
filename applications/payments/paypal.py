import requests
from fortuna_303.settings.base import get_secret

"""Funciones para usar la api de PAYPAL"""

link_main_api = "https://api-m.paypal.com"
redirect_page = "https://fortuna303.com/"

def create_order_paypal(amount: float, description: str):

    url = link_main_api + '/v2/checkout/orders'
    auth_user = (get_secret('PAYPAL_CLIENT_ID'), get_secret('PAYPAL_CLIENT_SECRET'))
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
            'return_url': redirect_page + '/payments/',
            'cancel_url': redirect_page + '/payments/'
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


def create_renewal_order_paypal(case: str, payment_id: int, amount: float, description: str):

    url = link_main_api + '/v2/checkout/orders'
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
            'return_url': redirect_page + '/payments/',
            'cancel_url': redirect_page + '/payments/'
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
def capture_order_paypal(id_order):
    url = link_main_api + '/v2/checkout/orders/'+id_order+'/capture'
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
