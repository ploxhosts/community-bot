#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
            Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from typing import Any, Dict, Generator, Iterable, Optional, Union, Tuple, List

from aiosqlite.core import Connection
from aiosqlite.cursor import Cursor

from .utils import build_query, dict_factory


class MotorSqliteTable(object):
    def __init__(self, conn: Connection, table: str) -> None:
        self.db = None
        self.conn = conn
        self.table = table

        # SQL queries
        self.select_sql = f'SELECT * FROM {table} WHERE '
        self.update_sql = f'UPDATE {table} SET '
        self.insert_sql = f'INSERT INTO {table} '
        self.delete_sql = f'DELETE FROM {table} WHERE '
        self.drop_sql = f'DROP TABLE {table}'
        self.count_sql = f'SELECT COUNT(*) FROM {table}'

    async def _execute(
        self, query: str, values: Iterable[Any] = None
    ) -> Cursor:

        if self.db is None:
            self.db = await self.conn

        self.db.row_factory = dict_factory  # type: ignore
        cursor = await self.db.execute(query, values)
        await self.db.commit()

        return cursor

    async def find(
        self, _dict: Dict[str, Any]
    ) -> Generator[Dict[str, Union[str, int]], None, None]:
        if not _dict:
            cursor = await self._execute(self.select_sql.split(' WHERE')[0])
        else:
            query, values = build_query(self.select_sql, _dict)
            cursor = await self._execute(query, values)

        # async generator to keep it similar to motor api
        for res in await cursor.fetchall():
            yield res

    async def find_one(
        self, _dict: Dict[str, Any]
    ) -> Optional[Dict[str, Union[str, int]]]:

        try:
            return await self.find(_dict).__anext__()
        except StopAsyncIteration:
            return None

    def _update(
        self, _dict: Dict[str, Any], opts: Dict[str, Dict[str, Any]]
    ) -> Tuple[str, List[Any]]:
        query, values = build_query(self.update_sql, opts['$set'], ' = ?,')
        # such an ugly way to remove trailing `,` and add `WHERE`
        query = query[:-1] + ' WHERE '

        query, x = build_query(query, _dict)
        values += x

        return query, values

    async def update(
        self, _dict: Dict[str, Any], opts: Dict[str, Dict[str, Any]],
        one: bool = False
    ) -> int:
        query, values = self._update(_dict, opts)
        cursor = await self._execute(query, values)

        if one:
            query += ' LIMIT 1'

        return cursor.rowcount

    async def update_one(
        self, _dict: Dict[str, Any], opts: Dict[str, Dict[str, Any]]
    ) -> bool:
        return await self.update(_dict, opts, True) == 1

    async def insert(self, data: Dict[str, Any]) -> int:
        query = f"{self.insert_sql}({','.join(data.keys())}) VALUES ("
        query, values = build_query(query, data, '?,', False)

        # such an ugly way to remove trailing `,` and add `)`
        query = query[:-1] + ')'

        cursor = await self._execute(query, values)

        return cursor.rowcount

    async def insert_one(self, data: Dict[str, Any]) -> bool:
        return await self.insert(data) == 1

    async def execute_raw(
        self, sql: str, params: Iterable[Any] = None
    ) -> Cursor:
        return await self._execute(sql, params)

    async def drop_collection(self) -> Cursor:
        return await self._execute(self.drop_sql)

    async def delete(self, data: Dict[str, Any], one: bool = False) -> int:
        query, values = build_query(self.delete_sql, data)

        if one:
            query += ' LIMIT 1'

        cursor = await self._execute(query, values)

        return cursor.rowcount

    async def delete_one(self, data: Dict[str, Any]) -> bool:
        return await self.delete(data, True) == 1

    async def count_documents(self, _dict: Dict[str, Any] = None) -> int:
        query = self.count_sql
        values = None

        if _dict is not None:
            query += ' WHERE '
            query, values = build_query(query, _dict)

        cursor = await self._execute(query, values)

        return (await cursor.fetchone())['COUNT(*)']
