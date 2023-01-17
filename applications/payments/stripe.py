import stripe
from fortuna_303.settings.base import get_secret
"""Funciones para usar la api de STRIPE"""

stripe.api_key = get_secret("STRIPE_PRIVATE_KEY")

redirect_page = "http://127.0.0.1:8000"

def create_order_stripe(email: str, amount: float, description: str):
    # Como stripe solo reconoce los precios de los producto o servicios en centavos hay que mandarle solo
    # numeros enteros y multiplicarlos por 100 para que sea el precio equivalente de centavos a dolares.
    

    session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price_data': {'currency': 'usd',
        'product_data': {'name': description},
        'unit_amount': 700},'quantity': 1,
    }],
    mode='payment',
    metadata={'custom_id': 'first_payment'},
    customer_email=email,
    success_url=redirect_page + '/payment-success',
    cancel_url=redirect_page + '/payment-cancel'
    )
    return session.url
