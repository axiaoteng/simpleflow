# -*- coding: utf-8 -*-
# 这是linear flow的错误测试
# output is
# -----------------------------------

from simpleflow import api
from simpleflow.patterns import linear_flow as lf
from simpleflow.engines.engine import ParallelActionEngine
from simpleflow import task
from simpleflow.utils.storage_utils import build_session
from simpleflow.storage import Connection
from simpleflow.types import failure
import eventlet
eventlet.monkey_patch()

failure.TRACEBACK = True

dst = {'host': '172.20.0.3',
       'port': 3304,
       'schema': 'simpleflow',
       'user': 'root',
       'passwd': '111111'}

session = build_session(dst)

connection = Connection(session)


class MysqlDumper(task.Task):

    def execute(self, server_id):
        print 'server_id', server_id

        return server_id + 1

    def revert(self, *args, **kwargs):
        print 'revert', args, kwargs


atask = MysqlDumper('s1', provides='s2', rebind=['s1'])
btask = MysqlDumper('s2', rebind=['s2'])


lflow = lf.Flow('lftest')
lflow.add(atask)
lflow.add(btask)

data = {'s1': 1}


result = api.run(session, lflow, store=data, engine_cls=ParallelActionEngine)
# result = api.run(session, lflow, store=data)
print 'all success',
print result

