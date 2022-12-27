import asyncio
from numpy import rint
from fortuna_303.settings.base import get_secret
from metaapi_cloud_sdk import MetaApi, CopyFactory
from metaapi_cloud_sdk.clients.metaApi.tradeException import TradeException
from datetime import datetime, date, timedelta
from django.contrib import messages
from applications.vps.models import AccountManagement

app_token = get_secret("METAAPI_TOKEN")

async def create_server_mt5(name: str, login: int, password: str, server: str, level: int, request):
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
        # Despues de crear la cuenta se verifica si la cuenta esta entre los limites del nivel de usuario
        if account:
            connection = account.get_rpc_connection()
            await connection.connect()
            await connection.wait_synchronized()

            account_info = await connection.get_account_information()
            balance = account_info['balance']

            if balance < level.min_balance or balance > level.max_balance:
                try:
                    asyncio.run(delete_server_mt5(account.id))
                except Exception as err:
                    messages.add_message(request=request, level=messages.ERROR, message=f'Fallo en la creación y conexión de la cuenta. El balance de la cuenta debe estar entre {level.min_balance} y {level.max_balance} dolares.')
                    print(f"La cuenta con el id_client_metaapi {account.id} no fue encontrada o no existe.")
        else:
            messages.add_message(request=request, level=messages.ERROR, message='Fallo en la creación y conexión de la cuenta. Los datos de la cuenta son incorrectos.')

        return {'id': account.id, 'balance': balance}

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


async def configure_copyfactory(slave_account_id, balance, id_user):
    api = MetaApi(app_token)
    copy_factory = CopyFactory(app_token)

    try:
        provider_accounts = await api.metatrader_account_api.get_accounts(accounts_filter={'copyFactoryRoles': ['PROVIDER']})
        if provider_accounts:
            master_metaapi_account = provider_accounts[0]

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

