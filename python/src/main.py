import time
import datetime
import collections

import serial
import pandas as pd
import numpy as np

PORT = '/dev/ttyUSB0'
BAUDRATE = 38400

data_frame = pd.DataFrame(columns=['time', 'ax', 'ay', 'az', 'gx', 'gy', 'gz'])
start_at = time.time()
initialized = False

FILTER_SIZE = 10
queues = {
    'ax': collections.deque(maxlen=FILTER_SIZE),
    'ay': collections.deque(maxlen=FILTER_SIZE),
    'az': collections.deque(maxlen=FILTER_SIZE),
    'gx': collections.deque(maxlen=FILTER_SIZE),
    'gy': collections.deque(maxlen=FILTER_SIZE),
    'gz': collections.deque(maxlen=FILTER_SIZE),
}
SHAKED_THRESHOLD = 25000

def main():
    global initialized, start_at
    with serial.Serial(PORT, timeout=0.1, baudrate=BAUDRATE) as se:
        while True:
            line = se.readline()
            raw_str = str(line)[:-5]
            data = raw_str.split('\\t')
            if len(data) < 7:
                continue
            if not initialized:
                initialized = True
                start_at = time.time()
            sensor_data = data[1:]
            should_save = on_data_recieved(*sensor_data)
            if should_save:
                save()
                break

def on_data_recieved(ax, ay, az, gx, gy, gz):
    # print(ax, ay, az, gx, gy, gz)
    record(ax, ay, az, gx, gy, gz)
    acc, acc_array = get_filtered_values()
    ax_norm = np.linalg.norm(acc_array)
    if ax_norm > SHAKED_THRESHOLD and acc['ay'] > 0:
        print(time.time(), 'shaked!!!!!', acc['ay'])
    # return make_log(ax, ay, az, gx, gy, gz)
    return False

def record(ax, ay, az, gx, gy, gz):
    global queues
    queues['ax'].append(ax)
    queues['ay'].append(ay)
    queues['az'].append(az)
    queues['gx'].append(gx)
    queues['gy'].append(gy)
    queues['gz'].append(gz)

def get_filtered_values():
    filtered = {}
    for k, v in queues.items():
        a = np.array(v, dtype=float)
        filtered[k] = np.average(a)
    ax_array = np.array([filtered['ax'], filtered['ay'], filtered['az']])
    return filtered, ax_array

def make_log(ax, ay, az, gx, gy, gz):
    global data_frame
    elapsed = time.time() - start_at
    s = pd.Series({
        'time': elapsed,
        'ax': ax,
        'ay': ay,
        'az': az,
        'gx': gx,
        'gy': gy,
        'gz': gz,
    })
    data_frame = data_frame.append(s, ignore_index=True)
    return elapsed > 10.0


def save():
    global data_frame
    data_frame.to_csv("../analytics/log/log-{0:%Y-%m-%d-%H-%M-%S}.csv".format(datetime.datetime.now()))


if __name__ == '__main__':
    main()
