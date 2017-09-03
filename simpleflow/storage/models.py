# -*- coding: utf-8 -*-

#    Copyright (C) 2014 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import sqlalchemy as sa
from sqlalchemy.ext import declarative
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.dialects.mysql import TEXT

from simpleutil.utils import timeutils
from simpleutil.utils import uuidutils

from simpleservice.ormdb.models import TableBase
from simpleservice.ormdb.models import InnoDBTableBase

from simpleflow import states
from simpleflow.storage import middleware

SimpleFlowTables = declarative.declarative_base(cls=TableBase)

# Column length limits...
NAME_LENGTH = 255
UUID_LENGTH = 36
STATE_LENGTH = 255
VERSION_LENGTH = 64


class LogBook(SimpleFlowTables):
    created_at = sa.Column(DATETIME, default=timeutils.utcnow)
    updated_at = sa.Column(DATETIME, onupdate=timeutils.utcnow)
    meta = sa.Column(TEXT)
    name = sa.Column(VARCHAR(NAME_LENGTH))
    uuid = sa.Column(CHAR(UUID_LENGTH), primary_key=True, nullable=False,
                     default=uuidutils.generate_uuid)

    __table_args__ = (
            InnoDBTableBase.__table_args__
    )


class FlowDetail(SimpleFlowTables):
    created_at = sa.Column(DATETIME, default=timeutils.utcnow)
    updated_at = sa.Column(DATETIME, onupdate=timeutils.utcnow)
    parent_uuid = sa.Column(sa.ForeignKey('logbooks.uuid', ondelete='CASCADE'))
    meta = sa.Column(TEXT)
    name = sa.Column(VARCHAR(NAME_LENGTH))
    state = sa.Column(VARCHAR(STATE_LENGTH))
    uuid = sa.Column(CHAR(UUID_LENGTH), primary_key=True, nullable=False,
                     default=uuidutils.generate_uuid)

    __table_args__ = (
            InnoDBTableBase.__table_args__
    )


class AtomDetail(SimpleFlowTables):
    created_at = sa.Column(DATETIME, default=timeutils.utcnow)
    updated_at = sa.Column(DATETIME, onupdate=timeutils.utcnow)
    meta = sa.Column(TEXT)
    parent_uuid = sa.Column(sa.ForeignKey('flowdetails.uuid', ondelete='CASCADE'))
    name = sa.Column(VARCHAR(NAME_LENGTH))
    version = sa.Column(VARCHAR(VERSION_LENGTH))
    state = sa.Column(VARCHAR(STATE_LENGTH))
    uuid = sa.Column(CHAR(UUID_LENGTH), primary_key=True, nullable=False,
                     default=uuidutils.generate_uuid)
    failure = sa.Column(TEXT)
    results = sa.Column(TEXT)
    revert_results = sa.Column(TEXT)
    revert_failure = sa.Column(TEXT)
    atom_type = sa.Column(ENUM(*middleware.ATOM_TYPES,
                               name='atom_types'))
    intention = sa.Column(ENUM(*states.INTENTIONS,
                               name='intentionS'))

    __table_args__ = (
            InnoDBTableBase.__table_args__
    )
