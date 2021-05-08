#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dotenv import load_dotenv
import os
from motor.motor_asyncio import AsyncIOMotorClient

# init env #
load_dotenv()

connection_string = os.getenv("connection_string")

database = AsyncIOMotorClient(connection_string)
