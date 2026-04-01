# Pin-Belegung — Waveshare ESP32-S3-LCD-1.85

> **Hinweis:** Diese Pins sind intern verschaltet. Externe I2C/UART-Pins sind begrenzt verfügbar.

---

## Display (ST7701 — SPI)

| Funktion | GPIO | Richtung | Beschreibung |
|----------|------|----------|-------------|
| LCD_CS   | 12   | OUT | Chip-Select (aktiv LOW) |
| LCD_CLK  | 13   | OUT | SPI Clock |
| LCD_MOSI | 11   | OUT | SPI Data (MOSI) |
| LCD_DC   | 4    | OUT | Data/Command (H=Data, L=Command) |
| LCD_RST  | 5    | OUT | Reset (aktiv LOW) |
| LCD_BL   | 38   | OUT | Backlight (PWM-fähig) |

---

## IMU: QMI8658 (I2C)

| Funktion | GPIO | Adresse |
|----------|------|---------|
| SDA      | 6    | 0x6B    |
| SCL      | 7    | —       |
| INT1     | 8    | —       |

---

## RTC: PCF85063 (I2C — same bus)

| Funktion | GPIO | Adresse |
|----------|------|---------|
| SDA      | 6    | 0x51    |
| SCL      | 7    | —       |

---

## GPIO-Expander: TCA9554 (I2C)

| Funktion | GPIO | Adresse |
|----------|------|---------|
| SDA      | 6    | 0x20    |
| SCL      | 7    | —       |

---

## TF-Karte / MicroSD (SPI — shared bus)

| Funktion | GPIO | Beschreibung |
|----------|------|-------------|
| SD_CS    | 15   | Chip-Select |
| SD_CLK   | 13   | SPI Clock (shared mit LCD) |
| SD_MOSI  | 11   | MOSI (shared mit LCD) |
| SD_MISO  | 14   | MISO |

---

## Audio: PCM5101 DAC (I2S Output)

| Funktion | GPIO | Beschreibung |
|----------|------|-------------|
| BCLK     | 17   | Bit Clock |
| LRCLK/WS | 18   | Left/Right Clock |
| DOUT     | 16   | Data Out |

---

## Mikrofon (I2S Input)

| Funktion | GPIO | Beschreibung |
|----------|------|-------------|
| MIC_BCLK | 39   | Bit Clock |
| MIC_WS   | 40   | Word Select |
| MIC_DATA | 41   | Data In |

---

## Buttons

| Funktion | GPIO | Beschreibung |
|----------|------|-------------|
| BOOT     | 0    | Boot-Mode / User-Button |
| POWER    | 21   | Power-Key Input |
| VOL      | 10   | Lautstärke |

---

## I2C Bus (extern nutzbar)

| Funktion | GPIO |
|----------|------|
| SDA      | 6    |
| SCL      | 7    |

> **Achtung:** Dieser I2C-Bus ist mit internen Chips (QMI8658, PCF85063, TCA9554) geteilt.
> Externe Geräte müssen unterschiedliche I2C-Adressen haben.

---

## UART (extern)

| Funktion | GPIO |
|----------|------|
| TX       | 43   |
| RX       | 44   |

> **Achtung:** Nur verfügbar wenn der UART-USB-Port nicht genutzt wird.

---

## config.py-Konstanten

```python
# src/config.py — Hardware Pin-Definitionen
# Display
LCD_CS   = 12
LCD_CLK  = 13
LCD_MOSI = 11
LCD_MISO = 14
LCD_DC   = 4
LCD_RST  = 5
LCD_BL   = 38

# I2C (IMU + RTC + GPIO-Expander)
I2C_SDA  = 6
I2C_SCL  = 7
IMU_INT  = 8

# TF-Card
SD_CS    = 15

# Audio DAC
I2S_BCLK = 17
I2S_WS   = 18
I2S_DOUT = 16

# Mikrofon
MIC_BCLK = 39
MIC_WS   = 40
MIC_DATA = 41

# Buttons
BOOT_BTN  = 0
POWER_BTN = 21

# I2C Adressen
QMI8658_ADDR = 0x6B
PCF85063_ADDR = 0x51
TCA9554_ADDR  = 0x20
```
