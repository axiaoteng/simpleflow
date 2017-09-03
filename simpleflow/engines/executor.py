# -*- coding: utf-8 -*-

#    Copyright (C) 2013 Yahoo! Inc. All Rights Reserved.
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

from simpleutil.utils import futurist

from simpleflow import task as ta
from simpleflow.types import failure
from simpleflow.types import notifier

# Execution and reversion outcomes.
EXECUTED = 'executed'
REVERTED = 'reverted'


def _execute_retry(retry, arguments):
    try:
        result = retry.execute(**arguments)
    except Exception:
        result = failure.Failure()
    return (EXECUTED, result)


def _revert_retry(retry, arguments):
    try:
        result = retry.revert(**arguments)
    except Exception:
        result = failure.Failure()
    return (REVERTED, result)


def _execute_task(task, arguments, progress_callback=None):
    with notifier.register_deregister(task.notifier,
                                      ta.EVENT_UPDATE_PROGRESS,
                                      callback=progress_callback):
        try:
            task.pre_execute()
            result = task.execute(**arguments)
        except Exception:
            # NOTE(imelnikov): wrap current exception with Failure
            # object and return it.
            result = failure.Failure()
        finally:
            task.post_execute()
    return (EXECUTED, result)


def _revert_task(task, arguments, result, failures, progress_callback=None):
    arguments = arguments.copy()
    arguments[ta.REVERT_RESULT] = result
    arguments[ta.REVERT_FLOW_FAILURES] = failures
    with notifier.register_deregister(task.notifier,
                                      ta.EVENT_UPDATE_PROGRESS,
                                      callback=progress_callback):
        try:
            task.pre_revert()
            result = task.revert(**arguments)
        except Exception:
            # NOTE(imelnikov): wrap current exception with Failure
            # object and return it.
            result = failure.Failure()
        finally:
            task.post_revert()
    return (REVERTED, result)


class Executor(object):

    def __init__(self, executor=None):
        self._executor = executor
        self._own_executor = executor is None

    def _max_workers(self):
        """return max workers of TaskExecutor"""
        return None

    @property
    def max_workers(self):
        return self._max_workers()

    def _create_executor(self, *args, **kwargs):
        """Called when an executor has not been provided to make one."""
        return futurist.SynchronousExecutor()

    def start(self):
        if self._own_executor:
            self._executor = self._create_executor(
                max_workers=self.max_workers)

    def stop(self):
        if self._own_executor:
            self._executor.shutdown(wait=True)
            self._executor = None


class SerialRetryExecutor(Executor):
    """Executes and reverts retries."""


    def execute_retry(self, retry, arguments):
        """Schedules retry execution."""
        fut = self._executor.submit(_execute_retry, retry, arguments)
        fut.atom = retry
        return fut

    def revert_retry(self, retry, arguments):
        """Schedules retry reversion."""
        fut = self._executor.submit(_revert_retry, retry, arguments)
        fut.atom = retry
        return fut


class TaskExecutor(Executor):
    """Executes and reverts tasks.

    This class takes task and its arguments and executes or reverts it.
    It encapsulates knowledge on how task should be executed or reverted:
    right now, on separate thread, on another machine, etc.
    """

    def _submit_task(self, func, task, *args, **kwargs):
        fut = self._executor.submit(func, task, *args, **kwargs)
        fut.atom = task
        return fut

    def execute_task(self, task, task_uuid, arguments, progress_callback=None):
        return self._submit_task(_execute_task, task, arguments,
                                 progress_callback=progress_callback)

    def revert_task(self, task, task_uuid, arguments, result, failures,
                    progress_callback=None):
        return self._submit_task(_revert_task, task, arguments, result,
                                 failures, progress_callback=progress_callback)


class SerialTaskExecutor(TaskExecutor):
    """Executes tasks one after another."""


class ParallelGreenThreadTaskExecutor(TaskExecutor):
    """Executes tasks in parallel using a greenthread pool executor."""

    MAX_WORKERS = 1000

    def __init__(self, workers=None):
        super(ParallelGreenThreadTaskExecutor, self).__init__()
        self.workers = workers

    def _create_executor(self, max_workers=None):
        """Called when an executor has not been provided to make one."""
        return futurist.GreenThreadPoolExecutor(max_workers=max_workers)

    def _max_workers(self):
        if self.workers:
            return min(self.workers, self.MAX_WORKERS)
        return self.MAX_WORKERS
