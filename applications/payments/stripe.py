import stripe
from fortuna_303.settings.base import get_secret
from applications.users.models import User

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
        name=name + " " + last_name
    )

    user.update(id_customer_stripe=customer['id'])
    return user[0].id_customer_stripe


def verify_id_customer_stripe(id_user: int):
    id_customer = User.objects.get_id_customer_stripe(id_user)
    user = User.objects.filter(id=id_user)
    email = user[0].email

    if not id_customer:
        customers_exists = stripe.Customer.search(query=f"email:'{email}'",)

        if customers_exists['data']:
            user.update(id_customer_stripe=customers_exists['data'][0].id)
            id_customer = customers_exists['data'][0].id
        else:
            id_customer = create_customer_stripe(id_user)
    else:
        customers_exists = stripe.Customer.search(query=f"email:'{email}'",)
        if not customers_exists['data']:
            id_customer = create_customer_stripe(id_user)
        else:
            data_customer = customers_exists['data'][0]
            if data_customer['id'] != id_customer:
                user.update(id_customer_stripe=customers_exists['data'][0].id)
                id_customer = customers_exists['data'][0].id

    return id_customer


def create_order_stripe(id_user: int, amount: float, description: str):
    amount_cents = int(amount * 100)
    id_customer = verify_id_customer_stripe(id_user)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': description},
                'unit_amount': amount_cents
            },
            'quantity': 1,
        }],
        mode='payment',
        metadata={'custom_id': 'first_payment', 'id_user': id_user},
        customer=id_customer,
        success_url=redirect_page + '/payments/',
        cancel_url=redirect_page + '/payments/'
    )
    return session.url


def create_renewal_order_stripe(id_user: int, amount: float, description: str, metadata: dict):
    amount_cents = int(amount * 100)
    id_customer = verify_id_customer_stripe(id_user)

    metadata['id_user'] = id_user

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': description},
                'unit_amount': amount_cents
            },
            'quantity': 1,
        }],
        mode='payment',
        metadata=metadata,
        customer=id_customer,
        success_url=redirect_page + '/payments/',
        cancel_url=redirect_page + '/payments/'
    )
    return session.url
