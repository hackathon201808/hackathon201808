import time
import datetime

import serial
import pandas as pd


class M5Brigde:
    def __init__(self, port, baudrate, on_imu_recieved=None, record=False, on_button_pressed=None):
        self._port = port
        self._baudrate = baudrate
        self._columns=['ax', 'ay', 'az', 'gx', 'gy', 'gz', 'yaw', 'pitch', 'roll']
        self._data_frame = pd.DataFrame(columns=self._columns)
        self._start_at = None
        self._on_imu_recieved = on_imu_recieved
        self._on_button_pressed = on_button_pressed
        self._record = record
    
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
                button_state = data[10:]
                data = data[1:10]
                now = time.time()
                if not self._start_at:
                    self._start_at = now
                elapsed = now - self._start_at
                parsed_data = {k: float(v) for k, v in zip(self._columns, data)}
                parsed_data['time'] = elapsed
                self._on_data_recieved(parsed_data, button_state)

                if elapsed > 2.0 and self._record:
                    self._save()
                    break

    def _on_data_recieved(self, imu_state, button_state):
        if self._on_imu_recieved:
            self._on_imu_recieved(imu_state)
        a, b, c = [s is '1' for s in button_state]
        if a or b or c and self._on_button_pressed:
            self._on_button_pressed(a, b, c)
        if self._record:
            self._make_log(imu_state)

    def _make_log(self, data):
        s = pd.Series(data)
        self._data_frame = self._data_frame.append(s, ignore_index=True)

    def _save(self):
        self._data_frame.to_csv("analytics/log/log-{0:%Y-%m-%d-%H-%M-%S}.csv".format(datetime.datetime.now()))


if __name__ == '__main__':
    recorder = M5Brigde('/dev/rfcomm0', 115200)
    recorder.start()
