import asyncio
import MetaTrader5 as mt5
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk.clients.metaApi.tradeException import TradeException
from datetime import datetime, timedelta, date
import json
import psycopg2

# Funcion para extraer los datos importantes y privados del sistema
with open(r"C:\projects_django\fortuna\secret.json") as f:
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


# Funcion que retorna el valor 'time' para el metodo sort() de las listas y ordenar los trades por fecha de cierre
def sort_trades_by_date(key):
    return key['positionId']


# Función que Unifica en una orden las ordenes cerradas de forma parcial tomando la ultima orden de la 
# position para unificarla.
def unify_partial_orders(trades: list):
    index_list = []
    for trade in trades:
        partial_trades = [trade,]
        for trade2 in trades:
            # Filtramos las ordenes por positions repetidos para saber cuales son las ordenes parciales.
            if trade['positionId'] == trade2['positionId'] and trade['orderId'] != trade2['orderId']:
                if trades.index(trade) not in index_list:
                    index_list.append(trades.index(trade))
                partial_trades.append(trade2)

        data_change = {'volume': 0.00, 'commission': 0.00, 'swap': 0.00, 'profit': 0.00}
        for trade in partial_trades:
            # Para el volumen, precio, comision, swap y el beneficio solo los sumamos.        
            data_change['volume'] += trade['volume']
            data_change['commission'] += trade['commission']
            data_change['swap'] += trade['swap']
            data_change['profit'] += trade['profit']
            # Borramos los trades parciales de la lista de trades   
            trades.remove(trade)

        if partial_trades:
            unified_trade = partial_trades[-1]
            unified_trade['volume'] = round(data_change['volume'], 2)
            unified_trade['commission'] = round(data_change['commission'], 2)
            unified_trade['swap'] = round(data_change['swap'], 2)
            unified_trade['profit'] = round(data_change['profit'], 2)
            # Despues de unificar a un solo trade lo agregamos a la lista de trades.
            trades.append(unified_trade)
            # Ordenamos los trades por fecha de cierre
            trades.sort(key=sort_trades_by_date)
            # Metemos en una lista las indices de los trades unificados para actualizar su precio de cierre en la
            # función de close_price_of_unified_trades()

    return index_list

# Lista de pares que tienen la moneda "JPY" como moneda secundaria.
par_jpy = ["USDJPY", "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY", "NZDJPY"]
# Lista de pares que tienen la moneda "USD" como moneda secundaria.
par_usd = ["AUDUSD","EURUSD", "GBPUSD", "NZDUSD"]
# Lista de pares alternativos y populares
par_alternatives = ["AUDCAD", "AUDCHF", "AUDNZD", "CADCHF", "EURGBP", "EURAUD", "EURCAD", "EURCHF", "EURGBP", "EURNZD", "GBPAUD", "GPBCAD", "GPBCHF", "GBPNZD", "NZDCAD", "NZDCHF", "USDCAD", "USDCHF"]
# Función que modifica el precio de cierre de la orden unificada que eran ordenes cerradas parcialmente.
def change_closing_price(trade: tuple, pips: float):
    if trade[2] in par_jpy:
        if trade[3] == "Compra":
            if trade[9] > 0:
                trade[6] = round(trade[1] + pips, 4)
            else:
                trade[6] = round(trade[1] - pips, 4)

        if trade[3] == "Venta":
            if trade[9] > 0:
                trade[6] = round(trade[1] - pips, 4)
            else:
                trade[6] = round(trade[1] + pips, 4)
    #
    if trade[2] in par_alternatives or trade[2] in par_usd:
        if trade[3] == "Compra":
            if trade[9] > 0:
                trade[6] = round(trade[1] + pips, 6)
            else:
                trade[6] = round(trade[1] - pips, 6)

        if trade[3] == "Venta":
            if trade[9] > 0:
                trade[6] = round(trade[1] - pips, 6)
            else:
                trade[6] = round(trade[1] + pips, 6)


# Función que actualiza los precios de cierre de las trades unificados ya que estos no se pueden cambiar desde
# la función unify_partial_ordes()
def close_price_of_unified_trades(trades: list, index_list: list):
    # Sacamos el precio de cierre dependiendo el par o simbolo de la orden.
    for index in index_list:
        # Sacamos los pares emparejados con el 'JPY' porque su valor por pip es 1000 yenes
        if trades[index][2] in par_jpy:
            pip_value = trades[index][4] / trades[index][1] * 1000
            pips = abs((trades[index][9] / pip_value) / 100)
            # Cambiamos el precio de cierre
            trades[index] = list(trades[index]) #convertimos a lista para modificar el precio de cierre.
            change_closing_price(trades[index], pips)
            trades[index] = tuple(trades[index]) #convertimos de nuevo a tupla para guardarlo en base de datos.

        # Sacamos los pares mas populares que no tienen el "USD" como moneda secundaria.
        if trades[index][2] in par_alternatives:
            pip_value = trades[index][4] / trades[index][1] * 10
            pips = abs((trades[index][9] / pip_value) / 10000)
            # Cambiamos el precio de cierre
            trades[index] = list(trades[index]) #convertimos a lista para modificar el precio de cierre.
            change_closing_price(trades[index], pips)
            trades[index] = tuple(trades[index]) #convertimos de nuevo a tupla para guardarlo en base de datos.
            
        # Sacamos los pares mas populares que tengan el "USD" como moneda secundaria.
        if trades[index][2] in par_usd:
            trades[index] = list(trades[index]) #convertimos a lista para modificar el precio de cierre.
            pip_value = 10 * trades[index][4]
            pips = abs((trades[index][9] / pip_value) / 10000)
            # Cambiamos el precio de cierre
            trades[index] = list(trades[index]) #convertimos a lista para modificar el precio de cierre.
            change_closing_price(trades[index], pips)
            trades[index] = tuple(trades[index]) #convertimos de nuevo a tupla para guardarlo en base de datos.


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

        list_orders = []
        trades = []
        balance_change = 0.00
        # filtramos las ordenes
        for order in orders_deals:
            try:
                if order['type'] == "DEAL_TYPE_BALANCE":
                    balance_change += order['profit']

                if order['type'] == "DEAL_TYPE_BUY" or order['type'] == "DEAL_TYPE_SELL":
                    list_orders.append(order)

                if order['entryType'] == "DEAL_ENTRY_OUT":
                    trades.append(order)
            except Exception as err:
                print("Error al agrupar las ordenes: ", err)

        trades.sort(key=sort_trades_by_date)
        # Unificamos los trades que se hayan cerrado parcialmente.
        index_list = unify_partial_orders(trades=trades)

        # Agregamos a las ordenes de tipo 'DEAL_ENTRY_OUT datos extras desde las ordenes de tipo 'DEAL_ENTRY_IN'
        for i in range(len(trades)):
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
        
        close_price_of_unified_trades(trades, index_list)

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