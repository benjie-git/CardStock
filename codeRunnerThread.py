"""
Modified from the Killable Threads post by tomer filiba:
http://tomerfiliba.com/recipes/Thread2/
"""

import threading
import inspect
import queue
from wx import CallAfter
import ctypes

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
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        raise AssertionError("could not determine the thread's id")

    def raise_exc(self, exctype):
        """raises the given exception type in the context of this thread"""
        _async_raise(self._get_my_tid(), exctype)

    def terminate(self):
        """raises SystemExit in the context of the given thread, which should
        cause the thread to exit silently (unless caught)"""
        self.is_terminated = True
        self.returnQueue.put(None) # Stop waiting for any currently running main-thread task
        self.raise_exc(SystemExit)
        self.returnQueue.put(None) # Stop waiting for any currently running main-thread task


def to_main_sync(callable, *args, **kwargs):
    """Run a function on the main thread, and await its return value so we can return it on the calling thread"""
    if threading.current_thread() == threading.main_thread():
        # on main thread
        return callable(*args, **kwargs)
    else:
        # on non-main thread
        thread = threading.current_thread()
        # no more to_main calls once we're terminated
        if not thread.is_terminated:
            CallAfter(to_main_helper, thread, callable, *args, **kwargs)
            ret = thread.returnQueue.get() # wait for return value
            return ret
        return None


def to_main_helper(thread, callable, *args, **kwargs):
    # On main thread
    if not thread.is_terminated:
        try:
            ret = callable(*args, **kwargs)
            thread.returnQueue.put(ret) # send return value to calling thread
        except Exception as e:
            thread.returnQueue.put(None) # send empty return value to calling thread
            raise e
    else:
        thread.returnQueue.put(None) # send empty return value to calling thread


def RunOnMain(func):
    """ Used as a decorator, to make Proxy object functions run on the main thread. """
    def wrapper_run_on_main(*args, **kwargs):
        return to_main_sync(func, *args, **kwargs)
    return wrapper_run_on_main
