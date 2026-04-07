# Pin-Belegung — Waveshare ESP32-S3-LCD-1.85

> **Verifiziert** gegen offizielle Waveshare Wiki + funktionierenden Code.
> Letzte Aktualisierung: 2026-04-02

---

## Display (ST77916 — QSPI, 4 Datenleitungen)

| Signal   | GPIO   | Richtung | Beschreibung |
|----------|--------|----------|--------------|
| LCD_SDA0 | GPIO46 | OUT      | QSPI Datenleitung 0 (MOSI) |
| LCD_SDA1 | GPIO45 | OUT      | QSPI Datenleitung 1 |
| LCD_SDA2 | GPIO42 | OUT      | QSPI Datenleitung 2 |
| LCD_SDA3 | GPIO41 | OUT      | QSPI Datenleitung 3 |
| LCD_SCK  | GPIO40 | OUT      | QSPI Clock |
| LCD_CS   | GPIO21 | OUT      | Chip Select (aktiv LOW) |
| LCD_BL   | GPIO5  | OUT      | Backlight (PWM-fähig) |
| LCD_RST  | EXIO2  | OUT      | Reset via TCA9554 GPIO-Expander! |
| LCD_TE   | GPIO18 | IN       | Tearing Effect Signal |

> **Wichtig:** Obwohl das Board ein QSPI-Interface hat, nutzen wir im MicroPython-Treiber
> den 1-wire SPI Modus (nur D0/SDA0 als MOSI). Das QSPI-Kommandoformat (0x02 Prefix)
> wird beibehalten, aber Daten werden seriell über D0 übertragen.

---

## I2C Bus 0 (IMU + RTC + TCA9554)

| Funktion | GPIO   | Beschreibung |
|----------|--------|--------------|
| I2C_SDA  | GPIO11 | I2C Data     |
| I2C_SCL  | GPIO10 | I2C Clock    |

### Geräte auf I2C Bus 0

| Chip       | Adresse | Funktion |
|------------|---------|----------|
| TCA9554PWR | 0x20    | GPIO-Expander (EXIO0..EXIO7) |
| QMI8658    | 0x6B    | 6-Achsen IMU (Accel + Gyro) |
| PCF85063   | 0x51    | Echtzeituhr (RTC) |

---

## GPIO-Expander TCA9554 (I2C 0x20)

| EXIO-Pin | Bit | Funktion |
|----------|-----|----------|
| EXIO0    | 0   | (Reserviert) |
| EXIO1    | 1   | Audio PA Enable (Verstärker) |
| EXIO2    | 2   | LCD_RST (Display Reset) |
| EXIO3    | 3   | SD_CS (TF-Card Chip Select) |
| EXIO4    | 4   | IMU_INT2 |
| EXIO5    | 5   | IMU_INT1 |

> **Kritisch:** Ohne Initialisierung des TCA9554 bleibt das Display im
> Reset-Zustand (EXIO2 LOW) → schwarzer Bildschirm!

---

## Touch: CST816S (I2C Bus 1 — separater Bus!)

| Funktion  | GPIO  | Beschreibung |
|-----------|-------|--------------|
| TOUCH_SDA | GPIO1 | I2C Data (separater Bus!) |
| TOUCH_SCL | GPIO3 | I2C Clock (separater Bus!) |
| TOUCH_INT | GPIO4 | Interrupt (aktiv LOW) |
| TOUCH_RST | EXIO0 | Reset via TCA9554 |

> **Achtung:** Der Touch-Controller nutzt einen **eigenen I2C-Bus** (Bus 1),
> nicht den gleichen wie IMU/RTC. I2C-Adresse: 0x15

---

## IMU: QMI8658 (I2C Bus 0)

| Funktion | GPIO/Addr | Beschreibung |
|----------|-----------|--------------|
| SDA      | GPIO11    | Shared I2C Bus |
| SCL      | GPIO10    | Shared I2C Bus |
| Adresse  | 0x6B      | (CS=High) |
| INT1     | EXIO5     | Interrupt 1 via TCA9554 |
| INT2     | EXIO4     | Interrupt 2 via TCA9554 |

---

## RTC: PCF85063 (I2C Bus 0)

| Funktion | GPIO/Addr | Beschreibung |
|----------|-----------|--------------|
| SDA      | GPIO11    | Shared I2C Bus |
| SCL      | GPIO10    | Shared I2C Bus |
| Adresse  | 0x51      | |
| INT      | GPIO9     | Alarm Interrupt |

---

## Audio: PCM5101 DAC (I2S)

| Signal    | GPIO   | Beschreibung |
|-----------|--------|--------------|
| SPEAK_BCK | GPIO48 | I2S Bit Clock |
| SPEAK_LRCK| GPIO38 | I2S Word Select / LR Clock |
| SPEAK_DIN | GPIO47 | I2S Data In (zum DAC) |

> **Verstärker:** Wird über TCA9554 EXIO1 aktiviert (HIGH = ein).

---

## Mikrofon (I2S Input)

| Signal  | GPIO   | Beschreibung |
|---------|--------|--------------|
| MIC_WS  | GPIO2  | Word Select |
| MIC_SCK | GPIO15 | Bit Clock |
| MIC_SD  | GPIO39 | Data |

---

## TF-Karte / MicroSD (SPI)

| Signal  | GPIO  | Beschreibung |
|---------|-------|--------------|
| SD_MISO | GPIO16| SD Data Out |
| SD_MOSI | GPIO17| SD Data In / CMD |
| SD_SCK  | GPIO14| SPI Clock |
| SD_CS   | EXIO3 | Chip Select via TCA9554 |

---

## Buttons

| Funktion | GPIO  | Beschreibung |
|----------|-------|--------------|
| BOOT     | GPIO0 | Boot-Mode / User-Button (aktiv LOW) |

---

## config.py Referenz

```python
# Display (QSPI)
LCD_SDA0 = 46; LCD_SDA1 = 45; LCD_SDA2 = 42; LCD_SDA3 = 41
LCD_SCK = 40; LCD_CS = 21; LCD_BL = 5
LCD_W = 360; LCD_H = 360

# I2C Bus 0
I2C_SCL = 10; I2C_SDA = 11

# TCA9554 GPIO-Expander
TCA9554_ADDR = 0x20
EXIO0 = 0; EXIO1 = 1; EXIO2 = 2; EXIO3 = 3; EXIO4 = 4; EXIO5 = 5

# Touch (separater I2C Bus 1!)
TOUCH_SCL = 3; TOUCH_SDA = 1; TOUCH_INT = 4

# Audio I2S
SPEAK_DIN = 47; SPEAK_LRCK = 38; SPEAK_BCK = 48

# Mikrofon I2S
MIC_WS = 2; MIC_SCK = 15; MIC_SD = 39

# SD-Karte
SD_MISO = 16; SD_MOSI = 17; SD_SCK = 14

# Sensor-Adressen
IMU_ADDR = 0x6B; RTC_ADDR = 0x51
```
