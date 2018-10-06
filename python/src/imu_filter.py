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
        """
        IMUから取得した情報を記録する
        data: M5Bridgeから渡されるIMUの情報
        """
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
        """
        重力要素を除去した加速度成分を取得する
        TODO: ローパスフィルタを用いて重力要素を除去しているだけなので、遅い動きを捉えられない
        TODO: 姿勢情報を使って除去する
        """
        non_biased = {}
        for k in ['ax', 'ay', 'az']:
            v = self.queues[k]
            if len(v) < 3:
                continue
            a = np.array(v, dtype=float)
            # 最新より3つ前以前のデータの平均
            ave = np.average(a[2:])
            # 最新2件の平均
            current_ave = np.average(a[:2])
            non_biased[k] = current_ave - ave
        return non_biased

    def get_pseudo_velocity(self):
        """
        一定期間で積分した擬似的な速度を取得する
        """
        keys = ['vx', 'vy', 'vz']
        vel = {}
        # 重力要素を除去した加速度情報を用いて速度を求める
        for k, nk in zip(keys, ['nx', 'ny', 'nz']):
            v = self.queues[nk]
            a = np.array(v, dtype=float)
            # TODO: 数値積分における微小時間を適当に0.1にせずにちゃんと計測するか調整する
            # TODO: より精度の高い数値積分法を用いる
            vel[k] = np.sum(a) * 0.1
        return vel