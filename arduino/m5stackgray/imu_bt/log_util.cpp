#include "log_util.h"

#include <M5Stack.h>

void displayWelcome()
{
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextColor(WHITE, BLACK); // Set pixel color; 1 on the monochrome screen
    M5.Lcd.setTextSize(2);

    M5.Lcd.setCursor(0, 0);
    M5.Lcd.print("MPU9250");
    M5.Lcd.setTextSize(1);
    M5.Lcd.setCursor(0, 20);
    M5.Lcd.print("9-DOF 16-bit");
    M5.Lcd.setCursor(0, 30);
    M5.Lcd.print("motion sensor");
    M5.Lcd.setCursor(20, 40);
    M5.Lcd.print("60 ug LSB");
}

void displayAdress(std::string name, unsigned char address, unsigned char expected)
{
    M5.Lcd.fillScreen(BLACK);          // clears the screen and buffer
    M5.Lcd.setTextColor(WHITE, BLACK); // Set pixel color; 1 on the monochrome screen
    M5.Lcd.setTextSize(1);             // Set text size to normal, 2 is twice normal etc.

    M5.Lcd.setCursor(20, 0);
    M5.Lcd.print(name.c_str());
    M5.Lcd.setCursor(0, 10);
    M5.Lcd.print("I AM");
    M5.Lcd.setCursor(0, 20);
    M5.Lcd.print(address, HEX);
    M5.Lcd.setCursor(0, 30);
    M5.Lcd.print("I Should Be");
    M5.Lcd.setCursor(0, 40);
    M5.Lcd.print(expected, HEX);
}

void displayAccelGyroBias(float *accelBias, float *gyroBias)
{
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextSize(1);

    M5.Lcd.setCursor(0, 0);
    M5.Lcd.print("MPU9250 bias");
    M5.Lcd.setCursor(0, 16);
    M5.Lcd.print(" x   y   z  ");

    M5.Lcd.setCursor(0, 32);
    M5.Lcd.print((int)(1000 * accelBias[0]));
    M5.Lcd.setCursor(32, 32);
    M5.Lcd.print((int)(1000 * accelBias[1]));
    M5.Lcd.setCursor(64, 32);
    M5.Lcd.print((int)(1000 * accelBias[2]));
    M5.Lcd.setCursor(96, 32);
    M5.Lcd.print("mg");

    M5.Lcd.setCursor(0, 48);
    M5.Lcd.print(gyroBias[0], 1);
    M5.Lcd.setCursor(32, 48);
    M5.Lcd.print(gyroBias[1], 1);
    M5.Lcd.setCursor(64, 48);
    M5.Lcd.print(gyroBias[2], 1);
    M5.Lcd.setCursor(96, 48);
    M5.Lcd.print("o/s");
}

void displayMagCalibration(float *magCalibration)
{
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextSize(1);

    M5.Lcd.setCursor(20,0); M5.Lcd.print("AK8963");
    M5.Lcd.setCursor(0,10); M5.Lcd.print("ASAX "); M5.Lcd.setCursor(50,10);
    M5.Lcd.print(magCalibration[0], 2);
    M5.Lcd.setCursor(0,20); M5.Lcd.print("ASAY "); M5.Lcd.setCursor(50,20);
    M5.Lcd.print(magCalibration[1], 2);
    M5.Lcd.setCursor(0,30); M5.Lcd.print("ASAZ "); M5.Lcd.setCursor(50,30);
    M5.Lcd.print(magCalibration[2], 2);
}

void displayIMU(float ax, float ay, float az,
                float gx, float gy, float gz,
                float mx, float my, float mz,
                float yaw, float pitch, float roll,
                float frequency)
{
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.print("     x       y       z ");
    M5.Lcd.setCursor(0, 24);
    M5.Lcd.printf("% 6d  % 6d  % 6d     mg   \r\n", (int)(1000 * ax), (int)(1000 * ay), (int)(1000 * az));
    M5.Lcd.setCursor(0, 44);
    M5.Lcd.printf("% 6d  % 6d  % 6d      o/s  \r\n", (int)(gx), (int)(gy), (int)(gz));
    M5.Lcd.setCursor(0, 64);
    M5.Lcd.printf("% 6d  % 6d  % 6d     mG    \r\n", (int)(mx), (int)(my), (int)(mz));

    M5.Lcd.setCursor(0, 100);
    M5.Lcd.printf("  yaw: % 5.2f    pitch: % 5.2f    roll: % 5.2f   \r\n", (yaw), (pitch), (roll));

    M5.Lcd.setCursor(12, 144);
    M5.Lcd.print("rt: ");
    M5.Lcd.print(frequency, 2);
    M5.Lcd.print(" Hz");
}