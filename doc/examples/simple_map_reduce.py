# -*- coding: utf-8 -*-

#    Copyright (C) 2014 Yahoo! Inc. All Rights Reserved.
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
import sys
import six

from simpleflow.engines.engine import ParallelActionEngine
from simpleflow import api
from simpleflow.patterns import linear_flow as lf
from simpleflow.patterns import graph_flow as gf
from simpleflow.patterns import unordered_flow as uf
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


class SumMapper(task.Task):
    def execute(self, inputs):
        # Sums some set of provided inputs.
        return sum(inputs)


class TotalReducer(task.Task):
    def execute(self, *args, **kwargs):
        # Reduces all mapped summed outputs into a single value.
        total = 0
        for (k, v) in six.iteritems(kwargs):
            # If any other kwargs was passed in, we don't want to use those
            # in the calculation of the total...
            if k.startswith('reduction_'):
                total += v
        return total


def chunk_iter(chunk_size, upperbound):
    """Yields back chunk size pieces from zero to upperbound - 1."""
    chunk = []
    for i in range(0, upperbound):
        chunk.append(i)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []


# Upper bound of numbers to sum for example purposes...
UPPER_BOUND = 10000

# How many mappers we want to have.
SPLIT = 10

# How big of a chunk we want to give each mapper.
CHUNK_SIZE = UPPER_BOUND // SPLIT

# This will be the workflow we will compose and run.
gflow = gf.Flow("root")
# The mappers will run in parallel.
store = {}
provided = []
uflow = uf.Flow('map')
for i, chunk in enumerate(chunk_iter(CHUNK_SIZE, UPPER_BOUND)):
    mapper_name = 'mapper_%s' % i
    # Give that mapper some information to compute.
    store[mapper_name] = chunk
    # The reducer uses all of the outputs of the mappers, so it needs
    # to be recorded that it needs access to them (under a specific name).
    provided.append("reduction_%s" % i)
    uflow.add(SumMapper(name=mapper_name,
                        rebind=[mapper_name],
                        provides=provided[-1]))

gflow.add(uflow)
# The reducer will run last (after all the mappers).
gflow.add(TotalReducer('reducer', provides='reducer', rebind=provided))

# print store

# Now go!
e = api.load(connection, gflow, store=store, engine_cls=ParallelActionEngine, max_workers=4)
print("Running a parallel engine with options: %s" % e.options)
e.run()

# Now get the result the reducer created.
# get_execute_result取代了get方法
total = e.storage.get_execute_result('reducer')
print("Calculated result = %s" % total)

# Calculate it manually to verify that it worked...
calc_total = sum(range(0, UPPER_BOUND))
if calc_total != total:
    sys.exit(1)
