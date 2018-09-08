#ifndef LOG_UTIL_H
#define LOG_UTIL_H

#include <string>

void displayWelcome();

void displayAdress(std::string name, unsigned char address, unsigned char expected);

void displayAccelGyroBias(float* accelBias, float* gyroBias);

void displayMagCalibration(float* magCalibration);

void displayIMU(float ax, float ay, float az,
                float gx, float gy, float gz,
                float mx, float my, float mz,
                float yaw, float pitch, float roll,
                float frequency);

#endif