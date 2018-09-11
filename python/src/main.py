import time

import serial
import pandas as pd
import numpy as np
import m5_bridge as m5b
import imu_filter as imuf


if __name__ == '__main__':
    def on_filtered(data):
        if data['ay'] > 0.4:
            print('thrown', time.time())
        if data['vz'] > 0.2:
            print('up', time.time())
        if data['vz'] < -0.2:
            print('down', time.time())

    def on_button_pressed(a, b, c):
        print(a, b, c)

    filter = imuf.IMUFilter(on_filtered=on_filtered)
    port = '/dev/tty.SLAB_USBtoUART'
    baudrate = 115200
    imu = m5b.M5Brigde(port, baudrate, on_imu_recieved=filter.record, on_button_pressed=on_button_pressed)
    imu.start()

