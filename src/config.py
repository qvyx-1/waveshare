# Zentrale Konfiguration — SuperHero Watch
# Waveshare ESP32-S3-LCD-1.85
# PINS VERIFIZIERT gegen offizielle Waveshare Wiki Dokumentation

# ============================================================
# DISPLAY PINS (ST77916 — QSPI, 4 Datenleitungen)
# ============================================================
LCD_SDA0 = 46   # QSPI Datenleitung 0 (MOSI)
LCD_SDA1 = 45   # QSPI Datenleitung 1
LCD_SDA2 = 42   # QSPI Datenleitung 2
LCD_SDA3 = 41   # QSPI Datenleitung 3
LCD_SCK  = 40   # QSPI Clock
LCD_CS   = 21   # Chip Select
LCD_BL   = 5    # Backlight (PWM)
# LCD_RST  = EXIO2 — gesteuert über TCA9554 GPIO-Expander!
# LCD_TE   = GPIO18 (Tearing Effect)

LCD_W    = 360  # Display-Breite
LCD_H    = 360  # Display-Höhe

# ============================================================
# I2C BUS (IMU + RTC + TCA9554 GPIO-Expander)
# ============================================================
I2C_SCL  = 10   # I2C Clock (ACHTUNG: nur I2C, kein GPIO!)
I2C_SDA  = 11   # I2C Data  (ACHTUNG: nur I2C, kein GPIO!)

# ============================================================
# GPIO-Expander TCA9554 (I2C Adresse 0x20)
# Steuert EXIO0..EXIO7
# ============================================================
TCA9554_ADDR = 0x20
EXIO0 = 0  # Bit 0
EXIO1 = 1  # Bit 1
EXIO2 = 2  # LCD_RST
EXIO3 = 3  # TF-Card CS (SD_D3/CS)
EXIO4 = 4  # IMU_INT2
EXIO5 = 5  # IMU_INT1

# ============================================================
# QMI8658 IMU (I2C — shared Bus mit RTC)
# ============================================================
IMU_SCL  = 10   # = I2C_SCL
IMU_SDA  = 11   # = I2C_SDA
IMU_ADDR = 0x6B

# ============================================================
# PCF85063 RTC (I2C — shared Bus)
# ============================================================
RTC_SCL  = 10   # = I2C_SCL
RTC_SDA  = 11   # = I2C_SDA
RTC_INT  = 9    # Interrupt-Pin
RTC_ADDR = 0x51

# ============================================================
# TF-CARD (SPI)
# ============================================================
SD_MISO  = 16   # SD_D0
SD_MOSI  = 17   # SD_CMD
SD_SCK   = 14   # SD_SCK
# SD_CS   = EXIO3 (via TCA9554!)

# ============================================================
# AUDIO PCM5101 (I2S)
# ============================================================
SPEAK_DIN  = 47  # I2S Data
SPEAK_LRCK = 38  # I2S Word Select / LRCK
SPEAK_BCK  = 48  # I2S Bit Clock

# ============================================================
# MICROPHONE (I2S)
# ============================================================
MIC_WS  = 2    # Word Select
MIC_SCK = 15   # Bit Clock
MIC_SD  = 39   # Data

# ============================================================
# TOUCHSCREEN CST816S (I2C 0x15)
# ACHTUNG: Nutzt einen separaten I2C-Bus!
# ============================================================
TOUCH_SCL = 3
TOUCH_SDA = 1
TOUCH_INT = 4

# ============================================================
# BUTTONS
# ============================================================
BTN_BOOT  = 0   # BOOT-Taste
BTN_POWER = None # Power über TCA9554 (EXIO?)
LCD_TE    = 18   # Tearing Effect

# ============================================================
# WIFI (optional — in secrets.py ablegen!)
# ============================================================
try:
    from secrets import WIFI_SSID, WIFI_PASSWORD
except ImportError:
    WIFI_SSID     = ""
    WIFI_PASSWORD = ""
WIFI_TIMEOUT = 15

# ============================================================
# WATCH EINSTELLUNGEN
# ============================================================
WATCH_NAME   = "SuperHero Watch"
WATCH_EDITION = "Iron Edition"
CPU_FREQ_MHZ = 240
BL_BRIGHTNESS = 512  # 0-1023 (50%)
