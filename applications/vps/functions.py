from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import MetaTrader5 as mt5
import pandas as pd
# functions own
from fortuna_303.settings.base import get_secret

""" Funciones con la api de Metatrader 5 """

def connect_terminal():
    # establecemos la conexión con el terminal MetaTrader 5
    if not mt5.initialize(path="C:\\Program Files\\Traders Way MetaTrader 5\\terminal64.exe"):
        print("initialize() failed, error code =", mt5.last_error())
        quit()


def trading_history():
    account = int(get_secret("ACCOUNT_MOTHER"))
    password = get_secret("ACCOUNT_MOTHER_PASSWORD")
    server = get_secret("ACCOUNT_MOTHER_SERVER")

    history_orders = None

    connect_terminal()
    authorized = mt5.login(account, password, server)

    if authorized:

        # obtenemos el número de órdenes en la historia en un periodo de 4 semanas
        time = datetime.now()
        from_date = time - timedelta(weeks=4)
        to_date = time + timedelta(days=1)
        history_orders = mt5.history_deals_get(from_date, to_date)

    if history_orders == None:
        return f"Hubo un error en la conexion con la cuenta {account}. El codigo de error es {mt5.last_error()} "

    elif len(history_orders) > 0:

        mt5.shutdown()
        # Metemos en dataframe los datos extraidos de la terminal y solo tomamos los datos necesarios
        df = pd.DataFrame(list(history_orders),
                          columns=history_orders[0]._asdict().keys())
        df.drop(['magic', 'commission', 'swap', 'external_id', 'order',
                'time_msc', 'ticket', 'reason', 'comment', 'fee'], axis=1, inplace=True)
        df['type'] = df['type'].astype('string')
        df.loc[df['type'] == '0', 'type'] = 'Venta'
        df.loc[df['type'] == '1', 'type'] = 'Compra'
        df['time'] = pd.to_datetime(df['time'], unit='s')
        list_data = df.to_dict('records')

        data = []  # Creamos una lista vacia para agregar los dict con los datos de la orden
        for register in list_data:
            if register['entry'] == 1:
                # usamos insert() para ordenar la lista de forma desendente
                data.insert(0, register)

        # Agregamos a las ordenes de salida datos extras de las ordenes de entrada
        for i in range(len(data)):
            for j in list_data:
                if j['entry'] == 0:
                    if data[i]['position_id'] == j['position_id']:
                        data[i]['open_time'] = j['time']
                        data[i]['open_price'] = j['price']

        # Reordenamos las claves de los dicts tomando solo las claves que se mostraran en el template
        ordered_data = []
        for i in range(len(data)):
            try:
                ordered_dicts = {}
                ordered_dicts['open_time'] = data[i]['open_time']
                ordered_dicts['open_price'] = round(data[i]['open_price'], 5)
                ordered_dicts['symbol'] = data[i]['symbol']
                ordered_dicts['type'] = data[i]['type']
                ordered_dicts['volume'] = data[i]['volume']
                ordered_dicts['time'] = data[i]['time']
                ordered_dicts['close_price'] = round(data[i]['price'], 5)
                ordered_dicts['profit'] = round(data[i]['profit'], 2)
            except Exception as err:
                print("Error al ordenar los ordered_dicts: ", err)

            ordered_data.append(ordered_dicts)

        return ordered_data


""" Funciones generales de vps """

# Funcion para encriptar los password de las cuentas mt5
def encrypt_password(password):

    key = get_secret("KEY_TO_ENCRYPT_AND_DECRYPT")
    object_cifrado = Fernet(key)
    password_encrypt = object_cifrado.encrypt(str.encode(password))

    return password_encrypt


# Funcion para desencriptar los password de las cuentas mt5
def decrypt_password(password: bytes):
    key = get_secret("KEY_TO_ENCRYPT_AND_DECRYPT")
    object_cifrado = Fernet(key)
    decrypted_text_bytes = object_cifrado.decrypt(password)
    decrypted_text = decrypted_text_bytes.decode()
    return decrypted_text


#  Verificando la fecha y hora que deben estar habilitados los botones de agregar y borrar cuenta mt5
def active_buttons_time():
    today = datetime.now()
    match today.weekday():
        case 4:
            if today.hour >= 15:
                return True
            else:
                return False
        case 5:
            return True
        case 6:
            if today.hour < 19:
                return True
            else:
                return False
        case _:
            return False
