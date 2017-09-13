# -*- coding: utf-8 -*-
# -----------------------------------
# 1 a exec
# 1 b exec
# RetryFlow exec () {} history: 0
# Exception d
# 1 c exec
# RetryFlow on_failure
# d revert () {'result': <simpleflow.types.failure.Failure object at 0x000000000F38B6A0>, 'value': 1, 'flow_failures': {'d': <simpleflow.types.failure.Failure object at 0x000000000F38B6A0>}}
# c revert () {'result': 'c', 'value': 1, 'flow_failures': {'d': <simpleflow.types.failure.Failure object at 0x000000000F38B6A0>}}
# RetryFlow exec () {} history: 1
# Exception d
# 1 c exec
# RetryFlow on_failure
# d revert () {'result': <simpleflow.types.failure.Failure object at 0x000000000F390278>, 'value': 1, 'flow_failures': {'d': <simpleflow.types.failure.Failure object at 0x000000000F390278>}}
# c revert () {'result': 'c', 'value': 1, 'flow_failures': {'d': <simpleflow.types.failure.Failure object at 0x000000000F390278>}}
# RetryFlow exec () {} history: 2
# Exception d
# 1 c exec
# RetryFlow on_failure
# d revert () {'result': <simpleflow.types.failure.Failure object at 0x000000000F447710>, 'value': 1, 'flow_failures': {'d': <simpleflow.types.failure.Failure object at 0x000000000F447710>}}
# c revert () {'result': 'c', 'value': 1, 'flow_failures': {'d': <simpleflow.types.failure.Failure object at 0x000000000F447710>}}
# -------REVERT_ALL会将回滚传达至上层,所以会多出下面2行---------
# b revert () {'result': 'b', 'value': 1, 'flow_failures': {'d': <simpleflow.types.failure.Failure object at 0x000000000F447710>}}
# a revert () {'result': 'a', 'value': 1, 'flow_failures': {'d': <simpleflow.types.failure.Failure object at 0x000000000F447710>}}


import random
from simpleflow import api
from simpleflow.patterns import linear_flow as lf
from simpleflow.patterns import graph_flow as gf
from simpleflow.engines.engine import ParallelActionEngine
from simpleflow import retry
from simpleflow import task
from simpleflow.utils.storage_utils import build_session
from simpleflow.storage import Connection
import eventlet
# eventlet.monkey_patch()

revert_all = False

dst = {'host': '172.20.0.3',
       'port': 3304,
       'schema': 'simpleflow',
       'user': 'root',
       'passwd': '111111'}
from simpleservice.ormdb.argformater import connformater
sql_connection = connformater % dst
session = build_session(sql_connection)

connection = Connection(session)


def choise_fail(src_list):
    # 随机选取列表中部分元素作为执行失败的目标
    choise_number = random.randint(2, 10)
    fail = random.sample(src_list, min(choise_number, len(src_list)))
    return list(set(src_list) - set(fail)), fail


class A(task.Task):

    def execute(self, value):
        if self.name in ('d', 'e'):
            print 'Exception', self.name
            raise Exception('i am %s' % self.name)
        print value,
        print '%s exec' % self.name
        return self.name

    def revert(self, *args, **kwargs):
        # result是execute的执行结果,是必定有的参数
        # 可以通过判断result是不是Failure类来确认execute是否出错
        # 可有选择性的让成功的节点不回滚
        print '%s revert' % self.name,
        print args, kwargs
        # 可以在这里抛出异常看看
        # raise Exception('revert error')


class RetryFlow(retry.Retry):

    def on_failure(self, history, *args, **kwargs):
        print 'RetryFlow on_failure'
        if len(history) > 2:
            global revert_all
            if revert_all:
                return retry.REVERT_ALL
            return retry.REVERT
        return retry.RETRY

    def execute(self, history, *args, **kwargs):
        print 'RetryFlow exec', args, kwargs, 'history:', len(history)
        return 2

    def revert(self, history, *args, **kwargs):
        return 'RetryFlow revert', args, kwargs, 'history:', len(history)


retryer = RetryFlow()
lflow = lf.Flow('xxx')
lflow.add(A('a', rebind=['va']))
lflow.add(A('b', rebind=['vb']))

# retry应该是写在这里,如果在顶层flow
# 那么RETRY和REVERT_ALL是没有区别的
gflow = gf.Flow('ogm', retry=retryer)
gflow.add(A('c', rebind=['vc']))    # 因为使用的是graph_flow, c和d是没有顺序的
gflow.add(A('d', rebind=['vd']))
lflow.add(gflow)

# 设置是否回滚全部
revert_all = True

api.run(session, lflow, engine_cls=ParallelActionEngine, store={'va': 1, 'vb': 1, 'vc': 1, 'vd': 1})
print 'all success'
