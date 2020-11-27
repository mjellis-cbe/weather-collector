# -*- coding: utf-8 -*-
"""
Generic runner class responsible for running a function periodically
"""
import logging
import time
from threading import Event, Thread

__author__ = "Matt Ellis"
__copyright__ = "Matt Ellis"
__license__ = "mit"

_logger = logging.getLogger(__name__)


class SynchronousEvent:
    """
    Repeat an event `function` every `interval` seconds.

    Args:
        interval (float): Interval in seconds
        function: Callable function
        *args: Positional arguments for function
        **kwargs: Keyword arguments function

    Attributes:
        interval (float): Interval in seconds
        function: Callable function
        args (tuple): Positional arguments for function
        kwargs (dict): Keyword arguments for function
        start_time (float): time to start
        event (:obj:`Event`): Event
        thread (:obj:`Thread`): Tread
    """
    def __init__(self, interval, function, *args, **kwargs):
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.event = None
        self.thread = None
        self.start_time = None

    def _target(self):
        while not self.event.wait(self._time):
            self.function(*self.args, **self.kwargs)

    @property
    def _time(self):
        return self.interval - ((time.time()-self.start_time) % self.interval)

    def start(self):
        """Start the execution of event"""
        if self.thread is None:
            self.thread = Thread(target=self._target)
        if self.event is None:
            self.event = Event()
        cur_time = time.time()
        self.start_time = cur_time - cur_time % self.interval + self.interval
        self.thread.start()

    def stop(self):
        """Terminate execution of event"""
        self.event.set()
        self.thread.join()
        self.thread = None
        self.event = None
