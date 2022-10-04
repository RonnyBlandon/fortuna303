import asyncio
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk.clients.metaApi.tradeException import TradeException
from datetime import datetime, timedelta, date
import json
import psycopg2

# Funcion para extraer los datos importantes y privados del sistema
with open("secret.json") as f:
    secret = json.loads(f.read())

def get_secret(secret_name, secrets=secret):
    try:
        return secrets[secret_name]
    except:
        msg = "La variable %s no existe" % secret_name
        raise msg


#Función que devuelve una lista de tuplas de los registros de cuentas mt5 de la base de datos y el cursor
#para seguir haciendo consultas, insertar o actualizar los datos.
def get_accounts_mt5_database():
    # Conectamos a la base de datos
    try:
        connetion = psycopg2.connect(database=get_secret("DB_NAME"), user=get_secret("USER"), password=get_secret("PASSWORD"))
        cursor = connetion.cursor()

    except Exception as err:
        print("Error en la conexión de la base de datos: ", err)
    #Consultamos los datos necesarios de cada cuenta mt5
    try:
        cursor.execute("SELECT id, id_client_metaapi FROM vps_accountmt5")
        accounts = cursor.fetchall()
        return {'accounts': accounts, 'conexion': connetion}

    except Exception as err:
        print("Error al consultar en la base de datos: ", err)
    connetion.commit()


# Esta funcion solo se ejecutara el domingo cuando abra el mercado de tokio
# Esta funcion recopila el balance de la cuenta en metaapi y lo inserta en la base de datos local
async def balance_initial():

    data = get_accounts_mt5_database()
    accounts = data['accounts']
    connetion = data['conexion']
    cursor = connetion.cursor()

    for account in accounts:
        id_account_mt5 = account[0]
        id_client_metaapi = account[1]

        # Nos conectamos a metaapi
        api = MetaApi(get_secret('METAAPI_TOKEN'))

        try:
            account = await api.metatrader_account_api.get_account(id_client_metaapi)
            initial_state = account.state
            deployed_states = ['DEPLOYING', 'DEPLOYED']

            if initial_state not in deployed_states:
                #  espere hasta que la cuenta esté implementada y conectada al corredor
                print('Deploying account')
                await account.deploy()

            print('Esperando a que el servidor API se conecte al intermediario (puede tardar un par de minutos)')
            await account.wait_connected()

            # connect to MetaApi API
            connection = account.get_rpc_connection()
            await connection.connect()

            # espere hasta que el estado del terminal se sincronice con el estado local
            print('Esperando a que el SDK se sincronice con el estado de la terminal (puede llevar algún tiempo según el tamaño de su historial)')
            await connection.wait_synchronized()
            # Obteniendo el balance de la cuenta
            account_info = await connection.get_account_information()
            balance = account_info['balance']
            await connection.close() # cerrando conexión

            # Insertamos los datos a la base de datos local
            try:
                start_date = date.today()
                end_date = start_date + timedelta(days=4)
                cursor.execute(f"INSERT INTO vps_accountmanagement (start_date, end_date, start_balance, withdraw_deposit, end_balance, gross_profit, commission, swap, net_profit, id_account_mt5_id) VALUES('{start_date}', '{end_date}', {balance}, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, {id_account_mt5})")
            except Exception as err: 
                print("Error al insertar datos: ", err)
            else:
                print("Datos insertados correctamente.")
            connetion.commit()

        except Exception as err:
            print(api.format_error(err))


# APARTIR DE AQUI ESTAN LAS FUNCIONES QUE SE EJECUTARAN EL VIERNES CUANDO CIERRE EL MERCADO
# Traemos el historial de los ultimos 5 dias en una lista para calcular las ganancias, swap y comisiones
async def list_orders_deals(account_id):
    api = MetaApi(get_secret('METAAPI_TOKEN'))

    try:
        account = await api.metatrader_account_api.get_account(account_id)
        initial_state = account.state
        deployed_states = ['DEPLOYING', 'DEPLOYED']

        if initial_state not in deployed_states:
            await account.deploy()

        # Esperando a que el servidor API se conecte al intermediario (puede tardar un par de minutos)
        await account.wait_connected()

        # conectarse a la API de MetaApi
        connection = account.get_rpc_connection()
        await connection.connect()

        # espere hasta que el estado del terminal se sincronice con el estado local
        #Esperando a que el SDK se sincronice con el estado de la terminal (puede llevar algún tiempo según el tamaño de su historial)'
        await connection.wait_synchronized()

        # Obteniendo el balance de la cuenta
        account_info = await connection.get_account_information()
        balance = account_info['balance']

        orders_deals = await connection.get_deals_by_time_range(datetime.utcnow() - timedelta(days=5), datetime.utcnow())
        orders_deals = orders_deals['deals']
        await connection.close()

        list_orders = []
        balance_change = 0.00
        # filtramos las ordenes por DEAL_TYPE_BUY y DEAL_TYPE_SELL
        for order in orders_deals:
            if order['type'] == "DEAL_TYPE_BALANCE":
                balance_change += order['profit']

            if order['type'] == "DEAL_TYPE_BUY" or order['type'] == "DEAL_TYPE_SELL":
                list_orders.append(order)

        return {'orders': list_orders, 'balance': balance, 'balance_change': balance_change}

    except Exception as err:
        print(api.format_error(err))


# Función para calcular el beneficio neto para agregarlo a la base de datos
async def calculate_profit():

    data = get_accounts_mt5_database()
    accounts = data['accounts']
    connetion = data['conexion']
    cursor = connetion.cursor()

    for account in accounts:
        id_account_mt5 = account[0]
        id_client_metaapi = account[1]

        data = await list_orders_deals(id_client_metaapi)

        commissions = 0.00
        swap = 0.00
        profits = 0.00

        for order in data['orders']:
            commissions += order['commission']
            swap += order['swap']
            profits += order['profit']

        net_profit = (profits - abs(commissions)) + swap


        # Actualizamos los datos usando subconsultas en sql
        try:
            cursor.execute(f"UPDATE vps_accountmanagement SET withdraw_deposit={data['balance_change']}, end_balance={data['balance']}, gross_profit={profits}, commission={commissions}, swap={swap}, net_profit={net_profit} WHERE id=(SELECT MAX(id) FROM vps_accountmanagement WHERE id_account_mt5_id={id_account_mt5})")
        except Exception as err: 
            print("Error al insertar datos: ", err)
        else:
            print("Datos Actualizados correctamente.")
        connetion.commit()


asyncio.run(balance_initial())
#asyncio.run(calculate_profit())
