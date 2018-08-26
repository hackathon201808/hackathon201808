import collections
import time

import numpy as np

class GestureDetector:
    RECORD_SIZE = 50
    RAISE_GAP = 1000
    RAISE_BETWEEN = 2.0 # 2回振ったと判定される間隔
    def __init__(self):
        self.queues = {
            'ax': collections.deque(maxlen=self.RECORD_SIZE),
            'ay': collections.deque(maxlen=self.RECORD_SIZE),
            'az': collections.deque(maxlen=self.RECORD_SIZE),
        }
        self.last_raise_occured_at = 0

    def record(self, ax, ay, az):
        self.queues['ax'].append(ax)
        self.queues['ay'].append(ay)
        self.queues['az'].append(az)

    def _elapsed_from_last_raise(self):
        return self.last_raise_occured_at - time.time()
    
    def _is_raised(self, ax, ay, az):
        log_az = self.queues['az']
        avg_az = np.average(log_az)
        gap = az - avg_az

        if gap < self.RAISE_GAP:
            return False

        # 一度検出したら0.5秒は検知しない
        if self._elapsed_from_last_raise() < 0.5:
            return False

        self.last_raise_occured_at = time.time()
        return True
    
    def is_raised_twice(self, ax, ay, az):
        return self._is_raised(ax, ay, az) \
            and self._elapsed_from_last_raise() < self.RAISE_BETWEEN


