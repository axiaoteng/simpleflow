# -*- coding: utf-8 -*-
# 这是linear flow的错误测试
# output is
# -----------------------------------

from simpleflow import api
from simpleflow.patterns import linear_flow as lf
from simpleflow.patterns import graph_flow as gf
from simpleflow.engines.engine import ParallelActionEngine
from simpleflow import task
from simpleflow.utils.storage_utils import build_session
from simpleflow.storage import Connection
from simpleflow.types import failure

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
        print 'execute server_id', server_id
        return server_id + 1

    def revert(self, *args, **kwargs):
        print 'revert', args, kwargs


atask = MysqlDumper('s1', provides='s2', rebind=['s1'])
btask = MysqlDumper('s2', provides='s3', rebind=['s2'])
ctask = MysqlDumper('s3', provides='s4', rebind=['s3'])
dtask = MysqlDumper('s4', provides='s5', rebind=['s4'])
etask = MysqlDumper('s5', provides='s6', rebind=['s5'])


lflow = lf.Flow('lftest')
lflow.add(atask)
lflow.add(btask)
lflow.add(ctask)
lflow.add(dtask)
lflow.add(etask)

data = {'s1': 1}

result = api.run(session, lflow, store=data, engine_cls=ParallelActionEngine)
# result = api.run(session, lflow, store=data)
print 'all success',
print result
