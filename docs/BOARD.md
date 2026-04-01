# Board-Dokumentation: Waveshare ESP32-S3-LCD-1.85

**Quelle:** https://www.waveshare.com/wiki/ESP32-S3-LCD-1.85

---

## Übersicht

| Eigenschaft | Wert |
|-------------|------|
| MCU | ESP32-S3R8 (Dual-Core LX7) |
| Taktrate | bis 240 MHz |
| SRAM | 512 KB intern |
| PSRAM | 8 MB (OPI/Octal) |
| Flash | 16 MB |
| Display | 1.85" rund, 360×360px, 262K Farben |
| Display-Controller | ST7701 (SPI-Interface) |
| WiFi | 802.11 b/g/n (2.4GHz) |
| Bluetooth | BLE 5.0 |
| Antenna | Onboard Keramik-Antenne + IPEX-Anschluss |

---

## Onboard-Ressourcen

| Nr | Komponente | Beschreibung |
|----|------------|-------------|
| 1 | ESP32-S3R8 | Hauptprozessor |
| 2 | 16MB Flash | NOR Flash Speicher |
| 3 | QMI8658 | 6-Achsen IMU (Gyro + Accel) |
| 4 | TCA9554PWR | GPIO-Expander (I2C) |
| 5 | PCM5101 | Audio-DAC |
| 6 | Power Amplifier | Lautsprecher-Verstärker |
| 7 | Battery Manager | Lade-IC |
| 8 | ME6217C33M5G | LDO 3.3V, 800mA |
| 9 | PCF85063 | RTC Echtzeituhr |
| 10 | Keramik-Antenne | 2.4GHz onboard |
| 11 | IPEX Gen1 | Externer Antennen-Anschluss |
| 12 | TF-Slot | MicroSD-Karte |
| 13 | Speaker-Anschluss | 8Ω 2W, 2030er Lautsprecher |
| 14 | Volume-Button | Lautstärke-Taste |
| 15 | Mikrofon | Onboard MIC |
| 16 | UART Interface | Nur wenn UART USB nicht belegt |
| 17 | Power-LED | Betriebsanzeige |
| 18 | USB Type-C | Daten + Stromversorgung |
| 19 | RTC-Batterie | CR2032 Halter |
| 20 | Lade-LED | Batterie-Ladeanzeige |
| 21 | I2C Interface | Interne Chips |
| 22 | Reset-Taste | Hardware-Reset |
| 23 | Boot-Taste | Download-Mode |
| 24 | Batterie-Anschluss | MX1.25 2-Pin, 3.7V LiPo |
| 25 | Power-Button | Batterie-Versorgung ein/aus |

---

## Interne Hardware-Verbindungen

```
ESP32-S3R8
├── SPI Bus 1 (LCD + TF)
│   ├── LCD ST7701  (CS: GPIO12, DC: GPIO4, RST: GPIO5, BL: GPIO38)
│   └── TF-Card     (CS: GPIO15)
│
├── I2C Bus (SDA: GPIO6, SCL: GPIO7)
│   ├── QMI8658  (IMU, Addr: 0x6B)
│   ├── PCF85063 (RTC, Addr: 0x51)
│   └── TCA9554  (GPIO-Expander, Addr: 0x20)
│
├── I2S (Audio)
│   ├── PCM5101  (BCLK: GPIO17, LRCLK: GPIO18, DATA: GPIO16)
│   └── MIC I2S  (BCLK: GPIO39, WS: GPIO40, DATA: GPIO41)
│
└── Buttons
    ├── BOOT (GPIO0)
    └── POWER (GPIO21)
```

---

## Versionen

| Modell | Touch | Beschreibung |
|--------|-------|-------------|
| ESP32-S3-LCD-1.85 | ❌ | Ohne Touch |
| ESP32-S3-Touch-LCD-1.85 | ✅ | Mit kapazitivem Touch (I2C) |

---

## Ressourcen

- **Wiki:** https://www.waveshare.com/wiki/ESP32-S3-LCD-1.85
- **Schaltplan:** Download auf Wiki-Seite
- **Demo-Code (Arduino/ESP-IDF):** Download auf Wiki-Seite
- **MicroPython:** https://micropython.org/download/ESP32_GENERIC_S3/
