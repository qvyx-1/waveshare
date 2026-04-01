# Zentrale Konfiguration — SuperHero Watch
# Waveshare ESP32-S3-LCD-1.85

# ============================================================
# DISPLAY PINS (ST7701 — SPI)
# ============================================================
LCD_CS   = 12    # Chip-Select (aktiv LOW)
LCD_CLK  = 13    # SPI Clock
LCD_MOSI = 11    # MOSI / SPI Data Out
LCD_MISO = 14    # MISO (für SD-Karte)
LCD_DC   = 4     # Data/Command
LCD_RST  = 5     # Reset (aktiv LOW)
LCD_BL   = 38    # Backlight (PWM)
LCD_W    = 360   # Display-Breite (Pixel)
LCD_H    = 360   # Display-Höhe (Pixel)

# ============================================================
# I2C BUS (IMU + RTC + GPIO-Expander)
# ============================================================
I2C_SDA  = 6
I2C_SCL  = 7
I2C_FREQ = 400_000  # 400kHz Fast Mode

# I2C Adressen
QMI8658_ADDR  = 0x6B   # IMU / 6-Achsen-Sensor
PCF85063_ADDR = 0x51   # RTC Echtzeituhr
TCA9554_ADDR  = 0x20   # GPIO-Expander
IMU_INT_PIN   = 8      # IMU Interrupt

# ============================================================
# TF-KARTE (SPI — shared bus mit Display)
# ============================================================
SD_CS    = 15

# ============================================================
# AUDIO DAC: PCM5101 (I2S Ausgang)
# ============================================================
I2S_BCLK = 17
I2S_WS   = 18
I2S_DOUT = 16

# ============================================================
# MIKROFON (I2S Eingang)
# ============================================================
MIC_BCLK = 39
MIC_WS   = 40
MIC_DATA = 41

# ============================================================
# BUTTONS
# ============================================================
BOOT_BTN  = 0    # BOOT / User-Button
POWER_BTN = 21   # Power-Key

# ============================================================
# SUPERHERO WATCH KONFIGURATION
# ============================================================

# Watch Face Einstellungen
WATCH_FACE_BG_COLOR   = 0x0000   # Hintergrundfarbe (16-bit RGB565) — Schwarz
WATCH_FACE_ACCENT     = 0x07E0   # Akzentfarbe — Grün (Superhelden-Style)
WATCH_FACE_TEXT_COLOR = 0xFFFF   # Textfarbe — Weiß

# Superhelden-Thema: "IRON WATCH"
HERO_NAME    = "IRON WATCH"
HERO_COLOR   = 0xF800   # Rot (Iron Man Style)
HERO_ACCENT  = 0xFFE0   # Gold

# Backlight
BL_DEFAULT_DUTY = 512   # PWM 0-1023 (50%)
BL_MIN_DUTY     = 50
BL_MAX_DUTY     = 1023
BL_DIM_DUTY     = 100   # Nach Inaktivität

# Energie-Management
SLEEP_AFTER_SEC   = 30  # Sekunden bis Display abdimmt
DEEPSLEEP_AFTER_S = 300 # Sekunden bis Deep Sleep

# WiFi (Optional — über Gadgets)
WIFI_SSID     = ""      # In secrets.py definieren!
WIFI_PASSWORD = ""      # In secrets.py definieren!
WIFI_TIMEOUT  = 10      # Sekunden

# NTP Zeit-Synchronisierung
NTP_HOST   = "pool.ntp.org"
TIMEZONE_OFFSET = 2     # UTC+2 (CEST) — anpassen!

# Gadget-System
GADGETS_ENABLED = [
    "clock",     # Immer aktiv
    "compass",   # QMI8658-basiert
    "steps",     # Schrittzähler
    # "weather", # Benötigt WiFi — aktivieren wenn konfiguriert
]

# Audio
AUDIO_ENABLED = True
AUDIO_VOLUME  = 50   # 0-100%
