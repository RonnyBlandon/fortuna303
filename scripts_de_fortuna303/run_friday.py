import asyncio
from funtions_payment import add_trader_payment_database, disable_mt5_without_paying_trader

# Aqui se ejecutan las funciones que agrega los importes a pagar en las tablas de Gestion de Cuentas de mt5
# de los usuarios y deberia de ejecutarse al menos dos veces al dia.
asyncio.run(add_trader_payment_database())

# Aqui se ejecutan las funciones que desconectan las cuentas mt5 en metaapi por falta de pago semanal de la
# tabla de Gestion de Cuentas de mt5 a los usuarios y deberia de ejecutarse al menos dos veces al dia.
asyncio.run(disable_mt5_without_paying_trader())
