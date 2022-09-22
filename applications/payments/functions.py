""" Funciones extras de python para la aplicacion users. 
    Aqui estan las funciones que no son parte de django. 
"""
import requests

"""Funciones para usar la api de PAYPAL"""


def create_order():
    url = 'https://api-m.sandbox.paypal.com/v2/checkout/orders'
    auth_user = ('AcdmHxGozWnFBLzScbP59mR8Nn3EADJz2ibstNgP4bAXbZ9QOoVDicHlaa5P4-66SvtR3Q0Zs4nEr4Av',
                 'EH9FJ_TzOwTIwl2ZBHTAMjtj4QuMuPcT_h3zxvZhBdle-FH0OCaRQ8ResUt7LuHZ1QQe6smeGITeio86')
    headers = {'Content-Type': 'application/json'}
    order = {
        'intent': 'CAPTURE',
        'purchase_units': [
            {
                'amount': {'currency_code': 'USD', 'value': '70.00'},
                'description': 'Alojamiento vps de cuenta metatrader 5 y uso del sistema copytrading.'
            }
        ],
        'application_context': {
            'brand_name': 'Fortuna 303',
            'payment_method': {'payee_preferred': 'IMMEDIATE_PAYMENT_REQUIRED'},
            'user_action': 'PAY_NOW',
            'return_url': 'http://127.0.0.1:8000/panel-user/',
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


def capture_order(id_order):
    url = 'https://api-m.sandbox.paypal.com/v2/checkout/orders/' + id_order + '/capture'
    auth_user = ('AcdmHxGozWnFBLzScbP59mR8Nn3EADJz2ibstNgP4bAXbZ9QOoVDicHlaa5P4-66SvtR3Q0Zs4nEr4Av',
                 'EH9FJ_TzOwTIwl2ZBHTAMjtj4QuMuPcT_h3zxvZhBdle-FH0OCaRQ8ResUt7LuHZ1QQe6smeGITeio86')
    headers = {'Content-Type': 'application/json'}

    resp = requests.post(url, auth=auth_user, headers=headers)

    if resp.status_code == 201:
        data = resp.json()
        payments_details = data['']
        print(data)
        return data
    else:
        print('Lo sentimos, hubo un fallo en la conexión. La razón:', resp.content)


def create_invoice():
    url = 'https://api-m.sandbox.paypal.com/v2/invoicing/invoices'
    auth_user = ('AcdmHxGozWnFBLzScbP59mR8Nn3EADJz2ibstNgP4bAXbZ9QOoVDicHlaa5P4-66SvtR3Q0Zs4nEr4Av',
                 'EH9FJ_TzOwTIwl2ZBHTAMjtj4QuMuPcT_h3zxvZhBdle-FH0OCaRQ8ResUt7LuHZ1QQe6smeGITeio86')
    headers = {'Content-Type': 'application/json'}
    invoice = {
        "detail": {
            "invoice_number": "1237",
            "invoice_date": "2022-08-25",
            "currency_code": "USD"
        },
        "invoicer": {
            "email_address": "sb-43kdni1016131@business.example.com",
            "phones": [
                {
                    "country_code": "001",
                    "national_number": "4085551234",
                    "phone_type": "MOBILE"
                }
            ],
            "website": "https://fortuna303.com",
            "logo_url": "https://fortuna303.com/producto/copy-trader-manual/"
        },
        "items": [
            {
                "name": "Vps + copytrading (30 dias)",
                "description": "Vps para cuenta metatrader 5 y uso de copytrading mensual.",
                "quantity": "1",
                "unit_amount": {
                    "currency_code": "USD",
                    "value": "50.00"
                },
                "unit_of_measure": "HOURS"
            }
        ]
    }

    resp = requests.post(url, auth=auth_user, json=invoice, headers=headers)

    if resp.status_code == 201:
        data = resp.json()
        print(data)
        return data
    else:
        print('Lo sentimos, hubo un fallo en la conexión. La razón:', resp.content)


create_invoice()
