import time

import serial
import pandas as pd
import numpy as np
import m5_bridge as m5b
import imu_filter as imuf


if __name__ == '__main__':
    def on_filtered(data):
        print(data['yaw'], data['pitch'], data['roll'])

    def on_button_pressed(a, b, c):
        # a is Take off. b is Land off. 
        print(a, b, c)

    filter = imuf.IMUFilter(on_filtered=on_filtered)
    # port = '/dev/tty.SLAB_USBtoUART'
    port = '/dev/tty.M5StackBluetoothSPP-ESP'

    baudrate = 115200
    imu = m5b.M5Brigde(port, baudrate, on_imu_recieved=filter.record, on_button_pressed=on_button_pressed)
    imu.start()
