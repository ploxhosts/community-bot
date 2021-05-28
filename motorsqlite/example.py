#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

from src import MotorSqlite


async def test():
    """
    This test function assumes you have a sqlite .db file in data/
    called `test.db` with a table called `posts` with a column called `key`
    with an existing `key` with the value `exists`
    """

    db = database.test
    posts = db.posts

    # None
    assert(await posts.find_one({'key': 'foo'}) is None)

    # {'key': 'exists'}
    assert(await posts.find_one({'key': 'exists'}) == {'key': 'exists'})

    # <async_generator object MotorSqliteTable.find at 0xxxxxxxxxxxxx>
    print(posts.find({'key': 'exists'}))

    # {'key': 'exists'}
    async for x in posts.find({'key': 'exists'}):
        assert(x == {'key': 'exists'})

    # 1
    assert(await posts.update(
        {'key': 'exists'},
        {'$set': {'key': 'value'}},
    ) == 1)

    # True
    assert(await posts.update_one(
        {'key': 'value'},
        {'$set': {'key': 'changed'}},
    ))

    # 1
    assert(await posts.update(
        {'key': 'changed'},
        {'$set': {'key': 'exists'}},
    ) == 1)

    # 1
    assert(await posts.insert_one({'key': 'inserted'}) == 1)

    # 1
    assert(await posts.insert({'key': 'inserted1'}) == 1)

    # 1
    assert(await posts.delete_one({'key': 'inserted1'}))

    # TODO(blaze): insert_many()
    for _ in range(3):
        assert(await posts.insert({'key': 'inserted2'}) == 1)

    # 3
    assert(await posts.delete({'key': 'inserted2'}) == 3)

    print('tests passed.')

database = MotorSqlite()

asyncio.run(test())
