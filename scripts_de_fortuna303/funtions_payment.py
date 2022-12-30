import psycopg2
from datetime import datetime, date, timedelta
from calendar import monthrange, isleap
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk.clients.metaApi.tradeException import TradeException
from funtions_panel_user import get_secret, get_accounts_mt5_database
from email.message import EmailMessage
import smtplib

# Función que devuelve una lista de tuplas de los usuarios de la base de datos y el cursor
# para seguir haciendo consultas, insertar o actualizar los datos.
def get_users_database():
    # Conectamos a la base de datos
    try:
        connection = psycopg2.connect(database=get_secret(
            "DB_NAME"), user=get_secret("USER"), password=get_secret("PASSWORD"))
        cursor = connection.cursor()

    except Exception as err:
        print("Error en la conexión de la base de datos: ", err)
    # Consultamos el id de cada user
    try:
        cursor.execute(
            "SELECT id, name, last_name, email, level_id FROM users_user WHERE subscriber='true'")
        users = cursor.fetchall()
        return {'users': users, 'conexion': connection}

    except Exception as err:
        print("Error en get_users_database() al consultar en la base de datos: ", err)
    connection.commit()
    connection.close()


# Obtenemos el ultimo pago de vps del usuario y lo devolvemos en un dict
def get_vps_payment_database(id_user: int):
    # Conectamos a la base de datos
    try:
        connection = psycopg2.connect(database=get_secret(
            "DB_NAME"), user=get_secret("USER"), password=get_secret("PASSWORD"))
        cursor = connection.cursor()

    except Exception as err:
        print("Error en la conexión de la base de datos: ", err)
    # Consultamos el ultimo pago del vps del usuario
    try:
        cursor.execute(
            f"SELECT id, expiration, status FROM payments_vpspayment WHERE id=(SELECT MAX(id) FROM payments_vpspayment WHERE id_user_id={id_user});")
        vps_payment = cursor.fetchone()
        return {'id': vps_payment[0], 'expiration': vps_payment[1], 'status': vps_payment[2]}

    except Exception as err:
        print("Error en get_vps_payment_database() al consultar en la base de datos: ", err)
    connection.commit()
    connection.close()


def get_trader_payment_database(id_user: int):
    # Conectamos a la base de datos
    try:
        connection = psycopg2.connect(database=get_secret(
            "DB_NAME"), user=get_secret("USER"), password=get_secret("PASSWORD"))
        cursor = connection.cursor()

    except Exception as err:
        print("Error en la conexión de la base de datos: ", err)
    # Consultamos el ultimo pago del vps del usuario
    try:
        cursor.execute(
            f"SELECT id, expiration, id_management_id, status FROM payments_traderpayment WHERE id=(SELECT MAX(id) FROM payments_traderpayment WHERE id_user_id={id_user});")
        trader_payment = cursor.fetchone()
        if trader_payment:
            return {'id': trader_payment[0], 'expiration': trader_payment[1], 'id_management': trader_payment[2], 'status': trader_payment[3]}
        else:
            return None
    except Exception as err:
        print("Error en get_trader_payment_database() al consultar en la base de datos: ", err)
    connection.commit()
    connection.close()


# Obtenemos el ultimo pago del trader del usuario y lo devolvemos en un dict
def get_management_database(id_user: int):
    # Conectamos a la base de datos
    try:
        connection = psycopg2.connect(database=get_secret(
            "DB_NAME"), user=get_secret("USER"), password=get_secret("PASSWORD"))
        cursor = connection.cursor()

    except Exception as err:
        print("Error en la conexión de la base de datos: ", err)
    # Consultamos el ultimo pago del vps del usuario
    try:
        cursor.execute(
            f"SELECT id, start_date, end_date, net_profit FROM vps_accountmanagement WHERE id=(SELECT MAX(id) FROM vps_accountmanagement WHERE id_user_id={id_user});")
        management = cursor.fetchone()
        return {'id': management[0], 'start_date': management[1], 'end_date': management[2], 'net_profit': management[3]}

    except Exception as err:
        print(
            "Error en gget_management_database() al consultar en la base de datos: ", err)
    connection.commit()
    connection.close()


# Obtenemos las cuenta mt5 sin pagar del usuario para posteriormente desconectarlos de metaapi
def get_mt5_without_paying_vps():
    # Conectamos a la base de datos
    try:
        connection = psycopg2.connect(database=get_secret("DB_NAME"), user=get_secret("USER"),password=get_secret("PASSWORD"))
        cursor = connection.cursor()

    except Exception as err:
        print("Error en la conexión de la base de datos: ", err)
    
    # Consultamos todos los pagos de vps o trader sin pagar del usuario
    try:
        payments = []
        cursor.execute(
            f"SELECT id, expiration, id_user_id FROM payments_vpspayment WHERE status='Pagar';")
        list_payment = cursor.fetchall()
        today = date.today()
        for payment in list_payment:
            if today > (payment[1] + timedelta(days=5)):
                payments.append(payment)

    except Exception as err:
        print("Error en et_mt5_without_paying() al consultar en la base de datos: ", err)
    connection.commit()

    if payments:
        # Consultamos las cuentas mt5 que no han pagado a datos de tipo dict y agregamos a una lista
        accounts_mt5 = []
        for payment in payments:
            try:
                cursor.execute(
                    f"SELECT id, id_client_metaapi, status, id_user_id FROM vps_accountmt5 WHERE id_user_id={payment[2]} AND status='1';")
                mt5 = cursor.fetchone()
                if mt5:
                    if mt5[2] == '1':
                        dictionary = {'id': mt5[0], 'id_metaapi_mt5': mt5[1], 'id_user': mt5[3]}
                        accounts_mt5.append(dictionary)

            except Exception as err:
                print("Error en et_mt5_without_paying_vps() al consultar en la base de datos: ", err)
            connection.commit()
        data = {'accounts_mt5': accounts_mt5, 'payments': payments, 'connection': connection}
        return data


def get_mt5_without_paying_trader():
    data = get_accounts_mt5_database()
    accounts = data['accounts']
    connection = data['conexion']
    cursor = connection.cursor()
    accounts_mt5 = []
    for account in accounts:
        # Consultamos todos los pagos de gestion de mt5 sin pagar del usuario
        try:
            cursor.execute(
                f"SELECT count(*) FROM payments_traderpayment WHERE id_user_id={account[2]} AND status='Pagar';")
            amount_payments = cursor.fetchone()
        except Exception as err:
            print("Error en et_mt5_without_paying_trader() al consultar en la base de datos: ", err)
        if amount_payments[0] > 1:
            accounts_mt5.append({'id': account[0], 'id_account_metaapi': account[1], 'id_user': account[2]})
    return {'accounts_mt5': accounts_mt5, 'connection': connection}


def expiration_monthly(date: datetime):
    # calculamos cuantos dias tiene el mes
    days_of_month = monthrange(date.year, date.month)[1]
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
            elif date.month == 7 or date.month == 12:  # En caso de que sea Julio o Diciembre
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


# funcion para enviar correos al usuario por desactivacion de cuenta o agregación de factura
def send_email(email_addressee: str, message: str, affair: str):
    sender = get_secret("EMAIL")
    password = get_secret("PASS_EMAIL")
    # Creamos el mensaje con sus datos correspondientes
    email = EmailMessage()
    email["From"] = sender
    email["To"] = email_addressee
    email["Subject"] = affair
    email.set_content(message, subtype="html")
    # El puerto del protocolo TLS es generalmente 587.
    smtp = smtplib.SMTP("smtp.gmail.com", port=587)
    # Iniciar la conexión segura vía TLS.
    smtp.starttls()
    # Nos authenticamos en la cuenta del correo emisor y enviamos el mensaje al destinatario
    smtp.login(sender, password)
    smtp.sendmail(sender, email_addressee, email.as_string())
    smtp.quit()


async def add_vps_payment_database():
    data = get_users_database()
    users = data['users']
    connection = data['conexion']
    cursor = connection.cursor()

    for user in users:
        id_user = user[0]
        last_vps_payment = get_vps_payment_database(id_user)

        if last_vps_payment['status'] != "Pagar":
            # Checkeamos si ya es la fecha de pago
            today = date.today()
            if today >= last_vps_payment['expiration']:
                expiration = expiration_monthly(today)
                id_level = user[4]

                # Consultamos el precio del level del usuario
                try:
                    cursor.execute(
                        f"SELECT price FROM users_level WHERE id={id_level}")
                    price_tuple = cursor.fetchone()
                    price = price_tuple[0]
                except Exception as err:
                    print(
                        "Error en add_vps_payment_database() al insertar en la base de datos: ", err)
                connection.commit()

                # Insertamos la nueva factura en la base de datos
                try:
                    cursor.execute(
                        f"INSERT INTO payments_vpspayment (created_date, expiration, total, status, transaction_id, id_user_id, payment_method) VALUES('{date.today()}', '{expiration}', {price}, 'Pagar', '', {id_user}, '');")
                except Exception as err:
                    print(
                        "Error en add_vps_payment_database() al insertar en la base de datos: ", err)
                connection.commit()

                # Creamos el mensaje y se lo enviamos por correo
                affair = 'PAGO DE VPS + COPYTRADING'
                message = f'<div style:margin: 0em auto; border: 0.15em solid #000; border-radius: 0.3em;"><a href="https://fortuna303.com" target="_blank"><img src="/static/img/logo.png" alt="logo"></a><h1>Hola {user[1]} {user[2]}</h1><p style="font-size: 1.2em;">Se le informa que ya se puede hacer el pago de la mensualidad de <b>VPS + COPYTRADING.</b> Le informamos también que de no hacerse el pago después de 5 días de la fecha de expiración se desconectara su cuenta de metatrader 5 del sistema copytrading y se reconectara una vez este al día con todos los pagos, esto incluye los pagos de <b>GESTIÓN DE CUENTAS DE MT5.</b></p><a style="padding:0.5em 1em;background:#00f; border: 0.2em solid #D4FF00;color: #fff;text-decoration: none;cursor: pointer;" href="https://fortuna303.com/payments/" target="_blank">Ir a la pagina de pago</a></div>'
                send_email(user[3], message=message, affair=affair)
    connection.close()


async def add_trader_payment_database():
    data = get_users_database()
    users = data['users']
    connection = data['conexion']
    cursor = connection.cursor()

    for user in users:
        id_user = user[0]
        last_management = get_management_database(id_user)
        last_payment = get_trader_payment_database(id_user)
        total = 0.00
        status = "Pagado"

        if last_management['net_profit'] > 0.01:# vemos si hubo ganancias si esta en negativo poner en 0.00
            status = "Pagar"
            total = (50 * last_management['net_profit'] / 100) #Sacamos el 50% de las ganancias del profit

        if last_payment != None:
            if last_management['id'] != last_payment['id_management']:
                # Insertamos la nueva factura en la base de datos
                try:
                    cursor.execute(
                        f"INSERT INTO payments_traderpayment (created_date, expiration, total, status, transaction_id, id_management_id, id_user_id, payment_method) VALUES('{last_management['start_date']}', '{last_management['end_date']}', {total}, '{status}', '', {last_management['id']}, {id_user}, '');")
                except Exception as err:
                    print(
                        "Error en add_trader_payment_database() al insertar en la base de datos: ", err)
                connection.commit()

                # Creamos el mensaje y se lo enviamos por correo
                affair = 'PAGO DE GESTION DE CUENTA MT5'
                message = f'<div style:margin: 0em auto; border: 0.15em solid #000; border-radius: 0.3em;"><a href="https://fortuna303.com" target="_blank"><img src="https://fortuna303.com/static/img/logo.png" alt="logo"></a><h1>Hola {user[1]} {user[2]}</h1><p style="font-size: 1.2em;">Se le informa que ya se puede hacer el pago de <b>GESTION DE CUENTAS DE METATRADER 5</b>. Le informamos también que de acumularse dos pagos adeudados se desconectara su cuenta metatrader 5 del sistema copytrading y se reconectara una vez este al día con todos los pagos, esto incluye los pagos de <b>VPS + COPYTRADING.</b></p><a style="padding:0.5em 1em;background:#00f; border: 0.2em solid #D4FF00;color: #fff;text-decoration: none;cursor: pointer;" href="https://fortuna303.com/payments/" target="_blank">Ir a la pagina de pago</a></div>'
                send_email(user[3], message=message, affair=affair)

        else:
            # Como no hay facturas insertamos una nueva factura en la base de datos
            try:
                cursor.execute(
                    f"INSERT INTO payments_traderpayment (created_date, expiration, total, status, transaction_id, id_management_id, id_user_id, payment_method) VALUES('{last_management['start_date']}', '{last_management['end_date']}', {total}, '{status}', '', {last_management['id']}, {id_user}, '');")
            except Exception as err:
                print(
                    "Error en add_trader_payment_database() al insertar en la base de datos: ", err)
            connection.commit()

            # Creamos el mensaje y se lo enviamos por correo
            affair = 'PAGO DE GESTION DE CUENTA MT5'
            message = f'<div style:margin: 0em auto; border: 0.15em solid #000; border-radius: 0.3em;"><a href="https://fortuna303.com" target="_blank"><img src="https://fortuna303.com/static/img/logo.png" alt="logo"></a><h1>Hola {user[1]} {user[2]}</h1><p style="font-size: 1.2em;">Se le informa que ya se puede hacer el pago de <b>GESTION DE CUENTAS DE METATRADER 5</b>. Le informamos también que de acumularse dos pagos adeudados se desconectara su cuenta metatrader 5 del sistema copytrading y se reconectara una vez este al día con todos los pagos, esto incluye los pagos de <b>VPS + COPYTRADING.</b></p><a style="padding:0.5em 1em;background:#00f; border: 0.2em solid #D4FF00;color: #fff;text-decoration: none;cursor: pointer;" href="https://fortuna303.com/payments/" target="_blank">Ir a la pagina de pago</a></div>'
            send_email(user[3], message=message, affair=affair)
    connection.close()


async def disable_mt5_without_paying_trader():
    api = MetaApi(get_secret("METAAPI_TOKEN"))

    data = get_mt5_without_paying_trader()
    if data:
        accounts_mt5 = data['accounts_mt5']
        connection = data['connection']
        cursor = connection.cursor()

        for account in accounts_mt5:
            #Desconectamos la cuenta borrando de metaapi la cuenta mt5
            account_metaapi = await api.metatrader_account_api.get_account(account_id=account['id_account_metaapi'])
            try:
                await account_metaapi.remove()
            except Exception as err:
                print(err.details)
    
            # Actualizamos la cuenta mt5 a 'desconectado' sin borrar o modificar los demas datos de la cuenta mt5
            # esto por si en futuro se pone al dia con los pagos se debe volver a conectar la cuenta a metaapi
            try:
                cursor.execute(f"UPDATE vps_accountmt5 SET status='0' WHERE id={account['id']};")
                cursor.execute(f"SELECT name, last_name, email FROM users_user WHERE id={account['id_user']};")
                user = cursor.fetchone()
                print(user)
            except Exception as err:
                print(
                    "Error en disable_mt5_without_paying_trader() al actualizar en la base de datos: ", err)
            connection.commit()

            # Creamos el mensaje y se lo enviamos por correo
            affair = 'CUENTA METATRADER 5 DESCONECTADA'
            message = f'<div style:margin: 0em auto; border: 0.15em solid #000; border-radius: 0.3em;"><a href="https://fortuna303.com" target="_blank"><img src="https://fortuna303.com/static/img/logo.png" alt="logo"></a><h1>Hola {user[0]} {user[1]}</h1><p style="font-size: 1.2em;">Su cuenta de metatrader 5 a sido desconectada por falta de pago de <b>GESTION DE CUENTAS MT5</b>. Para reconectarla debe estar al día con todo los pagos, esto incluye los pagos de <b>VPS + COPYTRADING</b> y automáticamente se reconectará en minutos. Si su cuenta no se ha conectado al cabo de 15 minutos, mandar un mensaje en la página de contacto.</p><a style="padding:0.5em 1em;background:#00f; border: 0.2em solid #D4FF00;color: #fff;text-decoration: none;cursor: pointer;" href="https://fortuna303.com/payments/" target="_blank">Ir a la pagina de pago</a></div>'
            send_email(user[2], message=message, affair=affair)
        connection.close()


async def disable_mt5_without_paying_vps():
    api = MetaApi(get_secret("METAAPI_TOKEN"))

    data = get_mt5_without_paying_vps()
    if data:    
        accounts_mt5 = data['accounts_mt5']
        connection = data['connection']
        cursor = connection.cursor()

        for account in accounts_mt5:
            #Desconectamos la cuenta borrando de metaapi la cuenta mt5
            try:
                account_metaapi = await api.metatrader_account_api.get_account(account_id=account['id_metaapi_mt5'])
                await account_metaapi.remove()
            except Exception as err:
                print(err.details)
    
            # Actualizamos la cuenta mt5 a 'desconectado' sin borrar o modificar los demas datos de la cuenta
            # esto por si en futuro se pone al dia con los pagos se debe volver a conectar la cuenta a metaapi
            try:
                cursor.execute(f"UPDATE vps_accountmt5 SET status='0' WHERE id={account['id']};")
                cursor.execute(f"SELECT name, last_name, email FROM users_user WHERE id={account['id_user']};")
                user = cursor.fetchone()
            except Exception as err:
                print("Error en disable_mt5_without_paying_trader() al actualizar o consultar en la base de datos: ", err)
            connection.commit()

            # Creamos el mensaje y se lo enviamos por correo
            affair = 'CUENTA METATRADER 5 DESCONECTADA'
            message = f'<div style:margin: 0em auto; border: 0.15em solid #000; border-radius: 0.3em;"><a href="https://fortuna303.com" target="_blank"><img src="https://fortuna303.com/static/img/logo.png" alt="logo"></a><h1>Hola {user[0]} {user[1]}</h1><p style="font-size: 1.2em;">Su cuenta de metatrader 5 a sido desconectada por falta de pago en su mensualidad del <b>VPS + COPYTRADING</b>. Para reconectarla debe estar al día con todo los pagos, esto incluye los pagos de <b>GESTION DE CUENTAS DE MT5</b> y automáticamente se reconectará en unos minutos. Si su cuenta no se ha conectado al cabo de 15 minutos, mandar un mensaje en la página de contacto.</p><a style="padding:0.5em 1em;background:#00f; border: 0.2em solid #D4FF00;color: #fff;text-decoration: none;cursor: pointer;" href="https://fortuna303.com/payments/" target="_blank">Ir a la pagina de pago</a></div>'
            send_email(user[2], message=message, affair=affair)
        connection.close()
