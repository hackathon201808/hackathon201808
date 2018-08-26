import collections
import time

import numpy as np

class GestureDetector:
    RECORD_SIZE = 50
    RAISE_GAP = 2000
    BLIND_TIME = 0.5 # 連続してraiseを検知しない時間
    RAISE_BETWEEN = 1.5 # 2回振ったと判定される間隔
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
        return time.time() - self.last_raise_occured_at
    
    def _is_raised(self, ax, ay, az):
        log_az = self.queues['az']
        record_weight = np.array([0.96**i for i in range(len(log_az))])
        avg_az = np.average(log_az, weights=record_weight)
        gap = az - avg_az

        if gap < self.RAISE_GAP:
            return False

        # 一度検出したらしばらくは検知しない
        if self._elapsed_from_last_raise() < self.BLIND_TIME:
            return False

        self.last_raise_occured_at = time.time()
        return True
    
    def is_raised_twice(self, ax, ay, az):
        return self._is_raised(ax, ay, az) \
            and self._elapsed_from_last_raise() < self.RAISE_BETWEEN


