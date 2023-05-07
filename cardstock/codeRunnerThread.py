# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Modified from the Killable Threads post by tomer filiba:
http://tomerfiliba.com/recipes/Thread2/
"""

import threading
import inspect
import queue
from wx import CallAfter
import ctypes

# -----------------------------------------
# Handle Stopping the runner thread, by injecting an exception, and then catching it in
# the runnerThread's runloop in runner.py - StartRunLoop()

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
    if res == 0:
        # raise ValueError("invalid thread id")
        pass
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class CodeRunnerThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.returnQueue = queue.Queue()
        self.is_terminated = False

    def _get_my_tid(self):
        """determines this (self's) thread id"""
        if not self.is_alive():
            # the thread is not active
            return None

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        # could not determine the thread's id
        return None

    def raise_exc(self, exctype):
        """raises the given exception type in the context of this thread"""
        tid = self._get_my_tid()
        if tid is not None:
            _async_raise(tid, exctype)

    def terminate(self):
        """raises SystemExit in the context of the given thread, which should
        cause the thread to exit silently (unless caught)"""
        self.is_terminated = True
        self.returnQueue.put(None) # Stop waiting for any currently running main-thread task
        self.raise_exc(SystemExit)
        self.returnQueue.put(None) # Stop waiting for any currently running main-thread task


# -----------------------------------------
# Build the @RunOnMainSync decorator, to run the function on the Main thread, and make the runnerThread wait for the
# return value, passed back through a queue

def to_main_sync(func, *args, **kwargs):
    """Run a function on the main thread, and await its return value so we can return it on the calling thread"""
    if threading.current_thread() == threading.main_thread():
        # on main thread
        return func(*args, **kwargs)
    else:
        # on non-main thread
        thread = threading.current_thread()
        # no more to_main calls once we're terminated
        if not thread.is_terminated:
            CallAfter(to_main_sync_helper, thread, func, *args, **kwargs)
            ret = thread.returnQueue.get() # wait for return value
            return ret
        return None


def to_main_sync_helper(thread, func, *args, **kwargs):
    # On main thread
    if not thread.is_terminated:
        try:
            ret = func(*args, **kwargs)
            thread.returnQueue.put(ret) # send return value to calling thread
        except Exception as e:
            thread.returnQueue.put(None) # send empty return value to calling thread
            raise e
    else:
        thread.returnQueue.put(None) # send empty return value to calling thread


def RunOnMainSync(func):
    """ Used as a decorator, to make Proxy object functions run on the main thread. """
    def wrapper_run_on_main(*args, **kwargs):
        return to_main_sync(func, *args, **kwargs)
    return wrapper_run_on_main


# -----------------------------------------
# Build the @RunOnMainAsync decorator, to run the function on the Main thread, and let the runnerThread continue
# without waiting for a return value -- no queue needed


def to_main_async(func, *args, **kwargs):
    """Run a function on the main thread, and await its return value so we can return it on the calling thread"""
    if threading.current_thread() == threading.main_thread():
        # on main thread
        func(*args, **kwargs)
    else:
        # on non-main thread
        thread = threading.current_thread()
        # no more to_main calls once we're terminated
        if not thread.is_terminated:
            CallAfter(to_main_async_helper, thread, func, *args, **kwargs)
        return None


def to_main_async_helper(thread, func, *args, **kwargs):
    # On main thread
    if not thread.is_terminated:
        func(*args, **kwargs)


def RunOnMainAsync(func):
    """ Used as a decorator, to make Proxy object functions run on the main thread. """
    def wrapper_run_on_main_async(*args, **kwargs):
        return to_main_async(func, *args, **kwargs)
    return wrapper_run_on_main_async
