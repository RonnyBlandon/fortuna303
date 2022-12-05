import asyncio
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk.clients.metaApi.tradeException import TradeException
from datetime import datetime, timedelta, date
import json
import psycopg2

# Funcion para extraer los datos importantes y privados del sistema
with open(r"C:\Users\RONNY BLANDON\Desktop\fortuna\secret.json") as f:
    secret = json.loads(f.read())


def get_secret(secret_name, secrets=secret):
    try:
        return secrets[secret_name]
    except:
        msg = "La variable %s no existe" % secret_name
        raise msg


# Función que devuelve una lista de tuplas de los registros de cuentas mt5 de la base de datos y el cursor
# para seguir haciendo consultas, insertar o actualizar los datos.
def get_accounts_mt5_database():
    # Conectamos a la base de datos
    try:
        connection = psycopg2.connect(database=get_secret(
            "DB_NAME"), user=get_secret("USER"), password=get_secret("PASSWORD"))
        cursor = connection.cursor()

    except Exception as err:
        print("Error en la conexión de la base de datos: ", err)
    # Consultamos los datos necesarios de cada cuenta mt5
    try:
        cursor.execute(
            "SELECT id, id_client_metaapi, id_user_id FROM vps_accountmt5 WHERE status='1'")
        accounts = cursor.fetchall()
        return {'accounts': accounts, 'conexion': connection}

    except Exception as err:
        print("Error al consultar en la base de datos: ", err)
    connection.commit()
    connection.close()


# Esta funcion solo se ejecutara el domingo cuando abra el mercado de tokio
# Esta funcion recopila el balance de la cuenta en metaapi y lo inserta en la base de datos local
async def balance_initial():

    data = get_accounts_mt5_database()
    accounts = data['accounts']
    connetion = data['conexion']
    cursor = connetion.cursor()

    for account in accounts:
        id_client_metaapi = account[1]
        id_user = account[2]

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

            print(
                'Esperando a que el servidor API se conecte al intermediario (puede tardar un par de minutos)')
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
            await connection.close()  # cerrando conexión

            start_date = date.today()
            end_date = start_date + timedelta(days=5)

            # Insertamos los datos a la base de datos local
            try:
                cursor.execute(
                    f"INSERT INTO vps_accountmanagement (start_date, end_date, start_balance, withdraw_deposit, end_balance, gross_profit, commission, swap, net_profit, id_user_id) VALUES('{start_date}', '{end_date}', {balance}, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, {id_user})")
            except Exception as err:
                print(
                    "Error al insertar datos. Proveniente de la función balance_initial(): ", err)
            else:
                print("Datos insertados correctamente.")
            connetion.commit()

        except Exception as err:
            print("Error en la conexion de una cuenta mt5 /n",
                  api.format_error(err))


# APARTIR DE AQUI ESTAN LAS FUNCIONES QUE SE EJECUTARAN EL VIERNES CUANDO CIERRE EL MERCADO
# Traemos el historial de los ultimos 5 dias en una lista para calcular las ganancias, swap y comisiones
async def list_orders_deals(account_id: str, id_account_mt5: int, history_days: int):
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
        # Esperando a que el SDK se sincronice con el estado de la terminal (puede llevar algún tiempo según el tamaño de su historial)'
        await connection.wait_synchronized()

        # Obteniendo el balance de la cuenta
        account_info = await connection.get_account_information()
        balance = account_info['balance']

        orders_deals = await connection.get_deals_by_time_range(datetime.utcnow() - timedelta(days=history_days), datetime.utcnow())
        orders_deals = orders_deals['deals']
        await connection.close()

        print(orders_deals)

        list_orders = []
        trades = []
        balance_change = 0.00
        # filtramos las ordenes
        for order in orders_deals:
            if order['type'] == "DEAL_TYPE_BALANCE":
                balance_change += order['profit']

            if order['type'] == "DEAL_TYPE_BUY" or order['type'] == "DEAL_TYPE_SELL":
                list_orders.append(order)

            if order['entryType'] == "DEAL_ENTRY_OUT":
                # La solucion al problema se coloca aqui
                trades.append(order)

        for i in range(len(trades)):
            # Agregamos a las ordenes de tipo 'DEAL_ENTRY_OUT datos extras desde las ordenes de tipo 'DEAL_ENTRY_IN'
            for j in orders_deals:
                if j['entryType'] == 'DEAL_ENTRY_IN':
                    if trades[i]['positionId'] == j['positionId']:
                        trades[i]['open_time'] = j['time']
                        trades[i]['open_price'] = j['price']
                        trades[i]['commission'] = trades[i]['commission'] + j['commission']

            # Ordenamos los dict y los pasamos a tuplas
            ordered_dict = {}

            ordered_dict['open_time'] = trades[i]['open_time'] - timedelta(hours=6)
            ordered_dict['open_time'] = ordered_dict['open_time'].strftime('%Y-%m-%d %H:%M:%S')
            ordered_dict['open_price'] = trades[i]['open_price']
            ordered_dict['symbol'] = trades[i]['symbol']
            if trades[i]['type'] == 'DEAL_TYPE_BUY':
                ordered_dict['type'] = 'Venta'
            elif trades[i]['type'] == 'DEAL_TYPE_SELL':
                ordered_dict['type'] = 'Compra'
            ordered_dict['volume'] = trades[i]['volume']
            ordered_dict['close_time'] = trades[i]['time'] - timedelta(hours=6)
            ordered_dict['close_time'] = ordered_dict['close_time'].strftime('%Y-%m-%d %H:%M:%S')
            ordered_dict['close_price'] = trades[i]['price']
            ordered_dict['commission'] = trades[i]['commission']
            ordered_dict['swap'] = trades[i]['swap']
            ordered_dict['profit'] = trades[i]['profit']
            ordered_dict['id_account_mt5'] = str(id_account_mt5)

            trades[i] = tuple(ordered_dict.values())

        return {'orders': list_orders, 'trades': trades, 'balance': balance, 'balance_change': balance_change}

    except Exception as err:
        print(api.format_error(err))


def corroborate_management_week(id_user, current_balance, net_profit):
    # Conectamos a la base de datos
    try:
        connection = psycopg2.connect(database=get_secret(
            "DB_NAME"), user=get_secret("USER"), password=get_secret("PASSWORD"))
        cursor = connection.cursor()

    except Exception as err:
        print("Error en la conexión de la base de datos: ", err)
    # Consultamos los datos necesarios para corroborrar la semana de gestión
    try:
        cursor.execute(f"SELECT end_date FROM vps_accountmanagement WHERE id=(SELECT MAX(id) FROM vps_accountmanagement WHERE id_user_id={id_user});")
        end_date_current_week = cursor.fetchall()
    except Exception as err:
        print("Error al consultar en la base de datos: ", err)
    connection.commit()
    print(end_date_current_week)
    now = datetime.now()
    if end_date_current_week:
        # Como end_date del registro es hasta el viernes agregaremos el dia y las horas que faltan para que sea
        # Domingo 19:00 horas que es el inicio de la siguiente semana de gestión
        end_date = end_date_current_week[0][0]
        end_week = datetime(end_date.year, end_date.month, end_date.day, 0, 0)
        end_week = end_week + timedelta(days=2, hours=19)
        
        if now > end_week:
            # Si no estamos dentro de la semana actual del registro creamos un registro con la semana actual.
            today = date.today()
            balance_initial = current_balance - net_profit
            match today.weekday():
                case 0:
                    start_date = today - timedelta(days=1)
                    end_date = today + timedelta(days=4)
                case 1:
                    start_date = today - timedelta(days=2)
                    end_date = today + timedelta(days=3)
                case 2:
                    start_date = today - timedelta(days=3)
                    end_date = today + timedelta(days=2)
                case 3:
                    start_date = today - timedelta(days=4)
                    end_date = today + timedelta(days=1)
                case 4:
                    start_date = today - timedelta(days=5)
                    end_date = today
                case 6:
                    start_date = today
                    end_date = today + timedelta(days=5)
            # Insertamos el nuevo registro de la semana actual en la base de datos
            try:
                cursor.execute(f"INSERT INTO vps_accountmanagement (start_date, end_date, start_balance, withdraw_deposit, end_balance, gross_profit, commission, swap, net_profit, id_user_id) VALUES('{start_date}', '{end_date}', {balance_initial}, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, {id_user})")
            except Exception as err:
                print("Error en la corroborate_management_week() al insertar en la base de datos: ", err)
            connection.commit()
            connection.close()
    else:
        # Si no hay registros en la tabla del usuario creamos un registro con la semana actual.
        today = date.today()
        start_date = ''
        end_date = ''
        balance_initial = current_balance - net_profit
        match today.weekday():
            case 0:
                start_date = today - timedelta(days=1)
                end_date = today + timedelta(days=4)
            case 1:
                start_date = today - timedelta(days=2)
                end_date = today + timedelta(days=3)
            case 2:
                start_date = today - timedelta(days=3)
                end_date = today + timedelta(days=2)
            case 3:
                start_date = today - timedelta(days=4)
                end_date = today + timedelta(days=1)
            case 4:
                if now.hour <= 15:
                    start_date = today - timedelta(days=5)
                    end_date = today
            case 6:
                if now.hour >= 19:
                    start_date = today
                    end_date = today + timedelta(days=5)
        # Insertamos el nuevo registro de la semana actual en la base de datos
        if start_date and end_date:
            try:
                cursor.execute(f"INSERT INTO vps_accountmanagement (start_date, end_date, start_balance, withdraw_deposit, end_balance, gross_profit, commission, swap, net_profit, id_user_id) VALUES('{start_date}', '{end_date}', {balance_initial}, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, {id_user})")
            except Exception as err:
                print("Error en la corroborate_management_week() al insertar en la base de datos: ", err)
            connection.commit()
            connection.close()

# Función para calcular beneficios, comisiones y swap para la tabla de ganancias semanales
async def history_and_profit():

    data_accounts = get_accounts_mt5_database()
    accounts = data_accounts['accounts']

    list_management = []
    trades = []
    for account in accounts:
        id_account_mt5 = account[0]
        id_client_metaapi = account[1]
        id_user = account[2]

        # Traemos el historial de la semana desde metaapi
        today = date.today().weekday()
        match today:
            case 0:
                data = await list_orders_deals(id_client_metaapi, id_account_mt5, 2)
            case 1:
                data = await list_orders_deals(id_client_metaapi, id_account_mt5, 3)
            case 2:
                data = await list_orders_deals(id_client_metaapi, id_account_mt5, 4)
            case 3:
                data = await list_orders_deals(id_client_metaapi, id_account_mt5, 5)
            case 4:
                data = await list_orders_deals(id_client_metaapi, id_account_mt5, 6)
            case 5:
                data = await list_orders_deals(id_client_metaapi, id_account_mt5, 7)
            case 6:
                data = await list_orders_deals(id_client_metaapi, id_account_mt5, 1)

        commissions = 0.00
        swap = 0.00
        profits = 0.00
        for order in data['trades']:
            commissions += order[7]
            swap += order[8]
            profits += order[9]

            # Agregamos los trades a una lista para agregarlos en una sola consulta en la base de datos
            trades.append(order)

        net_profit = (profits - abs(commissions)) + swap
        # Corroboramos que haya un registro de la semana actual de no ser asi creamos un registro nuevo
        corroborate_management_week(id_user, data['balance'], net_profit)
        # dejamos en formato listo para agregar a una base de datos
        management = f"UPDATE vps_accountmanagement SET withdraw_deposit={data['balance_change']}, end_balance={data['balance']}, gross_profit={profits}, commission={commissions}, swap={swap}, net_profit={net_profit}, id_user_id={id_user} WHERE id=(SELECT id FROM vps_accountmanagement WHERE id=(SELECT MAX(id) FROM vps_accountmanagement WHERE id_user_id={id_user}));"

        list_management.append(management)

    data.pop('orders')  # Estas ordenes ya no lo necesitamos y lo borramos
    # Agregamos los strings de los managements
    data['managements'] = list_management
    # Agregamos la info de las cuentas con la conexion a la base de datos
    data['accounts_mt5'] = data_accounts
    # Reescribimos la "data['trades']" con una lista con todos los trades de las demas cuentas
    data['trades'] = trades

    return data


async def operations_database(data: dict):

    connection = data['accounts_mt5']['conexion']
    cursor = connection.cursor()
    managements = data['managements']
    accounts = data['accounts_mt5']['accounts']
    trades = data['trades']

    data_str = ','.join(str(trade) for trade in trades)
    management_str = ' '.join(str(management) for management in managements)
    delete_operations_str = ' '.join(f"DELETE FROM vps_accountoperation WHERE id_account_mt5_id={account[0]};" for account in accounts)

    # Actualizamos los datos de la tabla de "vps_accountmanagement"
    try:
        cursor.execute(management_str)
    except Exception as err:
        print("Error al actualizar datos. Proveniente de la función operations_database(): ", err)
    else:
        print("Datos Actualizados correctamente.")
    connection.commit()

    # Borramos los trades del usuario de la tabla "vps_accountoperation" para agregar la data actualizada
    try:
        cursor.execute(delete_operations_str)
    except Exception as err:
        print("Error al eliminar datos. Proveniente de la función operations_database(): ", err)
    else:
        print("Datos Borrados correctamente.")
    connection.commit()

    # Insertamos los datos de los trades de cada usuario en la tabla "vps_accountoperation"
    try:
        if data_str:
            cursor.execute("INSERT INTO vps_accountoperation (open_time, open_price, symbol, type, volume, close_time, close_price, commission, swap, profit, id_account_mt5_id)"
                       "VALUES " + data_str)
    except Exception as err:
        print("Error al insertar datos. Proveniente de la función operations_database(): ", err)
    else:
        print("Datos Insertados correctamente.")
    connection.commit()
    connection.close()
