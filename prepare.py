#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from motor.motor_asyncio import AsyncIOMotorClient

connection_string = os.getenv("connection_string")

database = AsyncIOMotorClient(connection_string)
