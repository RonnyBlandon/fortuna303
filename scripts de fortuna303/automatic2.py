from funtions import history_and_profit, operations_database
import asyncio

data = asyncio.run(history_and_profit())
asyncio.run(operations_database(data))
