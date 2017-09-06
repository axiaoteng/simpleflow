# -*- coding: utf-8 -*-
# 这是一个无向图有错误的并发测试
# output is
# -----------------------------------
# success 10
# success 4
# success 6
# success 2
# success 8
# revert () {'server_id': 9, 'result': <simpleflow.types.failure.Failure object at 0x000000000F50C240>, 'flow_failures': {'dumper9': <simpleflow.types.failure.Failure object at 0x000000000F50C240>}}
# revert () {'server_id': 10, 'result': None, 'flow_failures': {'dumper9': <simpleflow.types.failure.Failure object at 0x000000000F50C240>}}
# revert () {'server_id': 3, 'result': <simpleflow.types.failure.Failure object at 0x000000000F44F390>, 'flow_failures': {'dumper9': <simpleflow.types.failure.Failure object at 0x000000000F50C240>}}
# revert () {'server_id': 1, 'result': <simpleflow.types.failure.Failure object at 0x000000000F44C438>, 'flow_failures': {'dumper9': <simpleflow.types.failure.Failure object at 0x000000000F50C240>}}
# revert () {'server_id': 4, 'result': None, 'flow_failures': {'dumper9': <simpleflow.types.failure.Failure object at 0x000000000F50C240>}}
# revert () {'server_id': 6, 'result': None, 'flow_failures': {'dumper9': <simpleflow.types.failure.Failure object at 0x000000000F50C240>}}
# revert () {'server_id': 7, 'result': <simpleflow.types.failure.Failure object at 0x000000000F51BC88>, 'flow_failures': {'dumper9': <simpleflow.types.failure.Failure object at 0x000000000F50C240>}}
# revert () {'server_id': 5, 'result': <simpleflow.types.failure.Failure object at 0x000000000F44CC18>, 'flow_failures': {'dumper9': <simpleflow.types.failure.Failure object at 0x000000000F50C240>}}
# revert () {'server_id': 2, 'result': None, 'flow_failures': {'dumper9': <simpleflow.types.failure.Failure object at 0x000000000F50C240>}}
# revert () {'server_id': 8, 'result': None, 'flow_failures': {'dumper9': <simpleflow.types.failure.Failure object at 0x000000000F50C240>}}
# Traceback (most recent call last):
#     .......
#     raise exc.WrappedFailure(failures)
# simpleflow.exceptions.WrappedFailure: WrappedFailure: [Failure: Exception: server id 9 error, Failure: Exception: server id 7 error, Failure: Exception: server id 5 error, Failure: Exception: server id 3 error, Failure: Exception: server id 1 error]
# -----------------------------------
import time
from simpleflow import api
from simpleflow.patterns import unordered_flow as uf
from simpleflow.engines.engine import ParallelActionEngine
from simpleflow import retry
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
        if server_id % 2 != 0:
            raise Exception('server id %d error' % server_id)
        print 'success', server_id

    def revert(self, *args, **kwargs):
        print 'revert', args, kwargs


servers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def add_task(flow, server_list):
    store = {}
    for sid in server_list:
        rebind = str(sid)
        dumper = MysqlDumper(name='dumper%d' % sid, provides='result_%i' % sid, rebind=[rebind])
        flow.add(dumper)
        store[rebind] = sid
    return store

s = time.time()
uflow = uf.Flow('retrying-uf')
data = add_task(uflow, servers)
print time.time() - s

try:
    result = api.run(session, uflow, store=data, engine_cls=ParallelActionEngine)
    print 'all success',
    print result
finally:
    print time.time() - s
