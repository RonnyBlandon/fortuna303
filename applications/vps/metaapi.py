import asyncio

from numpy import rint
from fortuna_303.settings.local import get_secret
from metaapi_cloud_sdk import MetaApi, CopyFactory
from metaapi_cloud_sdk.clients.metaApi.tradeException import TradeException
from datetime import datetime, timedelta, date
import psycopg2

app_token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI3ZTYwMGI2ZDljYmM4ZTkwOTU0YzI2MGE2MjUzOThhMiIsInBlcm1pc3Npb25zIjpbXSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaWF0IjoxNjYyNzcwNjIyLCJyZWFsVXNlcklkIjoiN2U2MDBiNmQ5Y2JjOGU5MDk1NGMyNjBhNjI1Mzk4YTIifQ.UTYs5SZ5_UDLBnA_bQdlXtLtk1dTcQA0MVJ2O0mdsu2KYIaVOzT19Vm5XDsGfQYO856lNJPu9RkztRABRpJW1cbw8zkWU9-IAh-L-5MFuC-mVkNkSCLDj3ziAbx5w7niN1wEOaCozg_y-MXrXCa972LwWaq4yxJ8IjxxhHGZSFs2DYQm9F7ehRCdjqEh-y9zQHKozVBTYwnFvIxoN5WwUqqyhCmWa_lpT5GE-YWrjO3VaHW0CbIm3PCzlL5b4qMTPuifoECpeJ5aBX17qevsagJ2TrS_NDet9i2dEBqKGGPGRaB84wIOruR1C7e5AnQ8haef8gqChWOBseKfo0dwnd_KntDwvMkWsxMq1rpvpGBia9WELyNz_jDvApB6kOJfmHO0p6ue9tilEJZJ4iZ9KDEGzqzy-44yweJtkq_hAFGt5HKFXrD2loPnjtpZ0EaMieNEDrn8YRM3bRnlixtlGm67iuqnrKq9KHqR7QZyA5I3SvkO-g4PvA0Cyi_QmyZ3yijlREzbvkOF15kJ2ncWl_Mm6SJjtksVKDK3u2QUlnj2ZYtOTCLgsQw9wP2tc9o5gTgLDU3CVQdoM6sc5BQpQzaQ0Bo-XHmozyCe3D-_q5JMe-rUt_vk05qqVwly33S2RO4j_2iqEGX5xH3Gm0NrzPWDIfCSxnncYXb7V_lmNA4"
master_account_id = "7bfe546b-1a05-4d2d-8f7d-744206ccab1c"
slave_account_id = "5ad1bbc5-0eae-4f1b-a2d7-198a1d334284"


async def create_server_mt5(name, login, password, server):
    api = MetaApi(app_token)

    try:
        account = await api.metatrader_account_api.create_account(account={
            'name': name,
            'type': 'cloud',
            'login': login,
            'platform': 'mt5',
            'region': 'new-york',
            # password can be investor password for read-only access
            'password': password,
            'server': server,
            'application': 'MetaApi',
            'copyFactoryRoles': ['SUBSCRIBER'],
            'magic': 0,
            'quoteStreamingIntervalInSeconds': 2.5,  # set to 0 to receive quote per tick
            # set this field to 'high' value if you want to increase uptime of your account (recommended for production environments)
            'reliability': 'high'
        })
        return {'id': account.id, 'access_token': account.access_token}

    except Exception as err:
        # errores de proceso
        if hasattr(err, 'details'):
            # devuelto si no se ha encontrado el archivo de servidor para el nombre de servidor especificado
            # se recomienda verificar el nombre del servidor o crear la cuenta usando un perfil de aprovisionamiento
            if err.details == 'E_SRV_NOT_FOUND':
                print(err)
            # devuelto si el servidor no se pudo conectar con el corredor utilizando sus credenciales
            # Se recomienda verificar su nombre de usuario y contraseña.
        elif err.details == 'E_AUTH':
            print(err)
            # devuelto si el servidor no ha podido detectar la configuración del intermediario
            # se recomienda volver a intentarlo más tarde o crear la cuenta con un perfil de aprovisionamiento

        elif err.details == 'E_SERVER_TIMEZONE':
            print(err)

        print(err.details)


async def configure_copyfactory(slave_account_id):
    api = MetaApi(app_token)
    copy_factory = CopyFactory(app_token)

    try:
        master_metaapi_account = await api.metatrader_account_api.get_account(master_account_id)
        if (master_metaapi_account is None) or master_metaapi_account.copy_factory_roles is None or 'PROVIDER' not \
                in master_metaapi_account.copy_factory_roles:
            raise Exception('Please specify PROVIDER copyFactoryRoles value in your MetaApi '
                            'account in order to use it in CopyFactory API')

        slave_metaapi_account = await api.metatrader_account_api.get_account(slave_account_id)
        if (slave_metaapi_account is None) or slave_metaapi_account.copy_factory_roles is None or 'SUBSCRIBER' not \
                in slave_metaapi_account.copy_factory_roles:
            raise Exception('Please specify SUBSCRIBER copyFactoryRoles value in your MetaApi '
                            'account in order to use it in CopyFactory API')

        configuration_api = copy_factory.configuration_api
        strategies = await configuration_api.get_strategies()
        strategy = next(
            (s for s in strategies if s['accountId'] == master_metaapi_account.id), None)
        if strategy:
            strategy_id = strategy['_id']
        else:
            strategy_id = await configuration_api.generate_strategy_id()
            strategy_id = strategy_id['id']

        # create subscriber
        suscriber = await configuration_api.update_subscriber(slave_metaapi_account.id, {
            'name': 'Esto es un test de suscribcion',
            'subscriptions': [
                {
                    'strategyId': strategy_id,
                    'multiplier': 1
                }
            ]
        })
        return suscriber
    except Exception as err:
        print(api.format_error(err))


async def delete_server_mt5(account_id):
    api = MetaApi(app_token)

    account = await api.metatrader_account_api.get_account(account_id=account_id)

    try:
        await account.remove()

    except Exception as err:
        print(err.details)

