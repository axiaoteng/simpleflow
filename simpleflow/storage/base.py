# -*- coding: utf-8 -*-

#    Copyright (C) 2013 Rackspace Hosting Inc. All Rights Reserved.
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

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class Connection(object):
    """Base class for backend connections."""

    @abc.abstractmethod
    def update_atom_details(self, atom_detail):
        """Updates a given atom details and returns the updated version.

        NOTE(harlowja): the details that is to be updated must already have
        been created by saving a flow details with the given atom detail inside
        of it.
        """

    @abc.abstractmethod
    def update_flow_details(self, flow_detail):
        """Updates a given flow details and returns the updated version.

        NOTE(harlowja): the details that is to be updated must already have
        been created by saving a logbook with the given flow detail inside
        of it.
        """

    @abc.abstractmethod
    def save_logbook(self, book):
        """Saves a logbook, and all its contained information."""

    @abc.abstractmethod
    def destroy_logbook(self, book_uuid):
        """Deletes/destroys a logbook matching the given uuid."""

    @abc.abstractmethod
    def get_logbook(self, book_uuid, lazy=False):
        """Fetches a logbook object matching the given uuid."""

    @abc.abstractmethod
    def get_logbooks(self, lazy=False):
        """Return an iterable of logbook objects."""

    @abc.abstractmethod
    def get_flows_for_book(self, book_uuid):
        """Return an iterable of flowdetails for a given logbook uuid."""

    @abc.abstractmethod
    def get_flow_details(self, fd_uuid, lazy=False):
        """Fetches a flowdetails object matching the given uuid."""

    @abc.abstractmethod
    def get_atom_details(self, ad_uuid):
        """Fetches a atomdetails object matching the given uuid."""

    @abc.abstractmethod
    def get_atoms_for_flow(self, fd_uuid):
        """Return an iterable of atomdetails for a given flowdetails uuid."""
