import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
# init env #

load_dotenv()

connection_string = os.getenv("connection_string")





database = AsyncIOMotorClient(connection_string)
