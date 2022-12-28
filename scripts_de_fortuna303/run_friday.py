import asyncio
from funtions_payment import add_trader_payment_database, disable_mt5_without_paying_trader

# Aqui se ejecutan las funciones que agrega los importes a pagar en laS tablas de GESTION DE CUENTAS MT5 de los
# usuarios y deberia de ejecutarse los viernes a la hora que cierra el mercado de divisas.
asyncio.run(add_trader_payment_database())

# Aqui se ejecutan las funciones que desconectan las cuentas mt5 en metaapi por falta de pago semanal de la
# tabla de Gestion de Cuentas de mt5 a los usuarios y deberia de ejecutarse los viernes a la hora cierra el mercado.
asyncio.run(disable_mt5_without_paying_trader())
