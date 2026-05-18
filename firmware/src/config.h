#ifndef CONFIG_H
#define CONFIG_H

// ---------- PIN CONFIGURATION (ESP32) ----------
#define GPS_RX   16
#define GPS_TX   17

#define MPU_SDA  21
#define MPU_SCL  22

#define BUZZER_PIN  5
#define CANCEL_BTN  4

// ---------- FALL DETECTION THRESHOLDS ----------
#define FALL_THRESHOLD  1.8      // g-force threshold
#define NO_MOVE_TIME_MS 8000     // 8 seconds

// ---------- BLE CONFIG ----------
#define BLE_DEVICE_NAME "SmartHelmetX"

// ---------- EMERGENCY CONTACT (edit later) ----------
#define EMERGENCY_NUMBER "+97798XXXXXXXX"

#endif
