from simpleutil.utils import uuidutils

from simpleservice.ormdb.engines import create_engine
from simpleservice.ormdb.orm import get_maker
from simpleservice.ormdb.argformater import connformater
from simpleservice.ormdb.api import MysqlDriver
from simpleservice.ormdb.tools.utils import init_database

from simpleflow.types.dbconver import SimpleFlowConverter
from simpleflow.storage import models
from simpleflow.storage import middleware


def build_session(db_info=None):
    if db_info is None:
        engine=create_engine(sql_connection='sqlite:///:memory:',logging_name='taskflow')
        models.SimpleFlowTables.metadata.create_all(engine)
        session_maker = get_maker(engine)
        session = session_maker()
    else:
        sql_connection = connformater % db_info
        engine = create_engine(sql_connection, converter_class=SimpleFlowConverter)
        session_maker = get_maker(engine=engine)
        session = session_maker()
    return session


def build_driver(name, conf):
    return MysqlDriver(name, conf, converter_class=SimpleFlowConverter)


def init_simpleflowdb(db_info):
    init_database(db_info, models.SimpleFlowTables.metadata)


def temporary_log_book(connection=None):
    """Creates a temporary logbook for temporary usage in the given backend.

    Mainly useful for tests and other use cases where a temporary logbook
    is needed for a short-period of time.
    """
    book = middleware.LogBook('tmp')
    if connection is not None:
        # with contextlib.closing(backend.get_connection()) as conn:
        connection.save_logbook(book)
    return book


def temporary_flow_detail(connection=None, meta=None):
    """Creates a temporary flow detail and logbook in the given backend.

    Mainly useful for tests and other use cases where a temporary flow detail
    and a temporary logbook is needed for a short-period of time.
    """
    flow_id = uuidutils.generate_uuid()
    book = temporary_log_book(connection)

    flow_detail = middleware.FlowDetail(name='tmp-flow-detail', uuid=flow_id)
    if meta is not None:
        if flow_detail.meta is None:
            flow_detail.meta = {}
        flow_detail.meta.update(meta)
    book.add(flow_detail)

    if connection is not None:
        connection.save_logbook(book)
    # Return the one from the saved logbook instead of the local one so
    # that the freshest version is given back.
    return book, book.find(flow_id)


def create_flow_detail(flow, book=None, connection=None, meta=None):
    """Creates a flow detail for a flow & adds & saves it in a logbook.

    This will create a flow detail for the given flow using the flow name,
    and add it to the provided logbook and then uses the given backend to save
    the logbook and then returns the created flow detail.

    If no book is provided a temporary one will be created automatically (no
    reference to the logbook will be returned, so this should nearly *always*
    be provided or only used in situations where no logbook is needed, for
    example in tests). If no backend is provided then no saving will occur and
    the created flow detail will not be persisted even if the flow detail was
    added to a given (or temporarily generated) logbook.
    """
    flow_id = uuidutils.generate_uuid()
    flow_name = getattr(flow, 'name', None)
    if flow_name is None:
        flow_name = flow_id

    flow_detail = middleware.FlowDetail(name=flow_name, uuid=flow_id)
    if meta is not None:
        if flow_detail.meta is None:
            flow_detail.meta = {}
        flow_detail.meta.update(meta)

    if connection is not None and book is None:
        book = temporary_log_book(connection)

    if book is not None:
        book.add(flow_detail)
        if connection is not None:
            connection.save_logbook(book)
        return book.find(flow_id)
    else:
        return flow_detail
