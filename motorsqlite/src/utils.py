#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
            Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from typing import Any, Dict, List, Tuple, Union

from aiosqlite.cursor import Cursor


def build_query(
    query: str, _dict: Dict[str, Any], build: str = " = ?", _key: bool = True,
) -> Tuple[str, List[Any]]:
    values: List[Any] = []

    for key, value in _dict.items():
        if _key:
            query += key

        query += build
        values.append(value)

    return query, values


def dict_factory(
    cursor: Cursor, row: Tuple[Union[str, int]]
) -> Dict[str, Union[str, int]]:
    _dict = {}

    for i, value in enumerate(cursor.description):
        _dict[value[0]] = row[i]

    return _dict
