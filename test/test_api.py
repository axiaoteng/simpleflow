# -*- coding: utf-8 -*-
import os

from simpleflow.patterns import linear_flow as lf
from simpleflow import task
from simpleflow import api
from simpleflow import states
from simpleflow.storage import Connection
from simpleflow.types.dbconver import SimpleFlowConverter
from simpleservice.ormdb.engines import create_engine
from simpleservice.ormdb.orm import get_maker
from simpleservice.ormdb.argformater import connformater


FINISHED_STATES = (states.SUCCESS, states.FAILURE, states.REVERTED)

dst = {'host': '172.20.0.3',
       'port': 3304,
       'schema': 'simpleflow',
       'user': 'root',
       'passwd': '111111'}

sql_connection = connformater % dst
engine = create_engine(sql_connection, converter_class=SimpleFlowConverter)
session_maker = get_maker(engine=engine)
session = session_maker()


class UnfortunateTask(task.Task):
    def execute(self):
        print('executing %s' % self)
        boom = os.environ.get('BOOM')
        if boom:
            print('> Critical error: boom = %s' % boom)
            raise SystemExit()
        else:
            print('> this time not exiting')


class TestTask(task.Task):
    def execute(self):
        print('executing %s' % self)


def test_flow_factory():
    return lf.Flow('example').add(
        TestTask(name='first'),
        UnfortunateTask(name='boom'),
        TestTask(name='second'))

print 'load_from_factory test'

engine = api.load_from_factory(session=session,
                               flow_factory=test_flow_factory)
print('Running flow %s %s' % (engine.storage.flow_name,
                              engine.storage.flow_uuid))
engine.run()


print 'finish load_from_factory test~'


print 'finish load_from_detail test~'

def resume(flowdetail, session):
    print('Resuming flow %s %s' % (flowdetail.name, flowdetail.uuid))
    engine = api.load_from_detail(session, flow_detail=flowdetail)
    engine.run()


logbooks = list(Connection(session).get_logbooks())


for lb in logbooks:
    for fd in lb:
        print fd.state
        print fd
        if fd.state not in FINISHED_STATES:
            resume(fd, session)
