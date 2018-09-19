import socket
from struct import Struct
import sys
import termios
import fcntl
import os
from getch import getch
from pynput.keyboard import Key, Listener
from threading import Thread, Timer
import time
import datetime


class Tello:

    TELLO_IP = '192.168.10.1'
    TELLO_PORT_CMD = 8889
    TELLO_PORT_VIDEO = 6038
    LOCAL_IP = '192.168.10.2'
    LOCAL_PORT_VIDEO = 8080

    # Tello Commands
    CMD_CONN_REQ = 'conn_req:'.encode() + TELLO_PORT_VIDEO.to_bytes(2,'little')
    CMD_REQ_IFRAME =(0xcc, 0x58, 0x00, 0x7c, 0x60, 0x25, 0x00, 0x00, 0x00, 0x6c, 0x95)
    CMD_TAKEOFF = (0xcc, 0x58, 0x00, 0x7c, 0x68, 0x54, 0x00, 0x01, 0x00, 0x6a, 0x90)
    CMD_LAND = (0xcc, 0x60, 0x00, 0x27, 0x68, 0x55, 0x00, 0x02, 0x00, 0x00, 0xc6, 0x5b)
    CMD_FLIGHT = (0xcc, 0xb0, 0x00, 0x7f, 0x60, 0x50, 0x00, 0x00, 0x00)
    STICK_HOVER = 1024
    STICK_H = 660
    STICK_M = 330
    STICK_L = 60
    STICK_ROLL_SENCER = 0
    STICK_PITCH_SENCER = 0

    # Format
    S11 = Struct("!11B")
    S12 = Struct("!12B")
    S22 = Struct("!22B")

    # CTC16 Table
    TBL_CRC16 = [
        0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf, 0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
        0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e, 0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
        0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd, 0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
        0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c, 0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
        0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb, 0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
        0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a, 0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
        0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9, 0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
        0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738, 0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
        0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7, 0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
        0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036, 0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
        0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5, 0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
        0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134, 0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
        0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3, 0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
        0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232, 0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
        0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1, 0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
        0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330, 0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78
    ]

    def __init__(self):

        self.stop_drone = False

        self.addr_cmd_tx = (self.TELLO_IP, self.TELLO_PORT_CMD)
        self.sock_cmd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Start Receiving Command
        #self.thread_cmd_rx = Thread(target=self._cmd_rx)
        #self.thread_cmd_rx.start()

        # Send Connection Request
        self._cmd_tx(self.CMD_CONN_REQ)

        # Initial Terminal Settings
        self.fd = sys.stdin.fileno()
        self.attr_org = termios.tcgetattr(self.fd)
        self.fcntl_org = fcntl.fcntl(self.fd, fcntl.F_GETFL)

        # Cancel Echo
        self._echo_off()

        # Initialize Tracking Interval
        self.tracking_interval = 2

        # Start Key Listener
        self.thread_key_listener = Thread(target=self._key_listener)
        self.thread_key_listener.start()

        # Initialize Flight Status
        self.in_flight = False
        # Initialize Run Status
        self.run_drone = False
        self.go_straight_drone = False
        self.stanby_drone = False

        # Initialize Flight Command
        self.mode = 0
        self.yaw = self.STICK_HOVER
        self.thr = self.STICK_HOVER
        self.pitch = self.STICK_HOVER
        self.roll = self.STICK_HOVER

        # Start Sending Flight Command
        self.thread_flight_ctrl = Thread(target=self._flight_ctrl)
        self.thread_flight_ctrl.start()

        # Start Requesting I-Frame
        self.thread_req_iframe = Thread(target=self._req_iframe)
        self.thread_req_iframe.start()

        # Start Forwarding Video
        self.thread_fwd_video = Thread(target=self._fwd_video)
        self.thread_fwd_video.start()

        # Initialize Tracking Flag
        self.is_tracking = False
        self.is_detect = False
        self.is_autopilot = False

        self.go_straight_pitch = self.STICK_H

        # Start Tracking Timer
        self.thread_timer_detect = Thread(target=self._timer_detect)
        self.thread_timer_detect.start()

    def _echo_off(self):
        attr = termios.tcgetattr(self.fd)
        attr[3] = attr[3] & ~termios.ECHO & ~termios.ICANON # & ~termios.ISIG
        termios.tcsetattr(self.fd, termios.TCSADRAIN, attr)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.fcntl_org | os.O_NONBLOCK)

    def _echo_on(self):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.fcntl_org)
        termios.tcsetattr(self.fd, termios.TCSANOW, self.attr_org)

    def _key_listener(self):
        with Listener(
            on_press = self._on_press,
            on_release = self._on_release
        ) as listener:
            listener.join()

    def _throw_drone(self):
        if self.go_straight_drone is False and self.stanby_drone:
            self.run_drone = True
            self.go_straight_drone = True
            print('go_straight_drone start')
            print('_auto_landoff start', self.go_straight_pitch)
            t = Timer(5, self._auto_landoff)
            t.start()
            t2 = Timer(0.02, self._go_straight_drone)
            t2.start()
        else:
            print('drone is runninng!')

    def _on_press(self, key):
        try:
            keyPressed = '{0}'.format(key.char)
            print('keyPressed!!' + str(keyPressed))
            if not self.is_tracking and keyPressed == '9':
                self.is_tracking = True
            elif self.is_tracking and keyPressed == '9':
                self.is_tracking = False
                self.is_autopilot = False
            elif self.is_tracking and not self.is_autopilot and keyPressed == '0':
                self.is_autopilot = True
            elif self.is_tracking and self.is_autopilot and keyPressed == '0':
                self.is_autopilot = False
            elif not self.is_autopilot and not self.run_drone and keyPressed == '1':
                if self.in_flight:
                    cmd = list(self.CMD_LAND)
                    self._cmd_tx(cmd)
                    self.in_flight = False
                    self.run_drone = False
                    print('_auto_landoff complete')
            elif not self.is_autopilot and not self.run_drone and keyPressed == '2':
                self.run_drone = True
                self.go_straight_drone = True
                print('go_straight_drone start')
                print('_auto_landoff start')
                t = Timer(5, self._auto_landoff)
                t.start()
                t2 = Timer(0.02, self._go_straight_drone)
                t2.start()
            elif not self.is_autopilot and not self.run_drone and keyPressed == '3':
                self.stanby_drone = True
                print('drone is stanby')
            elif not self.is_autopilot:
                if keyPressed == 'W':
                    self.thr = self.STICK_HOVER + self.STICK_H
                elif keyPressed == 'w':
                    self.thr = self.STICK_HOVER + self.STICK_M
                elif keyPressed == 'S':
                    self.thr = self.STICK_HOVER - self.STICK_H
                elif keyPressed == 's':
                    self.thr = self.STICK_HOVER - self.STICK_M
                elif keyPressed == 'A':
                    self.yaw = self.STICK_HOVER - self.STICK_H
                elif keyPressed == 'a':
                    self.yaw = self.STICK_HOVER - self.STICK_M
                elif keyPressed == 'D':
                    self.yaw = self.STICK_HOVER + self.STICK_H
                elif keyPressed == 'd':
                    self.yaw = self.STICK_HOVER + self.STICK_M
                elif keyPressed == 'I':
                    self.pitch = self.STICK_HOVER + self.STICK_H
                elif keyPressed == 'i':
                    self.pitch = self.STICK_HOVER + self.STICK_M
                elif keyPressed == 'K':
                    self.pitch = self.STICK_HOVER - self.STICK_H
                elif keyPressed == 'k':
                    self.pitch = self.STICK_HOVER - self.STICK_M
                elif keyPressed == 'J':
                    self.roll = self.STICK_HOVER - self.STICK_H
                elif keyPressed == 'j':
                    self.roll = self.STICK_HOVER - self.STICK_M
                elif keyPressed == 'L':
                    self.roll = self.STICK_HOVER + self.STICK_H
                elif keyPressed == 'l':
                    self.roll = self.STICK_HOVER + self.STICK_M
                elif not self.go_straight_drone:
                    self.thr = self.STICK_HOVER
                    self.yaw = self.STICK_HOVER
                    self.pitch = self.STICK_HOVER
                    self.roll = self.STICK_HOVER
        except AttributeError:
            keyPressed = '{0}'.format(key)
            if not self.in_flight and keyPressed == 'Key.space':
                cmd = list(self.CMD_TAKEOFF)
                self._cmd_tx(cmd)
                self.in_flight = True
                print('takeoff')
            elif self.in_flight and keyPressed == 'Key.space':
                cmd = list(self.CMD_LAND)
                self._cmd_tx(cmd)
                self.in_flight = False
            elif not self.in_flight and keyPressed == 'Key.enter':
                self.stop_drone = True
                self._echo_on()
                while True:
                    clearBuffer = getch()
                    if clearBuffer == '\n':
                        break
                return False
            elif not self.is_autopilot:
                if keyPressed == 'Key.up':
                    self.pitch = self.STICK_HOVER + self.STICK_M
                elif keyPressed == 'Key.down':
                    self.pitch = self.STICK_HOVER - self.STICK_M
                elif keyPressed == 'Key.left':
                    self.roll = self.STICK_HOVER - self.STICK_M
                elif keyPressed == 'Key.right':
                    self.roll = self.STICK_HOVER + self.STICK_M
                else:
                    self.thr = self.STICK_HOVER
                    self.yaw = self.STICK_HOVER
                    self.pitch = self.STICK_HOVER
                    self.roll = self.STICK_HOVER
            
    def _on_release(self, key):
        if not self.is_autopilot:
            self.thr = self.STICK_HOVER
            self.yaw = self.STICK_HOVER
            self.pitch = self.STICK_HOVER
            self.roll = self.STICK_HOVER
        else:
            return

    def _cmd_rx(self):
        while True:
            try:
                data, server = self.sock_cmd.recvfrom(1518)
                print('Rx: ' + str(data))
            except Exception as e:
                print(e)
                break

    def _cmd_tx(self, cmd):
        if type(cmd) == bytes:
            cmd = cmd
            self.sock_cmd.sendto(cmd, self.addr_cmd_tx)
        elif type(cmd) == list:
            if len(cmd) == 11:
                s = self.S11
            elif len(cmd) == 12:
                s = self.S12
            elif len(cmd) == 22:
                s = self.S22
            else:
                return
                #print('Tx: unknown format')
            if s:
                cmd = s.pack(*cmd)
                self.sock_cmd.sendto(cmd, self.addr_cmd_tx)
                #print('Tx: ' + str(cmd))

    def _flight_ctrl(self):
        c = (self.mode<<44) + (self.yaw<<33) + (self.thr<<22) + (self.pitch<<11) + (self.roll)
        cmd = list(self.CMD_FLIGHT)
        for i in range(0,6):
            cmd.append(c>>(8*i)&0xff)
        now = datetime.datetime.now()
        h = now.hour
        m = now.minute
        s = now.second
        ms = round(now.microsecond / 1000)
        cmd.append(h)
        cmd.append(m)
        cmd.append(s)
        cmd.append(ms & 0xff)
        cmd.append(ms >> 8)
        buf = bytearray()
        for b in cmd:
            buf.append(b)
        crc16 = self._calc_crc16(buf, len(buf))
        cmd.append(crc16 & 0xff)
        cmd.append(crc16 >> 8)
        self._cmd_tx(cmd)
        if not self.stop_drone:
            t = Timer(0.02, self._flight_ctrl)
            t.start()

    def _req_iframe(self):
        cmd = list(self.CMD_REQ_IFRAME)
        self._cmd_tx(cmd)
        if not self.stop_drone:
            t = Timer(1, self._req_iframe)
            t.start()
        else:
            self.sock_cmd.close()

    def _fwd_video(self):
        self.sock_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr_video = (self.LOCAL_IP, self.TELLO_PORT_VIDEO)
        self.sock_video.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_video.settimeout(.5)
        self.sock_video.bind(self.addr_video)
        self.sock_fwd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr_fwd = (self.LOCAL_IP, self.LOCAL_PORT_VIDEO)
        self.sock_fwd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_fwd.settimeout(.5)
        data = bytearray(4096)
        slice = bytearray()
        isSps = False

        while not self.stop_drone:
            try:
                size, addr = self.sock_video.recvfrom_into(data)
            except socket.timeout:
                time.sleep(.5)
                continue
            except socket.error as e:
                print(e)
                break
            else:
                if size > 6 and data[2] == 0x00 and data[3] == 0x00 and data[4] == 0x00 and data[5] == 0x01:
                    nal_type = data[6] & 0x1f
                    if nal_type == 7:
                        isSps = True
                if isSps:
                    self.sock_fwd.sendto(data[2:size], self.addr_fwd)
        self.sock_video.close()
        self.sock_fwd.close()

    def _timer_detect(self):
        self.is_detect = True
        if not self.stop_drone:
            t = Timer(self.tracking_interval, self._timer_detect)
            t.start()

    def _calc_crc16(self, buf, size):
        i = 0
        seed = 0x3692
        while size > 0:
            seed = self.TBL_CRC16[(seed ^ buf[i]) & 0xff] ^ (seed >> 8)
            i = i + 1
            size = size - 1

        return seed

    def _auto_landoff(self):
        if self.in_flight:
            self.go_straight_pitch = self.STICK_H
            cmd = list(self.CMD_LAND)
            self._cmd_tx(cmd)
            self.in_flight = False
            self.run_drone = False
            self.go_straight_drone = False
            self.stanby_drone = False
            print('_auto_landoff complete')

    def _go_straight_drone(self):
        if self.in_flight:
            if self.go_straight_pitch > 0:
                print('go_straight_drone doing:' + str(self.go_straight_pitch))
                self.pitch = self.STICK_HOVER + self.go_straight_pitch
                self.go_straight_pitch = self.go_straight_pitch - 5
            else:
                # t = Timer(0.02, self._auto_landoff)
                # t.start()
                self.go_straight_pitch = 0
                self.go_straight_drone = False
                self.stanby_drone = False
            if not self.stop_drone and self.in_flight:
                t = Timer(0.5, self._go_straight_drone)
                t.start()
            else:
                print('drone is stop')

    def _ctrl_drone_bysenser(self):
        # print('roll!', abs(self.STICK_ROLL_SENCER), 'thr!', abs(self.STICK_PITCH_SENCER))
        if abs(self.STICK_ROLL_SENCER) > 60.0 or abs(self.STICK_PITCH_SENCER) > 60.0:
            print(self.go_straight_drone, self.stanby_drone)
            if self.go_straight_drone and self.stanby_drone:
                if abs(self.STICK_ROLL_SENCER) > abs(self.STICK_PITCH_SENCER):
                    self.roll = self.STICK_HOVER + self.STICK_ROLL_SENCER
                    print('ROOOOOOOLLLLL!!! roll!', self.STICK_ROLL_SENCER, 'thr!', self.STICK_PITCH_SENCER)
                else:
                    self.thr = self.STICK_HOVER - self.STICK_PITCH_SENCER
                    print('PPPPPPPPPPPPIIITCHHH!!! roll!', self.STICK_ROLL_SENCER, 'thr!', self.STICK_PITCH_SENCER)

