import asyncio
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk.clients.metaApi.tradeException import TradeException
from datetime import datetime, timedelta

token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI3ZTYwMGI2ZDljYmM4ZTkwOTU0YzI2MGE2MjUzOThhMiIsInBlcm1pc3Npb25zIjpbXSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaWF0IjoxNjYyNzcwNjIyLCJyZWFsVXNlcklkIjoiN2U2MDBiNmQ5Y2JjOGU5MDk1NGMyNjBhNjI1Mzk4YTIifQ.UTYs5SZ5_UDLBnA_bQdlXtLtk1dTcQA0MVJ2O0mdsu2KYIaVOzT19Vm5XDsGfQYO856lNJPu9RkztRABRpJW1cbw8zkWU9-IAh-L-5MFuC-mVkNkSCLDj3ziAbx5w7niN1wEOaCozg_y-MXrXCa972LwWaq4yxJ8IjxxhHGZSFs2DYQm9F7ehRCdjqEh-y9zQHKozVBTYwnFvIxoN5WwUqqyhCmWa_lpT5GE-YWrjO3VaHW0CbIm3PCzlL5b4qMTPuifoECpeJ5aBX17qevsagJ2TrS_NDet9i2dEBqKGGPGRaB84wIOruR1C7e5AnQ8haef8gqChWOBseKfo0dwnd_KntDwvMkWsxMq1rpvpGBia9WELyNz_jDvApB6kOJfmHO0p6ue9tilEJZJ4iZ9KDEGzqzy-44yweJtkq_hAFGt5HKFXrD2loPnjtpZ0EaMieNEDrn8YRM3bRnlixtlGm67iuqnrKq9KHqR7QZyA5I3SvkO-g4PvA0Cyi_QmyZ3yijlREzbvkOF15kJ2ncWl_Mm6SJjtksVKDK3u2QUlnj2ZYtOTCLgsQw9wP2tc9o5gTgLDU3CVQdoM6sc5BQpQzaQ0Bo-XHmozyCe3D-_q5JMe-rUt_vk05qqVwly33S2RO4j_2iqEGX5xH3Gm0NrzPWDIfCSxnncYXb7V_lmNA4"
accountId = "17d40174-0417-49fc-aadb-16c05370aa5c"

async def test_meta_api_synchronization():
    api = MetaApi(token)
    try:
        account = await api.metatrader_account_api.get_account(accountId)
        initial_state = account.state
        deployed_states = ['DEPLOYING', 'DEPLOYED']

        if initial_state not in deployed_states:
            #  espere hasta que la cuenta esté desplegada y conectada al corredor
            print('Deploying account')
            await account.deploy()

        print('Esperando a que el servidor API se conecte al intermediario (puede tardar un par de minutos)')
        await account.wait_connected()

        # conectarse a la API de MetaApi
        connection = account.get_rpc_connection()
        await connection.connect()

        # espere hasta que el estado del terminal se sincronice con el estado local
        print('Esperando a que el SDK se sincronice con el estado de la terminal (puede llevar algún tiempo según el tamaño de su historial)')
        await connection.wait_synchronized()

        # invoque la API de RPC (reemplace los números de boleto con los números de boleto reales que existen en su cuenta de MT)
        print('Prueba de la API RPC de MetaAPI')
        print('account information:', await connection.get_account_information())
        print('positions:', await connection.get_positions())
        # print(await connection.get_position('1234567'))
        print('open orders:', await connection.get_orders())
        # print(await connection.get_order('1234567'))
        print('history orders by ticket:', await connection.get_history_orders_by_ticket('1234567'))
        print('history orders by position:', await connection.get_history_orders_by_position('1234567'))
        print('history orders (~last 3 months):',
              await connection.get_history_orders_by_time_range(datetime.utcnow() - timedelta(days=90),
                                                                datetime.utcnow()))
        print('history deals by ticket:', await connection.get_deals_by_ticket('1234567'))
        print('history deals by position:', await connection.get_deals_by_position('1234567'))
        print('history deals (~last 3 months):',
              await connection.get_deals_by_time_range(datetime.utcnow() - timedelta(days=90), datetime.utcnow()))
        print('server time', await connection.get_server_time())

        # calculate margin required for trade
        print('margen requerido para el trade', await connection.calculate_margin({
            'symbol': 'GBPUSD',
            'type': 'ORDER_TYPE_BUY',
            'volume': 0.1,
            'openPrice': 1.1
        }))

        # trade
        print('Envío de orden pendiente')
        try:
            result = await connection.create_limit_buy_order('GBPUSD', 0.07, 1.0, 0.9, 2.0,
                                                             {'comment': 'comm', 'clientId': 'TE_GBPUSD_7hyINWqAlE'})
            print('Trade successful, result code is ' + result['stringCode'])
        except Exception as err:
            print('Trade failed with error:')
            print(api.format_error(err))
        if initial_state not in deployed_states:
            # undeploy account if it was undeployed
            print('Undeploying account')
            await connection.close()
            await account.undeploy()

    except Exception as err:
        print(api.format_error(err))
    exit()

asyncio.run(test_meta_api_synchronization())
