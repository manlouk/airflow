#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import json
from typing import List, NamedTuple

from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from airflow.models.connection import Connection


class ConnectionCollectionItemSchema(SQLAlchemySchema):
    """Schema for a connection item"""

    class Meta:
        """Meta"""

        model = Connection

    connection_id = auto_field('conn_id', required=True)
    conn_type = auto_field(required=True)
    description = auto_field()
    host = auto_field()
    login = auto_field()
    schema = auto_field()
    port = auto_field()


class ConnectionSchema(ConnectionCollectionItemSchema):
    """Connection schema"""

    password = auto_field(load_only=True)
    extra = fields.Method('serialize_extra', deserialize='deserialize_extra')

    @staticmethod
    def serialize_extra(obj: Connection):
        if obj.extra is None:
            return
        from airflow.utils.log.secrets_masker import redact

        try:
            extra = json.loads(obj.extra)
            return json.dumps(redact(extra))
        except json.JSONDecodeError:
            # we can't redact fields in an unstructured `extra`
            return obj.extra

    @staticmethod
    def deserialize_extra(value):  # an explicit deserialize method is required for field.Method
        return value


class ConnectionCollection(NamedTuple):
    """List of Connections with meta"""

    connections: List[Connection]
    total_entries: int


class ConnectionCollectionSchema(Schema):
    """Connection Collection Schema"""

    connections = fields.List(fields.Nested(ConnectionCollectionItemSchema))
    total_entries = fields.Int()


class ConnectionTestSchema(Schema):
    """connection Test Schema"""

    status = fields.Boolean(required=True)
    message = fields.String(required=True)


connection_schema = ConnectionSchema()
connection_collection_item_schema = ConnectionCollectionItemSchema()
connection_collection_schema = ConnectionCollectionSchema()
connection_test_schema = ConnectionTestSchema()
