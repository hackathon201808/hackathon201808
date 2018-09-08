import time
import datetime
import collections

import serial
import pandas as pd
import numpy as np

import gesture_detector as gd

# PORT = '/dev/ttyUSB0'
PORT = '/dev/rfcomm0'
BAUDRATE = 115200

data_frame = pd.DataFrame(columns=['time', 'ax', 'ay', 'az', 'gx', 'gy', 'gz'])
start_at = time.time()
initialized = False

FILTER_SIZE = 10
queues = {
    'ax': collections.deque(maxlen=FILTER_SIZE),
    'ay': collections.deque(maxlen=FILTER_SIZE),
    'az': collections.deque(maxlen=FILTER_SIZE),
}
SHAKED_THRESHOLD = 25000

gesture_detector = gd.GestureDetector()

def main():
    global initialized, start_at
    with serial.Serial(PORT, timeout=0.1, baudrate=BAUDRATE) as se:
        while True:
            line = se.readline()
            # print(str(line))
            raw_str = str(line)[:-5]
            data = raw_str.split('\\t')
            # print(len(data))
            if len(data) < 7:
                continue
            ax, ay, az, y, p, r = data[1:]
            ax = float(ax)
            ay = float(ax)
            az = float(az)
            y = float(y)
            p = float(p)
            r = float(r)
            if not initialized:
                initialized = True
                start_at = time.time()
            should_save = on_data_recieved(ax, ay, az, y, p, r)
            if should_save:
                save()
                break

def on_data_recieved(ax, ay, az, y, p, r):
    # print(ax, ay, az, gx, gy, gz)
    print(ax, ay, az, y, p, r)
    record(ax, ay, az)
    gesture_detector.record(ax, ay, az)

    acc, acc_array= get_filtered_values()
    ypr_array = np.array([y, p, r], dtype=float)
    ax_norm = np.linalg.norm(acc_array)
    if ax_norm > SHAKED_THRESHOLD and acc['ay'] < -1000:
        print(ax_norm)
        print(time.time(), 'shaked!!!!!', acc['ay'])
    if gesture_detector.is_raised_twice(ax, ay, az):
        print('raised twice !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    roll = ypr_array[1]
    return False

def record(ax, ay, az):
    global queues
    queues['ax'].append(ax)
    queues['ay'].append(ay)
    queues['az'].append(az)

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
