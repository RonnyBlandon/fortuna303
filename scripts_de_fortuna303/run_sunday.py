from funtions_panel_user import balance_initial
import asyncio

# Aqui se ejecutan las funciones que inicializan la semana a la hora de abrir el mercado

# Iniciamos las semana de gestion agregando otra fila de la semana actual a la tabla de "Ganancias Semanales"
# a las cuentas mt5 conectadas a metaapi.
asyncio.run(balance_initial())
