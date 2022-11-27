import asyncio
from funtions_payment import add_vps_payment_database, disable_mt5_without_paying_vps

# Aqui se ejecutan las funciones que agrega los importes a pagar en las tablas de VPS + COPYTRADING de los
# usuarios y deberia de ejecutarse al menos dos veces al dia.
asyncio.run(add_vps_payment_database())

# Aqui se ejecutan las funciones que desconectan las cuentas mt5 en metaapi por falta de pago de la 
# mensualidad de VPS + COPYTRADING de los usuarios y deberia de ejecutarse al menos dos veces al dia.
asyncio.run(disable_mt5_without_paying_vps())
