# -*- coding: utf-8 -*-

#    Copyright (C) 2013 Yahoo! Inc. All Rights Reserved.
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
import six

from simpleutil.utils import importutils
from simpleutil.utils import reflection


from simpleflow import exceptions as exc
from simpleflow.engines.engine import SerialActionEngine
from simpleflow.utils import storage_utils as p_utils
from simpleflow.storage.impl import Connection


def _fetch_factory(factory_name):
    try:
        return importutils.import_class(factory_name)
    except (ImportError, ValueError) as e:
        raise ImportError("Could not import factory %r: %s"
                          % (factory_name, e))


def _fetch_validate_factory(flow_factory):
    if isinstance(flow_factory, six.string_types):
        factory_fun = _fetch_factory(flow_factory)
        factory_name = flow_factory
    else:
        factory_fun = flow_factory
        factory_name = reflection.get_callable_name(flow_factory)
        try:
            reimported = _fetch_factory(factory_name)
            assert reimported == factory_fun
        except (ImportError, AssertionError):
            raise ValueError('Flow factory %r is not reimportable by name %s'
                             % (factory_fun, factory_name))
    return factory_name, factory_fun


def flow_from_detail(flow_detail):
    """Reloads a flow previously saved.

    Gets the flow factories name and any arguments and keyword arguments from
    the flow details metadata, and then calls that factory to recreate the
    flow.

    :param flow_detail: FlowDetail that holds state of the flow to load
    """
    try:
        factory_data = flow_detail.meta['factory']
    except (KeyError, AttributeError, TypeError):
        raise ValueError('Cannot reconstruct flow %s %s: '
                         'no factory information saved.'
                         % (flow_detail.name, flow_detail.uuid))

    try:
        factory_fun = _fetch_factory(factory_data['name'])
    except (KeyError, ImportError):
        raise ImportError('Could not import factory for flow %s %s'
                          % (flow_detail.name, flow_detail.uuid))

    args = factory_data.get('args', ())
    kwargs = factory_data.get('kwargs', {})
    return factory_fun(*args, **kwargs)


def save_factory_details(flow_detail,
                         flow_factory, factory_args, factory_kwargs,
                         connection=None):
    """Saves the given factories reimportable attributes into the flow detail.

    This function saves the factory name, arguments, and keyword arguments
    into the given flow details object  and if a backend is provided it will
    also ensure that the backend saves the flow details after being updated.

    :param flow_detail: FlowDetail that holds state of the flow to load
    :param flow_factory: function or string: function that creates the flow
    :param factory_args: list or tuple of factory positional arguments
    :param factory_kwargs: dict of factory keyword arguments
    :param connection: storage connection
    """
    if not factory_args:
        factory_args = []
    if not factory_kwargs:
        factory_kwargs = {}
    factory_name, _factory_fun = _fetch_validate_factory(flow_factory)
    factory_data = {
        'factory': {
            'name': factory_name,
            'args': factory_args,
            'kwargs': factory_kwargs,
        },
    }
    if not flow_detail.meta:
        flow_detail.meta = factory_data
    else:
        flow_detail.meta.update(factory_data)
    if connection is not None:
        connection.update_flow_details(flow_detail)


def load(connection,
         flow, flow_detail=None, book=None, store=None,
         engine_cls=SerialActionEngine, **options):

    if flow_detail is None:
        flow_detail = p_utils.create_flow_detail(flow, book=book,
                                                 connection=connection)
    try:
        engine = engine_cls(flow, flow_detail, connection, options)
    except Exception:
        raise exc.NotFound("Could not find engine '%s'" % str(engine_cls))
    else:
        if store:
            engine.storage.inject(store)
        return engine


def run(session, flow, flow_detail=None,
        book=None, store=None,
        engine_cls=SerialActionEngine, **options):
    """Run the flow.

    This function loads the flow into an engine (with the :func:`load() <load>`
    function) and runs the engine.

    The arguments are interpreted as for :func:`load() <load>`.

    :returns: dictionary of all named
              results (see :py:meth:`~.taskflow.storage.Storage.fetch_all`)
    """
    connection = Connection(session)
    engine = load(connection,
                  flow=flow, flow_detail=flow_detail, book=book, store=store,
                  engine_cls=engine_cls, **options)
    engine.run()
    return engine.storage.fetch_all()


def load_from_factory(session,
                      flow_factory, factory_args=None, factory_kwargs=None,
                      book=None, store=None,
                      engine_cls=SerialActionEngine,
                      **options):
    _factory_name, factory_fun = _fetch_validate_factory(flow_factory)
    if not factory_args:
        factory_args = []
    if not factory_kwargs:
        factory_kwargs = {}
    flow = factory_fun(*factory_args, **factory_kwargs)
    connection = Connection(session)
    flow_detail = p_utils.create_flow_detail(flow, book=book, connection=connection)
    save_factory_details(flow_detail,
                         flow_factory, factory_args, factory_kwargs,
                         connection=connection)
    return load(connection,
                flow=flow, flow_detail=flow_detail, book=book, store=store,
                engine_cls=engine_cls, **options)


def load_from_detail(session, flow_detail,
                     engine_cls=SerialActionEngine, store=None,
                     **options):
    connection = Connection(session)
    flow = flow_from_detail(flow_detail)
    return load(connection,
                flow, flow_detail=flow_detail, store=store,
                engine_cls=engine_cls, **options)
