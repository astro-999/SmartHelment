#include <Wire.h>
#include <MPU6050_tockn.h>
#include <TinyGPSPlus.h>
#include <HardwareSerial.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "config.h"

// -------- OBJECTS ----------
MPU6050 mpu(Wire);
TinyGPSPlus gps;

HardwareSerial SerialGPS(1);
HardwareSerial SerialGSM(2);

BLECharacteristic *alertChar;

// -------- STATE VARIABLES ----------
String authToken       = "";
unsigned long lastMoveTime   = 0;
unsigned long lastGPSSend    = 0;
unsigned long lastLoginTime  = 0;
bool firstMove               = false;   // tracks if we have seen movement yet
bool bleConnected            = false;

// ==================================================
//  BLE
// ==================================================
class MyServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer *server)    { bleConnected = true;  Serial.println("BLE connected"); }
    void onDisconnect(BLEServer *server) { bleConnected = false; Serial.println("BLE disconnected"); }
};

void setupBLE() {
    BLEDevice::init(BLE_DEVICE_NAME);
    BLEServer  *server  = BLEDevice::createServer();
    server->setCallbacks(new MyServerCallbacks());

    BLEService *service = server->createService("1234");
    alertChar = service->createCharacteristic("5678", BLECharacteristic::PROPERTY_NOTIFY);
    alertChar->addDescriptor(new BLE2902());

    service->start();
    BLEAdvertising *adv = BLEDevice::getAdvertising();
    adv->addServiceUUID("1234");
    adv->start();
    Serial.println("BLE advertising started");
}

void sendBLE(const String &msg) {
    if (bleConnected) {
        alertChar->setValue(msg.c_str());
        alertChar->notify();
        Serial.println("BLE sent: " + msg);
    }
}

// ==================================================
//  GSM HELPERS
// ==================================================
void waitForGSMResponse(unsigned long timeout = 2000) {
    unsigned long start = millis();
    while (millis() - start < timeout) {
        while (SerialGSM.available()) {
            Serial.write(SerialGSM.read());
        }
    }
}

void sendAT(const String &cmd, unsigned long wait = 1000) {
    SerialGSM.println(cmd);
    waitForGSMResponse(wait);
}

// ==================================================
//  GSM — LOGIN
// ==================================================
bool loginToServer() {
    Serial.println("Logging in to server...");

    String body    = "{\"username\":\"" + String(API_USERNAME) + "\",\"password\":\"" + String(API_PASSWORD) + "\"}";
    int    bodyLen = body.length();

    sendAT("AT+HTTPTERM", 500);          // close any open session first
    sendAT("AT+HTTPINIT", 1000);
    sendAT("AT+HTTPPARA=\"CID\",1", 500);
    sendAT("AT+HTTPPARA=\"URL\",\"http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/auth/login/\"", 500);
    sendAT("AT+HTTPPARA=\"CONTENT\",\"application/json\"", 500);
    sendAT("AT+HTTPDATA=" + String(bodyLen) + ",5000", 1000);
    SerialGSM.print(body);
    delay(3000);
    sendAT("AT+HTTPACTION=1", 6000);
    sendAT("AT+HTTPREAD", 3000);

    // Collect full response
    String response = "";
    unsigned long t = millis();
    while (millis() - t < 3000) {
        while (SerialGSM.available()) {
            response += (char)SerialGSM.read();
        }
    }
    sendAT("AT+HTTPTERM", 500);

    Serial.println("Login response: " + response);

    // Extract access token
    int idx = response.indexOf("\"access\":\"");
    if (idx != -1) {
        idx += 10;
        int end = response.indexOf("\"", idx);
        authToken = response.substring(idx, end);
        lastLoginTime = millis();
        Serial.println("Login successful! Token length: " + String(authToken.length()));
        return true;
    }

    Serial.println("Login failed — check username/password and server IP");
    return false;
}

// ==================================================
//  GSM — SEND GPS
// ==================================================
void sendGPSToServer(float lat, float lng) {
    if (authToken.length() == 0) {
        Serial.println("No token — skipping GPS send");
        return;
    }

    Serial.println("Sending GPS to server...");
    String body    = "{\"latitude\":" + String(lat, 6) + ",\"longitude\":" + String(lng, 6) + ",\"speed\":" + String(gps.speed.kmph(), 1) + "}";
    int    bodyLen = body.length();

    sendAT("AT+HTTPTERM", 500);
    sendAT("AT+HTTPINIT", 1000);
    sendAT("AT+HTTPPARA=\"CID\",1", 500);
    sendAT("AT+HTTPPARA=\"URL\",\"http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/gps/\"", 500);
    sendAT("AT+HTTPPARA=\"CONTENT\",\"application/json\"", 500);
    sendAT("AT+HTTPPARA=\"USERDATA\",\"Authorization: Bearer " + authToken + "\"", 500);
    sendAT("AT+HTTPDATA=" + String(bodyLen) + ",5000", 1000);
    SerialGSM.print(body);
    delay(3000);
    sendAT("AT+HTTPACTION=1", 6000);
    sendAT("AT+HTTPTERM", 500);

    Serial.println("GPS sent: lat=" + String(lat, 6) + " lng=" + String(lng, 6));
}

// ==================================================
//  GSM — SEND SOS
// ==================================================
void sendSOSToServer(float lat, float lng) {
    if (authToken.length() == 0) {
        Serial.println("No token — skipping SOS send");
        return;
    }

    Serial.println("Sending SOS to server...");
    String body    = "{\"latitude\":" + String(lat, 6) + ",\"longitude\":" + String(lng, 6) + ",\"message\":\"Crash detected!\"}";
    int    bodyLen = body.length();

    sendAT("AT+HTTPTERM", 500);
    sendAT("AT+HTTPINIT", 1000);
    sendAT("AT+HTTPPARA=\"CID\",1", 500);
    sendAT("AT+HTTPPARA=\"URL\",\"http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/sos/\"", 500);
    sendAT("AT+HTTPPARA=\"CONTENT\",\"application/json\"", 500);
    sendAT("AT+HTTPPARA=\"USERDATA\",\"Authorization: Bearer " + authToken + "\"", 500);
    sendAT("AT+HTTPDATA=" + String(bodyLen) + ",5000", 1000);
    SerialGSM.print(body);
    delay(3000);
    sendAT("AT+HTTPACTION=1", 6000);
    sendAT("AT+HTTPTERM", 500);

    Serial.println("SOS sent!");
}

// ==================================================
//  GSM — SEND SMS
// ==================================================
void sendSMS(const String &text) {
    Serial.println("Sending SMS...");
    sendAT("AT+CMGF=1", 500);
    SerialGSM.print("AT+CMGS=\"");
    SerialGSM.print(EMERGENCY_NUMBER);
    SerialGSM.println("\"");
    delay(500);
    SerialGSM.print(text);
    SerialGSM.write(26);   // CTRL+Z to send
    delay(3000);
    Serial.println("SMS sent to " + String(EMERGENCY_NUMBER));
}

// ==================================================
//  GPS HELPERS
// ==================================================
void readGPS() {
    while (SerialGPS.available()) {
        gps.encode(SerialGPS.read());
    }
}

String getGoogleMapsLink() {
    if (gps.location.isValid()) {
        return "https://maps.google.com/?q=" +
               String(gps.location.lat(), 6) + "," +
               String(gps.location.lng(), 6);
    }
    return "GPS not ready";
}

// ==================================================
//  FALL DETECTION (fixed)
// ==================================================
bool detectFall() {
    mpu.update();

    float ax = abs(mpu.getAccX());
    float ay = abs(mpu.getAccY());
    float az = abs(mpu.getAccZ());

    // Impact detected
    if (ax > FALL_THRESHOLD || ay > FALL_THRESHOLD || az > FALL_THRESHOLD) {
        lastMoveTime = millis();
        firstMove    = true;
        Serial.println("Impact detected! ax=" + String(ax) + " ay=" + String(ay) + " az=" + String(az));
        return true;
    }

    // No movement after impact for NO_MOVE_TIME_MS = possible unconscious rider
    if (firstMove && (millis() - lastMoveTime > NO_MOVE_TIME_MS)) {
        firstMove = false;   // reset so it doesn't keep firing
        Serial.println("No movement detected after impact — possible fall!");
        return true;
    }

    return false;
}

// ==================================================
//  SETUP
// ==================================================
void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\n=== SmartHelmetX Booting ===");

    // GPIO
    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(CANCEL_BTN, INPUT_PULLUP);
    digitalWrite(BUZZER_PIN, LOW);

    // I2C + MPU6050
    Wire.begin(MPU_SDA, MPU_SCL);
    mpu.begin();
    mpu.calcGyroOffsets(true);
    Serial.println("MPU6050 ready");

    // GPS (UART1)
    SerialGPS.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
    Serial.println("GPS UART started");

    // GSM (UART2)
    SerialGSM.begin(9600, SERIAL_8N1, GSM_RX, GSM_TX);
    Serial.println("GSM UART started");

    // BLE
    setupBLE();

    // Wait for GSM to register on network
    Serial.println("Waiting for GSM network...");
    delay(5000);
    sendAT("AT", 1000);           // check GSM alive
    sendAT("AT+CREG?", 1000);     // check network registration
    sendAT("AT+SAPBR=3,1,\"Contype\",\"GPRS\"", 500);
    sendAT("AT+SAPBR=3,1,\"APN\",\"internet\"", 500);  // change APN if needed
    sendAT("AT+SAPBR=1,1", 3000);  // open GPRS bearer

    // Login to Django server
    loginToServer();

    Serial.println("=== SmartHelmetX Ready ===");
}

// ==================================================
//  LOOP
// ==================================================
void loop() {
    // Always read GPS in background
    readGPS();

    // Re-login every 11 hours (token refresh)
    if (millis() - lastLoginTime > LOGIN_INTERVAL_MS) {
        loginToServer();
    }

    // Send GPS to server every 30 seconds
    if (millis() - lastGPSSend > GPS_SEND_INTERVAL_MS) {
        if (gps.location.isValid()) {
            sendGPSToServer(gps.location.lat(), gps.location.lng());
        } else {
            Serial.println("GPS not valid yet — skipping send");
        }
        lastGPSSend = millis();
    }

    // Fall / crash detection
    if (detectFall()) {
        // Alert rider immediately
        digitalWrite(BUZZER_PIN, HIGH);
        sendBLE("ALERT: Possible Accident! Press cancel button within 10 seconds.");
        Serial.println("Fall detected — waiting 10s for cancel...");

        // 10 second cancel window — keep reading GPS during wait
        unsigned long waitStart = millis();
        while (millis() - waitStart < 10000) {
            readGPS();
            delay(100);
        }

        // Check if rider pressed cancel button
        // INPUT_PULLUP: HIGH = not pressed = no cancel = send alerts
        if (digitalRead(CANCEL_BTN) == HIGH) {
            Serial.println("No cancel — sending SOS!");

            float lat = gps.location.isValid() ? gps.location.lat() : 0.0;
            float lng = gps.location.isValid() ? gps.location.lng() : 0.0;

            // 1. Send SOS to Django server
            sendSOSToServer(lat, lng);

            // 2. Wait for HTTP to close before SMS
            delay(2000);

            // 3. Send SMS to emergency contact
            String link = getGoogleMapsLink();
            String msg  = "ACCIDENT ALERT! SmartHelmetX detected a crash.\nLocation: " + link;
            sendSMS(msg);

            // 4. Notify via BLE
            sendBLE(msg);

            Serial.println("All alerts sent!");
        } else {
            Serial.println("Cancel button pressed — alert cancelled");
            sendBLE("Alert cancelled by rider.");
        }

        digitalWrite(BUZZER_PIN, LOW);
    }

    delay(100);
}
