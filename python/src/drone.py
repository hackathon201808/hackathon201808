import tello
import numpy as np
import cv2
import sys
import time
import datetime
import collections
import serial
import math as m
import pandas as pd
import numpy as np
import concurrent.futures
# M5Stack
import pandas as pd
import m5_bridge as m5b
import imu_filter as imuf


PORT = '/dev/tty.SLAB_USBtoUART'
BAUDRATE = 115200

data_frame = pd.DataFrame(columns=['time', 'ax', 'ay', 'az', 'gx', 'gy', 'gz'])
start_at = time.time()
initialized = False
drone_throw = False

drone = tello.Tello()

ax = 0.0
ay = 0.0
az = 0.0
yaw = 0.0
pitch = 0.0
roll = 0.0


FILTER_SIZE = 10
queues = {
    'ax': collections.deque(maxlen=FILTER_SIZE),
    'ay': collections.deque(maxlen=FILTER_SIZE),
    'az': collections.deque(maxlen=FILTER_SIZE),
}

throw_queues = {
    'ax_norm': collections.deque(maxlen=FILTER_SIZE),
}
SHAKED_THRESHOLD = 25000

LOCAL_IP = '192.168.10.2'
LOCAL_PORT_VIDEO = '8080'

# Center Cordinates
CX = 480
CY = 360

# Reference Distance
L0 = 100
S0 = 25600

# Base Distance
LB = 120


# Initialize Tracker
def tracker_init(frame):
    global bbox
    rc = 1
    w_cur = 0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        if w >= w_cur:
            bbox = (x,y,w,h)
            w_cur = w
        bbox = (x,y,w,h)
    if w_cur > 0:
        rc = 0
    return rc


# Create Tracker
def tracker_create(tracker_type):
    global tracker
    if tracker_type == 'BOOSTING':
        tracker = cv2.TrackerBoosting_create()
    if tracker_type == 'MIL':
        tracker = cv2.TrackerMIL_create()
    if tracker_type == 'KCF':
        tracker = cv2.TrackerKCF_create()
    if tracker_type == 'TLD':
        tracker = cv2.TrackerTLD_create()
    if tracker_type == 'MEDIANFLOW':
        tracker = cv2.TrackerMedianFlow_create()
    if tracker_type == 'GOTURN':
        tracker = cv2.TrackerGOTURN_create()


def on_data_recieved(ax, ay, az, y, p, r):
    # print(ax, ay, az, y, p, r)
    global drone_throw, throw_queues
    record(ax, ay, az)
    acc, acc_array = get_filtered_values()
    # print(acc,acc_array)
    ypr_array = np.array([y, p, r], dtype=float)
    ax_norm = np.linalg.norm(acc_array)
    ax_norm_max = 0
    # print(time.time(), ax_norm, acc['ax'])
    if acc['ax'] > 15000:
        drone_throw = True
        # print(time.time(), ax_norm, acc['ax'])
        throw_record(ax_norm)
    elif drone_throw:
        print('none')
        drone_throw = False
        filtered, ax_norm_max = get_average_ax_norm()
        throw_queues['ax_norm'].clear()
        print(ax_norm_max)
    return ax_norm_max, ypr_array[1], ypr_array[2]


def record(ax, ay, az):
    global queues
    queues['ax'].append(ax)
    queues['ay'].append(ay)
    queues['az'].append(az)


def throw_record(ax_norm):
    global throw_queues
    throw_queues['ax_norm'].append(ax_norm)


def get_filtered_values():
    filtered = {}
    for k, v in queues.items():
        a = np.array(v, dtype=float)
        filtered[k] = np.average(a)
    ax_array = np.array([filtered['ax'], filtered['ay'], filtered['az']])
    return filtered, ax_array


def get_average_ax_norm():
    filtered = {}
    for k, v in throw_queues.items():
        # print(k, v)
        a = np.array(v, dtype=float)
        filtered[k] = np.amax(a)
    ax_norm_max = filtered['ax_norm']
    return filtered, ax_norm_max


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


def scale_number(unscaled, to_min, to_max, from_min, from_max):
    return (to_max-to_min)*(unscaled-from_min)/(from_max-from_min)+to_min


# 傾き計算(1軸の傾斜の計算) for accel data
# 1軸だけ傾く場合はこの関数で計算できる.
def calc_slope_for_accel_1axis(x, y, z): # radian
    #
    # θ = asin(出力加速度[g]/1g)
    #
    # Y, Z軸固定. X軸だけ傾いた場合.
    if x > 1:    x = 1
    elif x < -1: x = -1
    slope_x = m.asin( x / 1 )
    # X, Z軸固定. Y軸だけ傾いた場合.
    if y > 1: y = 1
    elif y < -1: y = -1
    slope_y = m.asin( y / 1 )
    # X, Y軸固定. Z軸だけ傾いた場合.
    if z > 1: z = 1
    elif z < -1: z = -1
    slope_z = m.asin( z / 1 )
    return [slope_x, slope_y, slope_z]


# 傾き計算(2軸の傾斜の計算) for accel data
# 2軸を使用することで360°測定できる.
def calc_slope_for_accel_2axis_deg(x, y, z): # degree
    #
    # θ = atan(X軸出力加速度[g]/Y軸出力加速度[g])
    #
    slope_xy = m.atan( x / y )
    deg_xy = m.degrees( slope_xy )
    if x > 0 and y > 0:    # 第1象限(0°〜+90°).
        deg_xy = deg_xy
    if x > 0 and y < 0:    # 第2象限(+90°〜±180°).
        deg_xy += 180.0
    if x < 0 and y < 0:    # 第3象限(±180°〜-90°).
        deg_xy -= 180.0
    if x < 0 and y > 0:    # 第4象限(-90°〜0°).
        deg_xy = deg_xy
#    slope_xy = m.atan2( x, y )
#    deg_xy = m.degrees( slope_xy )
    return deg_xy


# 傾き計算(3軸の傾斜の計算) for accel data
# 3軸を使用することで完全な球体(θΨΦ)を測定できる.
# θ = 水平線とX軸との角度
# Ψ = 水平線とy軸との角度
# Φ = 重力ベクトルとz軸との角度
def calc_slope_for_accel_3axis_deg(x, y, z): # degree
    # θ（シータ）
    theta = m.atan( x / m.sqrt( y*y + z*z ) )
    # Ψ（プサイ）
    psi = m.atan( y / m.sqrt( x*x + z*z ) )
    # Φ（ファイ）
    phi = m.atan( m.sqrt( x*x + y*y ) / z )

    deg_theta = m.degrees( theta )
    deg_psi = m.degrees(psi)
    deg_phi = m.degrees(phi)
    return [deg_theta, deg_psi, deg_phi]


def on_filtered(data):
    global initialized, drone

    if not initialized:
        initialized = True
        start_at = time.time()
        print("start at :", start_at)
    ar_max, roll, pitch = on_data_recieved(data['ax'], data['ay'], data['az'], data['yaw'], data['pitch'], data['roll'])
    # print(data['ay'], roll, pitch)

    if data['ay'] > 0.4:
        ar_max_scale = scale_number(data['ay'], 330, 400, 0.4, 1.0)
        print('pitch:', ar_max_scale)
        drone.go_straight_pitch = int(ar_max_scale)
        drone._throw_drone()
    drone.STICK_ROLL_SENCER = int(scale_number(roll, 0, 480, 0, 80))
    drone.STICK_PITCH_SENCER = int(scale_number(pitch, 0, 480, 0, 80))
    drone._ctrl_drone_bysenser()

    if drone.stop_drone:
        print('stop: ' + str(drone.stop_drone))
        time.sleep(1)


def on_button_pressed(a, b, c):
    # a is Take off. b is Land off. 
    print(a, b, c)


if __name__ == '__main__':
    print('Connect Tello...')
    addr = 'udp://' + LOCAL_IP + ':' + str(LOCAL_PORT_VIDEO) + '?overrun_nonfatal=1&fifo_size=50000000'

    print('Connect M5Stack...')
    filter = imuf.IMUFilter(on_filtered=on_filtered)
    port = '/dev/tty.M5StackBluetoothSPP-ESP'
    baudrate = 115200
    imu = m5b.M5Brigde(port, baudrate, on_imu_recieved=filter.record, on_button_pressed=on_button_pressed)
    imu.start()

