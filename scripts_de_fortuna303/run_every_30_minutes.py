from funtions_panel_user import history_and_profit, operations_database
import asyncio

# Aqui se ejecutan las funciones que actualizan las tablas de "Ganancias Semanales" e "Historial de 
# operaciones de la cuenta mt5" del panel de usuario cada 30 minutos.

data = asyncio.run(history_and_profit())
asyncio.run(operations_database(data))
