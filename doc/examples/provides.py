# -*- coding: utf-8 -*-
import time
import random
from simpleflow.task import Task
from simpleflow import api
from simpleflow.patterns import graph_flow as gf
from simpleflow.patterns import linear_flow as lf
from simpleflow.engines.engine import ParallelActionEngine
from simpleflow.utils.storage_utils import build_session
import eventlet
eventlet.monkey_patch()


dst = {'host': '172.20.0.3',
       'port': 3304,
       'schema': 'simpleflow',
       'user': 'root',
       'passwd': '111111'}


session = build_session(dst)


def choise_fail(src_list):
    # 随机选取列表中部分元素作为执行失败的目标
    choise_number = random.randint(2, 10)
    fail = random.sample(src_list, min(choise_number, len(src_list)))
    return list(set(src_list) - set(fail)), fail


class BroadCastStop(Task):

    def execute(self, server_list):
        print 'du broad cast'
        eventlet.sleep(1)
        # 群发停止命令
        return choise_fail(server_list)


class RetryStop(Task):

    def execute(self, success, fail):
        # 对部分停服失败服务器进行重试
        # 可以在这里对停服失败的进行kill操作
       return success, fail


class DumpDb(Task):

    def execute(self, server_list):
        # 备份对应数据库
        print 'do dump'
        eventlet.sleep(3)
        return choise_fail(server_list)


class UpdateDb(Task):

    def execute(self, server_list):
        # 升级对应数据库
        print 'do update db'
        eventlet.sleep(3)
        return choise_fail(server_list)


class UpdateApp(Task):

    def execute(self, server_list):
        # 更新文件, 与DumpDb是并行执行的
        print 'do update app'
        return choise_fail(server_list)


class StartServer(Task):

    def execute(self, updateapp_success,  updatedb_success):
        print 'do start'
        # 启动服务器, 需要UpdateApp和UpdateDb完成
        dst = set(updateapp_success) & set(updatedb_success)
        return choise_fail(dst)


class ReultNotify(Task):

    def execute(self, stop_fail, dump_fail, updatedb_fail, updateapp_fail, start_fail):
        # 处理失败对象,一般为对外通知
        print 'stop fail' % str(stop_fail)
        print 'dump fail' % str(dump_fail)
        print 'update db  fail' % str(updatedb_fail)
        print 'update app fail' % str(updateapp_fail)
        print 'start fail' % str(start_fail)

flow = gf.Flow('stop_update_start').add(
    BroadCastStop(provides=('broadcast_success', 'broadcast_fail'), rebind=['stop_services']),
    RetryStop(provides=('stop_success', 'stop_fail'), rebind=['broadcast_success', 'broadcast_fail']),
    DumpDb(provides=('dump_success', 'dump_fail'), rebind=['stop_success']),
    UpdateDb(provides=('updatedb_success', 'updatedb_fail'), rebind=['dump_success']),
    UpdateApp(provides=('updateapp_success', 'updateapp_fail'), rebind=['stop_success']),
    StartServer(provides=('start_success', 'start_fail')),
    # ReultNotify()
)

store = {'stop_services': [i for i in range(50)]}
result = api.run(session, flow, store=store, engine_cls=ParallelActionEngine)
result.pop('stop_services')
result.pop('broadcast_success')
result.pop('broadcast_fail')
for key in result:
    print key, result[key]

eventlet.sleep(1)