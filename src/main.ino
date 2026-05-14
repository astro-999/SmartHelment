#include <Wire.h>
#include <MPU6050_tockn.h>
#include <TinyGPSPlus.h>
#include <HardwareSerial.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "config.h"

MPU6050 mpu(Wire);
TinyGPSPlus gps;

HardwareSerial SerialGPS(1);
HardwareSerial SerialGSM(2);

BLECharacteristic *alertChar;
unsigned long lastMoveTime = 0;

// -------- BLE SETUP ----------
void setupBLE()
{
    BLEDevice::init("SmartHelmetX");
    BLEServer *server = BLEDevice::createServer();
    BLEService *service = server->createService("1234");

    alertChar = service->createCharacteristic(
        "5678",
        BLECharacteristic::PROPERTY_NOTIFY);
    alertChar->addDescriptor(new BLE2902());

    service->start();
    BLEAdvertising *adv = BLEDevice::getAdvertising();
    adv->addServiceUUID("1234");
    adv->start();
}

void sendBLE(String msg)
{
    alertChar->setValue(msg.c_str());
    alertChar->notify();
}

// -------- GSM SMS ----------
void sendSMS(String text)
{
    SerialGSM.println("AT+CMGF=1");
    delay(500);
    SerialGSM.print("AT+CMGS=\"");
    SerialGSM.print(EMERGENCY_NUMBER);
    SerialGSM.println("\"");
    delay(500);
    SerialGSM.print(text);
    SerialGSM.write(26); // CTRL+Z
    delay(2000);
}

// -------- GET GPS LINK ----------
String getGoogleMapsLink()
{
    while (SerialGPS.available())
    {
        gps.encode(SerialGPS.read());
    }

    if (gps.location.isValid())
    {
        String link = "https://maps.google.com/?q=";
        link += String(gps.location.lat(), 6);
        link += ",";
        link += String(gps.location.lng(), 6);
        return link;
    }
    return "GPS not ready";
}

// -------- FALL DETECTION ----------
bool detectFall()
{
    mpu.update();

    float ax = abs(mpu.getAccX());
    float ay = abs(mpu.getAccY());
    float az = abs(mpu.getAccZ());

    if (ax > FALL_THRESHOLD || ay > FALL_THRESHOLD || az > FALL_THRESHOLD)
    {
        lastMoveTime = millis();
        return true;
    }

    if (millis() - lastMoveTime > NO_MOVE_TIME_MS)
    {
        return true;
    }
    return false;
}

// -------- SETUP ----------
void setup()
{
    Serial.begin(115200);

    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(CANCEL_BTN, INPUT_PULLUP);

    // IMU
    Wire.begin(MPU_SDA, MPU_SCL);
    mpu.begin();
    mpu.calcGyroOffsets(true);

    // GPS & GSM
    SerialGPS.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
    SerialGSM.begin(9600, SERIAL_8N1, GSM_RX, GSM_TX);

    // BLE
    setupBLE();

    Serial.println("SmartHelmetX Ready with GPS + SMS");
}

// -------- LOOP ----------
void loop()
{

    if (detectFall())
    {

        digitalWrite(BUZZER_PIN, HIGH);
        sendBLE("ALERT: Possible Accident!");

        // Wait 10 sec before SMS (rider can cancel)
        delay(10000);

        if (digitalRead(CANCEL_BTN) == HIGH)
        {
            String link = getGoogleMapsLink();
            String msg = "Accident detected! Location: " + link;

            sendSMS(msg);
            sendBLE(msg);
        }

        digitalWrite(BUZZER_PIN, LOW);
    }

    delay(100);
}
