ASCII Hackathon 2018 DooTu
---
This resources are made for ASCII IOT dev hackathon.

# Requirements
* pipenv (recommended)
* pyenv (recommended)

# Install
Use command bellow (If you use pipenv)

```
$ cd python
$ pipenv install
```

If you want to install resources for development, also use command bellow.
It will install jupyter notebook and so on, which is used to analize IMU data.
```
$ pipenv install --dev
```

# Usage
## Send IMU data from M5Stack Gray by Bluetooth
Open `arduino/m5stackgray/imu_bt/imu_bt.ino` by Arduino IDE and Upload it to M5Stack Gray.

## Detect someone go through the gate by M5Stack
Open `arduino/m5stackgray/gate/gate.ino` by Arduino IDE and Upload it to M5Stack Gray.

## Receive IMU data from M5Stack and filter by python
Run command bellow
```
pipenv run start_bt_receiver
```
or just run script directly by python. (version python(3 >) is required)
```
python python/src/main.py
```

## Display game state
Open `unity/display_practice/Assets/Main.unity` by Unity and run it.
