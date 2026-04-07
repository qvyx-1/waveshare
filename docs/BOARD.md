# Board-Dokumentation: Waveshare ESP32-S3-LCD-1.85

**Quelle:** https://www.waveshare.com/wiki/ESP32-S3-LCD-1.85

---

## Übersicht

| Eigenschaft | Wert |
|-------------|------|
| MCU | ESP32-S3R8 (Dual-Core LX7, Xtensa 32-bit) |
| Taktrate | bis 240 MHz |
| SRAM | 512 KB intern |
| PSRAM | 8 MB (Octal SPI) |
| Flash | 16 MB |
| Display | 1.85" rund, 360×360px, 262K Farben, IPS |
| Display-Controller | **ST77916** (QSPI-Schnittstelle) |
| Touch | CST816S kapazitiv (nur Touch-Variante) |
| WiFi | 802.11 b/g/n (2.4GHz) |
| Bluetooth | BLE 5.0 |
| Antenna | Onboard Keramik-Antenne + IPEX-Anschluss |

---

## Onboard-Ressourcen

| Nr | Komponente | Beschreibung |
|----|------------|--------------|
| 1 | ESP32-S3R8 | Hauptprozessor, KI-Vektorbefehle |
| 2 | 16MB Flash | NOR Flash Speicher |
| 3 | 8MB PSRAM | Octal SPI, für Framebuffer |
| 4 | QMI8658 | 6-Achsen IMU (Gyro + Accel) |
| 5 | TCA9554PWR | GPIO-Expander (I2C, 0x20) |
| 6 | PCM5101 | Audio-DAC (I2S) |
| 7 | Power Amplifier | Lautsprecher-Verstärker (via EXIO1) |
| 8 | PCF85063 | RTC Echtzeituhr (I2C, 0x51) |
| 9 | CST816S | Touch-Controller (separater I2C Bus) |
| 10 | TF-Slot | MicroSD-Karte |
| 11 | Speaker-Anschluss | 8Ω 2W, 2030er Lautsprecher |
| 12 | Mikrofon | Onboard MIC (I2S) |

---

## Interne Hardware-Verbindungen

```
ESP32-S3R8 (240MHz, 8MB PSRAM)
│
├── QSPI Display (ST77916, 360×360)
│   ├── SDA0: GPIO46  (nur D0 im 1-wire Modus genutzt)
│   ├── SDA1: GPIO45
│   ├── SDA2: GPIO42
│   ├── SDA3: GPIO41
│   ├── SCK:  GPIO40
│   ├── CS:   GPIO21
│   ├── BL:   GPIO5   (PWM Backlight)
│   ├── RST:  EXIO2   (via TCA9554!)
│   └── TE:   GPIO18  (Tearing Effect)
│
├── I2C Bus 0 (SDA: GPIO11, SCL: GPIO10)
│   ├── TCA9554  (GPIO-Expander, 0x20)
│   │   ├── EXIO0: (reserviert)
│   │   ├── EXIO1: Audio PA Enable
│   │   ├── EXIO2: LCD Reset
│   │   ├── EXIO3: SD Card CS
│   │   ├── EXIO4: IMU INT2
│   │   └── EXIO5: IMU INT1
│   ├── QMI8658  (IMU, 0x6B)
│   └── PCF85063 (RTC, 0x51)
│
├── I2C Bus 1 (SDA: GPIO1, SCL: GPIO3) — NUR Touch!
│   └── CST816S  (Touch, 0x15, INT: GPIO4)
│
├── I2S Audio Output
│   └── PCM5101  (BCK: GPIO48, LRCK: GPIO38, DIN: GPIO47)
│
├── I2S Mikrofon Input
│   └── MIC      (SCK: GPIO15, WS: GPIO2, SD: GPIO39)
│
├── SPI SD-Karte
│   └── TF-Card  (MISO: GPIO16, MOSI: GPIO17, SCK: GPIO14, CS: EXIO3)
│
└── Buttons
    └── BOOT (GPIO0)
```

---

## Versionen

| Modell | Touch | Beschreibung |
|--------|-------|--------------|
| ESP32-S3-LCD-1.85 | ❌ | Ohne Touch |
| ESP32-S3-Touch-LCD-1.85 | ✅ | Mit kapazitivem Touch CST816S |
| ESP32-S3-Touch-LCD-1.85C | ✅ | Neuere Revision mit Touch |

---

## MicroPython Firmware

- **Empfohlen:** `ESP32_GENERIC_S3-SPIRAM_OCT` (nutzt 8MB PSRAM Octal)
- **Download:** https://micropython.org/download/ESP32_GENERIC_S3/
- **Version:** ≥ 1.23.0

---

## Ressourcen

- **Wiki:** https://www.waveshare.com/wiki/ESP32-S3-LCD-1.85
- **Schaltplan:** Download auf Wiki-Seite
- **Demo-Code (Arduino/ESP-IDF):** Download auf Wiki-Seite
- **MicroPython:** https://micropython.org/download/ESP32_GENERIC_S3/
