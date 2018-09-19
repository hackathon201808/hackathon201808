import collections
import time

import numpy as np


class IMUFilter:
    RECORD_SIZE = 10
    def __init__(self, on_filtered=None):
        self.queues = {
            'ax': collections.deque(maxlen=self.RECORD_SIZE),
            'ay': collections.deque(maxlen=self.RECORD_SIZE),
            'az': collections.deque(maxlen=self.RECORD_SIZE),
            'nx': collections.deque(maxlen=self.RECORD_SIZE*5),
            'ny': collections.deque(maxlen=self.RECORD_SIZE*5),
            'nz': collections.deque(maxlen=self.RECORD_SIZE*5),
        }
        self.last_raise_occured_at = 0
        self._on_filtered = on_filtered

    def record(self, data):
        for k in ['ax', 'ay', 'az']:
            self.queues[k].append(data[k])
        acc = self.get_natural_accel()
        if acc:
            for nk, k in zip(['nx', 'ny', 'nz'], ['ax', 'ay', 'az']):
                self.queues[nk].append(acc[k])

        if self._on_filtered:
            vel = self.get_pseudo_velocity()
            if acc and vel:
                filtered = acc.copy()
                filtered.update(vel)
                filtered['yaw'] = data['yaw']
                filtered['pitch'] = data['pitch']
                filtered['roll'] = data['roll']
                self._on_filtered(filtered)

    def get_natural_accel(self):
        non_biased = {}
        for k in ['ax', 'ay', 'az']:
            v = self.queues[k]
            if len(v) < 3:
                continue
            a = np.array(v, dtype=float)
            ave = np.average(a[2:])
            current_ave = np.average(a[:2])
            non_biased[k] = current_ave - ave
        return non_biased

    def get_pseudo_velocity(self):
        keys = ['vx', 'vy', 'vz']
        vel = {}
        for k, nk in zip(keys, ['nx', 'ny', 'nz']):
            v = self.queues[nk]
            a = np.array(v, dtype=float)
            vel[k] = np.sum(a) * 0.1
        return vel