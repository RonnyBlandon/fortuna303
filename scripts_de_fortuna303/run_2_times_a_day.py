import asyncio
from funtions_payment import add_vps_payment_database, disable_mt5_without_paying_vps, add_forex_payment_database, add_stock_payment_database

asyncio.run(add_vps_payment_database())

asyncio.run(disable_mt5_without_paying_vps())

asyncio.run(add_forex_payment_database())

asyncio.run(add_stock_payment_database())
