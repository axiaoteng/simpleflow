# -*- coding: utf-8 -*-

# output is
# -----------------------------------
# Calling jim 555.
# Calling joe 444.
# Calling 444 and apologizing.
# Calling 555 and apologizing.
# Flow failed: Suzzie not home right now.
# -----------------------------------

from simpleflow import api
from simpleflow.patterns import linear_flow as lf
from simpleflow import task
from simpleflow.utils.storage_utils import build_session
from simpleflow.storage import Connection
import eventlet
eventlet.monkey_patch()


dst = {'host': '172.20.0.3',
       'port': 3304,
       'schema': 'simpleflow',
       'user': 'root',
       'passwd': '111111'}


session = build_session(dst)

connection = Connection(session)



class CallJim(task.Task):
    def execute(self, jim_number, *args, **kwargs):
        print("Calling jim %s." % jim_number)

    def revert(self, jim_number, *args, **kwargs):
        print("Calling %s and apologizing." % jim_number)


class CallJoe(task.Task):
    def execute(self, joe_number, *args, **kwargs):
        print("Calling joe %s." % joe_number)

    def revert(self, joe_number, *args, **kwargs):
        print("Calling %s and apologizing." % joe_number)


class CallSuzzie(task.Task):
    def execute(self, suzzie_number, *args, **kwargs):
        raise Exception("Suzzie not home right now.")


# Create your flow and associated tasks (the work to be done).
flow = lf.Flow('simple-linear').add(
    CallJim(),
    CallJoe(),
    CallSuzzie()
)

stone = dict(joe_number=444,
             jim_number=555,
             suzzie_number=666)


try:
    # Now run that flow using the provided initial data (store below).
    api.run(session, flow, store=stone)
except Exception as e:
    # NOTE(harlowja): This exception will be the exception that came out of the
    # 'CallSuzzie' task instead of a different exception, this is useful since
    # typically surrounding code wants to handle the original exception and not
    # a wrapped or altered one.
    #
    # *WARNING* If this flow was multi-threaded and multiple active tasks threw
    # exceptions then the above exception would be wrapped into a combined
    # exception (the object has methods to iterate over the contained
    # exceptions). See: exceptions.py and the class 'WrappedFailure' to look at
    # how to deal with multiple tasks failing while running.
    #
    # You will also note that this is not a problem in this case since no
    # parallelism is involved; this is ensured by the usage of a linear flow
    # and the default engine type which is 'serial' vs being 'parallel'.
    print("Flow failed: %s" % e)
