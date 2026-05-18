# SmartHelmetX Firmware

ESP32-based firmware for the smart helmet hardware module.

## Hardware Components

| Component   | Model        | Purpose                          | Pins (ESP32)   |
|-------------|--------------|----------------------------------|----------------|
| IMU         | MPU6050      | Accelerometer + Gyroscope        | SDA=21, SCL=22 |
| GPS         | NEO-6M       | Location tracking                | RX=16, TX=17   |
| GSM         | SIM800L      | SMS emergency notifications      | RX/TX via UART2|
| Buzzer      | Passive      | Alert buzzer                     | GPIO 5         |
| Button      | Push button  | Cancel false alerts              | GPIO 4         |
| MCU         | ESP32        | Main controller + BLE            | —              |

## Wiring Diagram

```
ESP32 GPIO 21 ──► MPU6050 SDA
ESP32 GPIO 22 ──► MPU6050 SCL
ESP32 GPIO 16 ──► GPS RX
ESP32 GPIO 17 ──► GPS TX
ESP32 GPIO  5 ──► Buzzer (+)
ESP32 GPIO  4 ──► Cancel Button
```

## Libraries Required

Install via Arduino Library Manager:
- `MPU6050_tockn` — IMU driver
- `TinyGPSPlus` — GPS NMEA parser
- ESP32 BLE (built-in)

## Configuration

Edit `src/config.h` to customize:
- Pin assignments
- Fall detection threshold (default: 1.8g)
- No-movement timeout (default: 8 seconds)
- Emergency phone number

## Flashing

1. Open `src/main.ino` in Arduino IDE
2. Select Board: **ESP32 Dev Module**
3. Set the correct COM port
4. Upload
