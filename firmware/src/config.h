#ifndef CONFIG_H
#define CONFIG_H

// ---------- PIN CONFIGURATION (ESP32) ----------
#define GPS_RX      16
#define GPS_TX      17

#define GSM_RX      26
#define GSM_TX      27

#define MPU_SDA     21
#define MPU_SCL     22

#define BUZZER_PIN  5
#define CANCEL_BTN  4

// ---------- FALL DETECTION THRESHOLDS ----------
#define FALL_THRESHOLD    1.8f     // g-force threshold
#define NO_MOVE_TIME_MS   8000     // 8 seconds of no movement after impact

// ---------- BLE CONFIG ----------
#define BLE_DEVICE_NAME   "SmartHelmetX"

// ---------- EMERGENCY CONTACT ----------
#define EMERGENCY_NUMBER  "+97798XXXXXXXX"   // edit this

// ---------- SERVER CONFIG ----------
#define SERVER_IP         "192.168.1.X"      // run ipconfig and put your IPv4 here
#define SERVER_PORT       "8000"
#define API_USERNAME      "your_username"    // your Django login username
#define API_PASSWORD      "your_password"    // your Django login password

// ---------- TIMING ----------
#define GPS_SEND_INTERVAL_MS    30000UL      // send GPS every 30 seconds
#define LOGIN_INTERVAL_MS       39600000UL   // re-login every 11 hours

#endif