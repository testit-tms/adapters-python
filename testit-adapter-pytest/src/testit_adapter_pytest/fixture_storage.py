import threading
from collections import OrderedDict, defaultdict


class ThreadContextFixtures:
    _thread_context = defaultdict(OrderedDict)
    _init_thread: threading.Thread

    @property
    def thread_context(self):
        context = self._thread_context[threading.current_thread()]
        if not context and threading.current_thread() is not self._init_thread:
            uuid, last_item = next(reversed(self._thread_context[self._init_thread].items()))
            context[uuid] = last_item
        return context

    def __init__(self, *args, **kwargs):
        self._init_thread = threading.current_thread()
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        self.thread_context.__setitem__(key, value)

    def __getitem__(self, item):
        return self.thread_context.__getitem__(item)

    def __iter__(self):
        return self.thread_context.__iter__()

    def __reversed__(self):
        return self.thread_context.__reversed__()

    def get(self, key):
        return self.thread_context.get(key)

    def pop(self, key):
        return self.thread_context.pop(key)

    def get_all(self):
        return dict(self.thread_context.items())
