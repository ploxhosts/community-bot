#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
            Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

import os

from aiosqlite.core import Connection
import aiosqlite

from .table import MotorSqliteTable


class MotorSqliteDatabase(object):
    def __init__(self, database: Connection) -> None:
        self.db = database

    def __getattr__(self, name: str) -> MotorSqliteTable:
        """ Creates a "table" object """
        return MotorSqliteTable(self.db, name)


class MotorSqlite(object):
    def __init__(self) -> None:
        pass

    def __getattr__(self, name: str) -> MotorSqliteDatabase:
        """ Creates a "database" object """
        db = aiosqlite.connect(os.path.join('data', f'{name}.db'))

        return MotorSqliteDatabase(db)
