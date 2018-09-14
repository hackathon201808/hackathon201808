#include <M5Stack.h>
#include <driver/dac.h>

#define SerialDebug false // Set to true to get Serial output for debugging
#define LCD
#define sendByBT true
#define PIN_N 10
uint8_t pinlist[PIN_N] = {21, 22, 23, 19, 18, 16, 17, 2, 5, 25};
uint8_t pinResultlist[PIN_N] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
uint32_t last_displayed;
uint8_t btnAPressed = 0;
uint8_t btnBPressed = 0;
uint8_t btnCPressed = 0;

// for beep
uint32_t beep_last_time = 0;
uint8_t beep_volume = 2; //min 1, max 255
uint32_t beep_total_time = 0;

void setup()
{
    M5.begin();
    Wire.begin();

    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.fillScreen(BLACK);

    pinMode(21, INPUT_PULLUP);
    pinMode(22, INPUT_PULLUP);
    pinMode(23, INPUT_PULLUP);
    pinMode(19, INPUT_PULLUP);
    pinMode(18, INPUT_PULLUP);
    pinMode(16, INPUT_PULLUP);
    pinMode(17, INPUT_PULLUP);
    pinMode(2, INPUT_PULLUP);
    pinMode(5, INPUT_PULLUP);
    pinMode(25, INPUT_PULLUP);

    beep_total_time = millis();

    //これを実行すると、M5Stackスピーカーから破裂音が出る
    dac_output_enable(DAC_CHANNEL_1); //DAC channel 1 is GPIO #25
}

void beep()
{
    if (millis() - beep_total_time < 10000)
    { //10秒後にbeep音停止
        uint32_t b_period = millis() - beep_last_time;
        if (b_period < 500)
        {
            dac_output_voltage(DAC_CHANNEL_1, 0);
            delay(1); //約500Hz
            //delayMicroseconds(500); //約1kHz
            dac_output_voltage(DAC_CHANNEL_1, beep_volume);
            delay(1); //約500Hz
                      //delayMicroseconds(500); //約1kHz
        }
        else if (b_period >= 500 && b_period < 1000)
        {
            dac_output_voltage(DAC_CHANNEL_1, 0);
        }
        else
        {
            beep_last_time = millis();
        }
    }
    else
    {
        //これを実行するとGPIO #25のDAC outputが無効になり、スピーカーからノイズが出なくなる。
        //ただし、次にdac_output_enableを実行する時に破裂音が出る。
        dac_output_disable(DAC_CHANNEL_1);
        delay(10000); //10秒無音状態
        beep_total_time = millis();

        //beep音を鳴らす為にはこれが必要。ただし破裂音が出る。
        dac_output_enable(DAC_CHANNEL_1);
    }
}

void flush()
{
    for (int i = 0; i < 4; ++i) {
        if (i % 2 == 0) {
            M5.Lcd.fillScreen(BLACK);
        } else {
            M5.Lcd.fillScreen(YELLOW);
        }
        delay(100);
    }
    M5.Lcd.fillScreen(BLACK);
}

void loop()
{

    if (M5.BtnA.wasPressed())
    {
        btnAPressed++;
    }
    if (M5.BtnB.wasPressed())
    {
        btnBPressed++;
    }
    if (M5.BtnC.wasPressed())
    {
        btnCPressed++;
    }

    uint32_t now = millis();
    if (now - last_displayed > 200)
    {
        bool changed = false;
        // M5.Lcd.drawNumber(now, 190, 0, 2);
        uint8_t input = 0;
        for (uint8_t i = 0; i < PIN_N; i++)
        {
            // M5.Lcd.drawString("number :", 0, i * 15, 2);
            long pinResult = digitalRead(pinlist[i]);
            if (pinResult != pinResultlist[i])
            {
                changed = true;
            }
            pinResultlist[i] = pinResult;
            // M5.Lcd.drawNumber(pinResult, 100, i * 15, 2);
        }
        // M5.Lcd.drawString("BtnA :", 0, 170, 2);
        // M5.Lcd.drawNumber(btnAPressed, 40, 170, 2);
        // M5.Lcd.drawString("BtnB :", 60, 170, 2);
        // M5.Lcd.drawNumber(btnBPressed, 100, 170, 2);
        // M5.Lcd.drawString("BtnC :", 120, 170, 2);
        // M5.Lcd.drawNumber(btnCPressed, 160, 170, 2);
        last_displayed = now;

        if (changed)
        {
            // TODO: beepの実行はよく検証できていない。多分変な音が出る。
            // beep();
            flush();
        }
    }

    M5.update();
}