from dotenv import load_dotenv
import os
import pymongo

# init env #
load_dotenv()

connection_string = os.getenv("connection_string")

database = pymongo.MongoClient(connection_string)
