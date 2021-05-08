#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# init env #
load_dotenv()

connection_string = os.getenv("connection_string")

database = AsyncIOMotorClient(connection_string)
