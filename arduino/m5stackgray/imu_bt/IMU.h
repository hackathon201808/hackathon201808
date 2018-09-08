#ifndef IMU_H
#define IMU_H

class MPU9250;

class IMU
{
  public:
    IMU();
    ~IMU();

  public:
    void read(float *ax, float *ay, float *az,
              float *gx, float *gy, float *gz,
              float *mx, float *my, float *mz,
              float *yaw, float *pitch, float *roll);
    unsigned char getAddress();
    unsigned char getAK8963Adress();
    float getFrequency();
    float* getAccelBias();
    float* getGyroBias();
    float* getMagCalibration();

  private:
    unsigned char address;
    unsigned char ak8963Address;
    MPU9250 *mpu9250;

  private:
    void readAccel();
    void readGyro();
    void readMag();
    void updateFilter();
};

#endif