#include "IMU.h"

#include <M5Stack.h>
#include "utility/MPU9250.h"
#include "utility/quaternionFilters.h"

IMU::IMU()
{
    mpu9250 = new MPU9250();

    address = mpu9250->readByte(MPU9250_ADDRESS, WHO_AM_I_MPU9250);
    mpu9250->MPU9250SelfTest(mpu9250->SelfTest);
    mpu9250->calibrateMPU9250(mpu9250->gyroBias, mpu9250->accelBias);
    mpu9250->initMPU9250();

    ak8963Address = mpu9250->readByte(AK8963_ADDRESS, WHO_AM_I_AK8963);
    mpu9250->initAK8963(mpu9250->magCalibration);
}

IMU::~IMU()
{
    delete mpu9250;
}

void IMU::read(float* ax, float* ay, float* az,
    float* gx, float* gy, float* gz,
    float* mx, float* my, float* mz,
    float* yaw, float* pitch, float* roll)
{
    if (mpu9250->readByte(MPU9250_ADDRESS, INT_STATUS) & 0x01)
    {
        readAccel();
        readGyro();
        readMag();
    }
    updateFilter();

    *ax = mpu9250->ax;
    *ay = mpu9250->ay;
    *az = mpu9250->az;
    *gx = mpu9250->gx;
    *gy = mpu9250->gy;
    *gz = mpu9250->gz;
    *mx = mpu9250->mx;
    *my = mpu9250->my;
    *mz = mpu9250->mz;
    *yaw = mpu9250->yaw;
    *pitch = mpu9250->pitch;
    *roll = mpu9250->roll;
}

float IMU::getFrequency()
{
    return (float)mpu9250->sumCount / mpu9250->sum;
}
unsigned char IMU::getAddress() {
    return address;
}
unsigned char IMU::getAK8963Adress() {
    return ak8963Address;
}

float* IMU::getAccelBias() {
    return mpu9250->accelBias;
}

float* IMU::getGyroBias() {
    return mpu9250->gyroBias;
}

float* IMU::getMagCalibration() {
    return mpu9250->magCalibration;
}

void IMU::readAccel()
{
    mpu9250->readAccelData(mpu9250->accelCount); // Read the x/y/z adc values
    mpu9250->getAres();

    // Now we'll calculate the accleration value into actual g's
    // This depends on scale being set
    mpu9250->ax = (float)mpu9250->accelCount[0] * mpu9250->aRes;
    mpu9250->ay = (float)mpu9250->accelCount[1] * mpu9250->aRes;
    mpu9250->az = (float)mpu9250->accelCount[2] * mpu9250->aRes;
}

void IMU::readGyro()
{
    mpu9250->readGyroData(mpu9250->gyroCount); // Read the x/y/z adc values
    mpu9250->getGres();

    // Calculate the gyro value into actual degrees per second
    // This depends on scale being set
    mpu9250->gx = (float)mpu9250->gyroCount[0] * mpu9250->gRes;
    mpu9250->gy = (float)mpu9250->gyroCount[1] * mpu9250->gRes;
    mpu9250->gz = (float)mpu9250->gyroCount[2] * mpu9250->gRes;
}

void IMU::readMag()
{
    mpu9250->readMagData(mpu9250->magCount); // Read the x/y/z adc values
    mpu9250->getMres();
    // User environmental x-axis correction in milliGauss, should be
    // automatically calculated
    mpu9250->magbias[0] = +470.;
    // User environmental x-axis correction in milliGauss TODO axis??
    mpu9250->magbias[1] = +120.;
    // User environmental x-axis correction in milliGauss
    mpu9250->magbias[2] = +125.;

    // Calculate the magnetometer values in milliGauss
    // Include factory calibration per data sheet and user environmental
    // corrections
    // Get actual magnetometer value, this depends on scale being set
    mpu9250->mx = (float)mpu9250->magCount[0] * mpu9250->mRes * mpu9250->magCalibration[0] -
                  mpu9250->magbias[0];
    mpu9250->my = (float)mpu9250->magCount[1] * mpu9250->mRes * mpu9250->magCalibration[1] -
                  mpu9250->magbias[1];
    mpu9250->mz = (float)mpu9250->magCount[2] * mpu9250->mRes * mpu9250->magCalibration[2] -
                  mpu9250->magbias[2];
}

void IMU::updateFilter()
{
    mpu9250->updateTime();
    MahonyQuaternionUpdate(mpu9250->ax, mpu9250->ay, mpu9250->az,
                           mpu9250->gx * DEG_TO_RAD, mpu9250->gy * DEG_TO_RAD, mpu9250->gz * DEG_TO_RAD,
                           mpu9250->my, mpu9250->mx, mpu9250->mz,
                           mpu9250->deltat);

    mpu9250->delt_t = millis() - mpu9250->count;
    if (mpu9250->delt_t > 100)
    {
        mpu9250->yaw = atan2(2.0f * (*(getQ() + 1) * *(getQ() + 2) + *getQ() *
                                                                         *(getQ() + 3)),
                             *getQ() * *getQ() + *(getQ() + 1) * *(getQ() + 1) - *(getQ() + 2) * *(getQ() + 2) - *(getQ() + 3) * *(getQ() + 3));
        mpu9250->pitch = -asin(2.0f * (*(getQ() + 1) * *(getQ() + 3) - *getQ() *
                                                                           *(getQ() + 2)));
        mpu9250->roll = atan2(2.0f * (*getQ() * *(getQ() + 1) + *(getQ() + 2) *
                                                                    *(getQ() + 3)),
                              *getQ() * *getQ() - *(getQ() + 1) * *(getQ() + 1) - *(getQ() + 2) * *(getQ() + 2) + *(getQ() + 3) * *(getQ() + 3));
        mpu9250->pitch *= RAD_TO_DEG;
        mpu9250->yaw *= RAD_TO_DEG;
        // Declination of SparkFun Electronics (40°05'26.6"N 105°11'05.9"W) is
        //   8° 30' E  ± 0° 21' (or 8.5°) on 2016-07-19
        // - http://www.ngdc.noaa.gov/geomag-web/#declination
        mpu9250->yaw -= 8.5;
        mpu9250->roll *= RAD_TO_DEG;

        mpu9250->count = millis();
        mpu9250->sumCount = 0;
        mpu9250->sum = 0;
    }
}
