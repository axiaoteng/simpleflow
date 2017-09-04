# -*- coding: utf-8 -*-

#    Copyright (C) 2012 Yahoo! Inc. All Rights Reserved.
#    Copyright (C) 2013 Rackspace Hosting All Rights Reserved.
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

from sqlalchemy import exc as sa_exc

from simpleutil.log import log as logging
from simpleservice.ormdb import api as dbapi

from simpleflow import exceptions as exc

from simpleflow.storage import base
from simpleflow.storage import middleware
from simpleflow.storage.models import LogBook
from simpleflow.storage.models import FlowDetail
from simpleflow.storage.models import AtomDetail


LOG = logging.getLogger(__name__)


class _Alchemist(object):
    """Internal <-> external row <-> objects + other helper functions.

    NOTE(harlowja): for internal usage only.
    """
    # def __init__(self, tables):
    #     self._tables = tables

    @staticmethod
    def convert_flow_detail(row):
        return middleware.FlowDetail.from_dict(dict(row.items()))

    @staticmethod
    def convert_book(row):
        return middleware.LogBook.from_dict(dict(row.items()))

    @staticmethod
    def convert_atom_detail(row):
        row = dict(row.items())
        atom_cls = middleware.atom_detail_class(row.pop('atom_type'))
        return atom_cls.from_dict(row)

    def atom_query_iter(self, session, parent_uuid):
        query = dbapi.model_query(session, AtomDetail).filter_by(parent_uuid=parent_uuid)
        for row in query:
            yield self.convert_atom_detail(row)

    def flow_query_iter(self, session, parent_uuid):
        query = dbapi.model_query(session, FlowDetail).filter_by(parent_uuid=parent_uuid)
        for row in query:
            yield self.convert_flow_detail(row)

    def populate_book(self, session, book):
        for fd in self.flow_query_iter(session, book.uuid):
            book.add(fd)
            self.populate_flow_detail(session, fd)

    def populate_flow_detail(self, session, fd):
        for ad in self.atom_query_iter(session, fd.uuid):
            fd.add(ad)


class Connection(base.Connection):
    def __init__(self, session):
        self.session = session
        self._converter = _Alchemist()

    def _insert_flow_details(self, fd, parent_uuid):
        value = fd.to_dict()
        value['parent_uuid'] = parent_uuid
        flowdetail = FlowDetail(**value)
        self.session.add(flowdetail)
        self.session.flush()
        for ad in fd:
            self._insert_atom_details(ad, fd.uuid)

    def _insert_atom_details(self, ad, parent_uuid):
        value = ad.to_dict()
        value['parent_uuid'] = parent_uuid
        value['atom_type'] = middleware.atom_detail_type(ad)
        atomdetail = AtomDetail(**value)
        self.session.add(atomdetail)
        self.session.flush()

    def _update_atom_details(self, ad, e_ad):
        e_ad.merge(ad)
        query = dbapi.model_query(self.session, AtomDetail).filter_by(uuid=e_ad.uuid)
        query.update(e_ad.to_dict())

    def update_atom_details(self, atom_detail):
        try:
            # atomdetails = self._tables.atomdetails
            with self.session.begin():
                query = dbapi.model_query(self.session, AtomDetail).filter_by(uuid=atom_detail.uuid)
                atomdetail = query.one_or_none()
                if not atomdetail:
                    raise exc.NotFound("No atom details found with uuid '%s'" % atom_detail.uuid)
                e_ad = self._converter.convert_atom_detail(atomdetail)
                self._update_atom_details(atom_detail, e_ad)
                return e_ad
        except sa_exc.SQLAlchemyError:
            exc.raise_with_cause(exc.StorageFailure,
                                 "Failed updating atom details"
                                 " with uuid '%s'" % atom_detail.uuid)

    def _update_flow_details(self, fd, e_fd):
        e_fd.merge(fd)
        query = dbapi.model_query(self.session, FlowDetail).filter_by(uuid=e_fd.uuid)
        query.update(e_fd.to_dict())
        for ad in fd:
            e_ad = e_fd.find(ad.uuid)
            if e_ad is None:
                e_fd.add(ad)
                self._insert_atom_details(ad, fd.uuid)
            else:
                self._update_atom_details(ad, e_ad)

    def update_flow_details(self, flow_detail):
        try:
            # flowdetails = self._tables.flowdetails
            with self.session.begin():
                query = dbapi.model_query(self.session, FlowDetail).filter_by(uuid=flow_detail.uuid)
                flowdetail = query.one_or_none()
                if not flowdetail:
                    raise exc.NotFound("No flow details found with uuid '%s'" % flow_detail.uuid)
                e_fd = self._converter.convert_flow_detail(flowdetail)
                self._converter.populate_flow_detail(self.session, e_fd)
                self._update_flow_details(flow_detail, e_fd)
                return e_fd
        except sa_exc.SQLAlchemyError:
            exc.raise_with_cause(exc.StorageFailure,
                                 "Failed updating flow details with"
                                 " uuid '%s'" % flow_detail.uuid)

    def destroy_logbook(self, book_uuid):
        try:
            with self.session.begin():
                query = dbapi.model_query(self.session, LogBook).filter_by(uuid=book_uuid)
                if query.delete().rowcount == 0:
                    raise exc.NotFound("No logbook found with uuid '%s'" % book_uuid)
        except sa_exc.DBAPIError:
            exc.raise_with_cause(exc.StorageFailure,
                                 "Failed destroying logbook '%s'" % book_uuid)

    def save_logbook(self, book):
        try:
            with self.session.begin():
                query = dbapi.model_query(self.session, LogBook).filter_by(uuid=book.uuid)
                logbook = query.one_or_none()
                if logbook:
                    e_lb = self._converter.convert_book(logbook)
                    self._converter.populate_book(self.session, e_lb)
                    e_lb.merge(book)
                    logbook.update(e_lb.to_dict())
                    for fd in book:
                        e_fd = e_lb.find(fd.uuid)
                        if e_fd is None:
                            e_lb.add(fd)
                            self._insert_flow_details(fd, e_lb.uuid)
                        else:
                            self._update_flow_details(fd, e_fd)
                    return e_lb
                else:
                    self.session.add(LogBook(**book.to_dict()))
                    self.session.flush()
                    for fd in book:
                        self._insert_flow_details(fd, book.uuid)
                    return book
        except sa_exc.DBAPIError:
            exc.raise_with_cause(
                exc.StorageFailure,
                "Failed saving logbook '%s'" % book.uuid)

    def get_logbook(self, book_uuid, lazy=False):
        try:
            with self.session.begin():
                query = dbapi.model_query(self.session, LogBook).filter_by(uuid=book_uuid)
                logbook = query.one_or_none()
                if not logbook:
                    raise exc.NotFound("No logbook found with"
                                       " uuid '%s'" % book_uuid)
                book = self._converter.convert_book(logbook)
                if not lazy:
                    self._converter.populate_book(self.session, book)
                return book
        except sa_exc.DBAPIError:
            exc.raise_with_cause(exc.StorageFailure,
                                 "Failed getting logbook '%s'" % book_uuid)

    def get_logbooks(self, lazy=False):
        gathered = []
        try:
            query = dbapi.model_query(self.session, LogBook)
            with self.session.begin():
                for logbook in query:
                    book = self._converter.convert_book(logbook)
                    if not lazy:
                        self._converter.populate_book(self.session, book)
                    gathered.append(book)
        except sa_exc.DBAPIError:
            exc.raise_with_cause(exc.StorageFailure,
                                 "Failed getting logbooks")
        for book in gathered:
            yield book

    def get_flows_for_book(self, book_uuid, lazy=False):
        gathered = []
        try:
            with self.session.begin():
                for fd in self._converter.flow_query_iter(self.session, book_uuid):
                    if not lazy:
                        self._converter.populate_flow_detail(self.session, fd)
                    gathered.append(fd)
        except sa_exc.DBAPIError:
            exc.raise_with_cause(exc.StorageFailure,
                                 "Failed getting flow details in"
                                 " logbook '%s'" % book_uuid)
        for flow_details in gathered:
            yield flow_details

    def get_flow_details(self, fd_uuid, lazy=False):
        try:
            query = dbapi.model_query(self.session, FlowDetail).filter_by(uuid=fd_uuid)
            with self.session.begin():
                flowdetail = query.one_or_none()
                if not flowdetail:
                    raise exc.NotFound("No flow details found with uuid"
                                       " '%s'" % fd_uuid)
                fd = self._converter.convert_flow_detail(flowdetail)
                if not lazy:
                    self._converter.populate_flow_detail(self.session, fd)
                return fd
        except sa_exc.SQLAlchemyError:
            exc.raise_with_cause(exc.StorageFailure,
                                 "Failed getting flow details with"
                                 " uuid '%s'" % fd_uuid)

    def get_atom_details(self, ad_uuid):
        try:
            query = dbapi.model_query(self.session, AtomDetail).filter_by(uuid=ad_uuid)
            with self.session.begin():
                atomdetail = query.one_or_none()
                if not atomdetail:
                    raise exc.NotFound("No atom details found with uuid"
                                       " '%s'" % ad_uuid)
                return self._converter.convert_atom_detail(atomdetail)
        except sa_exc.SQLAlchemyError:
            exc.raise_with_cause(exc.StorageFailure,
                                 "Failed getting atom details with"
                                 " uuid '%s'" % ad_uuid)

    def get_atoms_for_flow(self, fd_uuid):
        gathered = []
        try:
            with self.session.begin():
                for ad in self._converter.atom_query_iter(self.session, fd_uuid):
                    gathered.append(ad)
        except sa_exc.DBAPIError:
            exc.raise_with_cause(exc.StorageFailure,
                                 "Failed getting atom details in flow"
                                 " detail '%s'" % fd_uuid)
        for atom_details in gathered:
            yield atom_details
