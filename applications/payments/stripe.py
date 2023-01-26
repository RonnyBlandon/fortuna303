import stripe
from fortuna_303.settings.base import get_secret
from applications.users.models import User
"""Funciones para usar STRIPE"""

stripe.api_key = get_secret("STRIPE_PRIVATE_KEY")

redirect_page = "https://fortuna303.com/"


def create_customer_stripe(id_user: int):
    user = User.objects.filter(id=id_user)
    email = user[0].email
    name = user[0].name
    last_name = user[0].last_name

    customer = stripe.Customer.create(
        description="Este usuario es cliente de fortuna303.com",
        email=email,
        name=name+" "+last_name
    )

    user.update(id_customer_stripe=customer['id'])

    return user[0].id_customer_stripe


# Función para verificar si el id_customer_stripe del usuario exista en la base de datos y en stripe.
def verify_id_customer_stripe(id_user: int):

    id_customer = User.objects.get_id_customer_stripe(id_user)
    user = User.objects.filter(id=id_user)
    email = user[0].email
    # Si el usuario no tiene id_customer en la base de datos verificamos que exista uno en stripe con el email.
    if not id_customer:
        customers_exists = stripe.Customer.search(query=f"email:'{email}'",)

        if customers_exists['data']: 
            # Si encuentra uno actualizamos al usuario con el id_customer_stripe en la base de datos. 
            user.update(id_customer_stripe=customers_exists['data'][0].id)
            id_customer = customers_exists['data'][0].id
        else:    
            id_customer = create_customer_stripe(id_user)
    
    else:
        # verificamos que el id_customer_stripe que tiene el usuario exista en stripe.
        customers_exists = stripe.Customer.search(query=f"email:'{email}'",)
        if not customers_exists['data']:
            id_customer = create_customer_stripe(id_user)
        else:
            data_customer = customers_exists['data'][0]
            # De no coincidir el id de la base de datos con el de stripe actualizamos el de la base de datos.
            if data_customer['id'] != id_customer:
                user.update(id_customer_stripe=customers_exists['data'][0].id)
                id_customer = customers_exists['data'][0].id

    return id_customer


def create_order_stripe(id_user: int, amount: float, description: str):
#Como stripe solo reconoce los precios de los productos y servicios en centavos hay que mandarle solo numeros 
#enteros, se debe multiplicar el amount por 100 para que sea el precio equivalente de dolares a centavos.
    amount_cents = int(amount * 100)
    # Obtenemos el id_customer
    id_customer = verify_id_customer_stripe(id_user)

    # creamos la sesión de pago para el usuario
    session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price_data': {'currency': 'usd',
        'product_data': {'name': description},
        'unit_amount': amount_cents},'quantity': 1,
    }],
    mode='payment',
    metadata={'custom_id': 'first_payment', 'id_user': id_user},
    customer=id_customer,
    success_url=redirect_page + '/payments/',
    cancel_url=redirect_page + '/payments/'
    )
    return session.url


def create_renewal_order_stripe(id_user: int, case: str, payment_id: int, amount: float, description: str):
#Como stripe solo reconoce los precios de los productos y servicios en centavos hay que mandarle solo numeros 
#enteros, se debe multiplicar el amount por 100 para que sea el precio equivalente de dolares a centavos.
    amount_cents = int(amount * 100)
    # Obtenemos el id_customer
    id_customer = verify_id_customer_stripe(id_user)

    # creamos la sesión de pago para el usuario
    session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price_data': {'currency': 'usd',
        'product_data': {'name': description},
        'unit_amount': amount_cents},'quantity': 1,
    }],
    mode='payment',
    metadata={'custom_id': case, 'payment_id': payment_id, 'id_user': id_user},
    customer=id_customer,
    success_url=redirect_page + '/payments/',
    cancel_url=redirect_page + '/payments/'
    )
    return session.url
