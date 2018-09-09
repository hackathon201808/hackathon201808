import time
import datetime

import serial
import pandas as pd


class IMUBTRecorder:
    def __init__(self, port, baudrate):
        self._port = port
        self._baudrate = baudrate
        self._columns=['ax', 'ay', 'az', 'gx', 'gy', 'gz', 'yaw', 'pitch', 'roll']
        self._data_frame = pd.DataFrame(columns=self._columns)
        self._start_at = None
    
    def start(self):
        with serial.Serial(self._port, timeout=0.1, baudrate=self._baudrate) as se:
            while True:
                line = se.readline()
                # remove return and line feed
                str_data = str(line).split('\\r\\n')[:-1]
                if not str_data:
                    continue
                # split by tag
                data = str_data[0].split('\\t')
                if len(data) < 10:
                    continue
                # remove data name column
                data = data[1:]
                now = time.time()
                if not self._start_at:
                    self._start_at = now
                elapsed = now - self._start_at
                parsed_data = {k: float(v) for k, v in zip(self._columns, data)}
                parsed_data['time'] = elapsed
                self._on_data_recieved(parsed_data)
                if elapsed > 2.0:
                    self._save()
                    break

    def _on_data_recieved(self, data):
        # print(data)
        self._make_log(data)

    def _make_log(self, data):
        s = pd.Series(data)
        self._data_frame = self._data_frame.append(s, ignore_index=True)

    def _save(self):
        self._data_frame.to_csv("analytics/log/log-{0:%Y-%m-%d-%H-%M-%S}.csv".format(datetime.datetime.now()))


if __name__ == '__main__':
    recorder = IMUBTRecorder('/dev/rfcomm0', 115200)
    recorder.start()
