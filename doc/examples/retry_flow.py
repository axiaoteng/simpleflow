# -*- coding: utf-8 -*-
# output is
# -----------------------------------
# Calling joe 111.
# Calling jim 333.
# Wrong number jim, apologizing.
# Calling joe 111 and apologizing.
# Calling joe 111.
# Calling jim 444.
# Wrong number jim, apologizing.
# Calling joe 111 and apologizing.
# Calling joe 111.
# Calling jim 555.
# Wrong number jim, apologizing.
# Calling joe 111 and apologizing.
# Calling joe 111.
# Calling jim 666.
# Wrong number jim, apologizing.
# Calling joe 111 and apologizing.
# Traceback (most recent call last):
# -----------------------------------

from simpleflow import api
from simpleflow.patterns import linear_flow as lf
from simpleflow import retry
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


class CallJoe(task.Task):
    def execute(self, joe_number, *args, **kwargs):
        print("Calling joe %s." % joe_number)

    def revert(self, joe_number, *args, **kwargs):
        print("Calling joe %s and apologizing." % joe_number)


class CallJim(task.Task):
    def execute(self, jim_number):
        print("Calling jim %s." % jim_number)
        if jim_number != 5551:
            raise Exception("Wrong number! of jim")
        else:
            print("Hello Jim!")

    def revert(self, jim_number, **kwargs):
        print("Wrong number jim, apologizing.")


retryer = retry.ParameterizedForEach(rebind=['phone_directory'], provides='jim_number')
lflow = lf.Flow('retrying-linear', retry=retryer)
lflow.add(CallJoe())
lflow.add(CallJim())
# Create your flow and associated tasks (the work to be done).
# Now run that flow using the provided initial data (store below).
result = api.run(session, lflow, store={'phone_directory': [333, 444, 555, 666], 'joe_number': 111})
print result
