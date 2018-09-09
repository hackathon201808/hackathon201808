import time

import imu_recorder as imur
import imu_filter as imuf

if __name__ == '__main__':
    def on_filtered(data):
        if data['ay'] > 0.4:
            print('thrown', time.time())
        if data['vz'] > 0.2:
            print('up', time.time())
        if data['vz'] < -0.2:
            print('down', time.time())

    filter = imuf.IMUFilter(on_filtered=on_filtered)
    imu = imur.IMUBTReciever('/dev/rfcomm0', 115200, handler=filter.record)
    imu.start()

