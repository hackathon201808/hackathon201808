#include <M5Stack.h>
#include "BluetoothSerial.h"
#include "IMU.h"
#include "log_util.h"

#define SerialDebug false // Set to true to get Serial output for debugging
#define LCD
#define sendByBT true

IMU* imu;
BluetoothSerial SerialBT;
uint32_t last_displayed;

void setup()
{
  M5.begin();
  Wire.begin();
  SerialBT.begin("M5StackBluetoothSPP"); // Bluetooth device name
  displayWelcome();
  delay(1000);

  imu = new IMU();

  displayAdress("MPU9250", imu->getAddress(), 0x71);
  delay(1000);
  displayAdress("AK8963", imu->getAK8963Adress(), 0x48);
  delay(1000);
  displayAccelGyroBias(imu->getAccelBias(), imu->getGyroBias());
  delay(1000);
  displayMagCalibration(imu->getMagCalibration());
  delay(1000);

  M5.Lcd.setTextSize(1);
  M5.Lcd.setTextColor(GREEN ,BLACK);
  M5.Lcd.fillScreen(BLACK);
}

void loop()
{
  float ax, ay, az, gx, gy, gz, mx, my, mz;
  float yaw, pitch, roll;
  imu->read(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz, &yaw, &pitch, &roll);

  uint32_t now = millis();
  if (now - last_displayed > 200)
  {
    auto frequency = imu->getFrequency();
    displayIMU(ax, ay, az, gx, gy, gz, mx, my, mz, yaw, pitch, roll, frequency);
    last_displayed = now;
  }
  uint8_t btnAPressed = 0;
  uint8_t btnBPressed = 0;
  uint8_t btnCPressed = 0;
  if (M5.BtnA.wasPressed()) {
    btnAPressed = 1;
  }
  if (M5.BtnB.wasPressed()) {
    btnBPressed = 1;
  }
  if (M5.BtnC.wasPressed()) {
    btnCPressed = 1;
  }
  SerialBT.printf(
    "axyzgxyzypr\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%d\t%d\t%d\r\n",
    ax, ay, az, gx, gy, gz, yaw, pitch, roll,
    btnAPressed, btnBPressed, btnCPressed);
  M5.update();
}
