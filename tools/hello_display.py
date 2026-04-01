# hello_display.py — Hello World Test für Waveshare ESP32-S3-LCD-1.85
# Standalone — keine externen Module nötig
# Direktes SPI-Rendering auf den ST7701S Display-Controller

import machine
import time

print("=== Display Hello World ===")

# ——— Pins (aus Waveshare-Schaltplan) ———
PIN_BL   = 38   # Backlight (PWM)
PIN_RST  = 5    # Reset
PIN_DC   = 4    # Data/Command
PIN_CS   = 12   # Chip-Select
PIN_CLK  = 13   # SPI Clock
PIN_MOSI = 11   # SPI Data

W = 360
H = 360

# ——— GPIO initialisieren ———
bl  = machine.Pin(PIN_BL,  machine.Pin.OUT)
rst = machine.Pin(PIN_RST, machine.Pin.OUT)
dc  = machine.Pin(PIN_DC,  machine.Pin.OUT)
cs  = machine.Pin(PIN_CS,  machine.Pin.OUT)

# SPI Bus
spi = machine.SPI(1,
                  baudrate=40_000_000,
                  polarity=0, phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(PIN_CLK),
                  mosi=machine.Pin(PIN_MOSI))

# Backlight erstmal aus
bl.value(0)
cs.value(1)
dc.value(1)

# ——— Hilfsfunktionen ———
def write_cmd(cmd):
    dc.value(0)
    cs.value(0)
    spi.write(bytes([cmd]))
    cs.value(1)

def write_data(data):
    dc.value(1)
    cs.value(0)
    if isinstance(data, (list, tuple)):
        spi.write(bytes(data))
    else:
        spi.write(bytes([data]))
    cs.value(1)

def hard_reset():
    rst.value(1); time.sleep_ms(10)
    rst.value(0); time.sleep_ms(50)
    rst.value(1); time.sleep_ms(120)

# ——— ST7701S Initialisierung ———
# Quelle: Waveshare-Demo + ST7701S Datenblatt
def init_display():
    hard_reset()

    # Befehlsseite 1 entsperren
    write_cmd(0xFF)
    write_data([0x77, 0x01, 0x00, 0x00, 0x10])

    # LN/LINESET
    write_cmd(0xC0); write_data([0x3B, 0x00])
    write_cmd(0xC1); write_data([0x0D, 0x02])
    write_cmd(0xC2); write_data([0x31, 0x05])
    write_cmd(0xCD); write_data([0x00])

    # Positive Gamma
    write_cmd(0xB0)
    write_data([0x00,0x11,0x18,0x0E,0x11,0x06,
                0x07,0x08,0x07,0x22,0x04,0x12,
                0x0F,0xAA,0x31,0x18])
    # Negative Gamma
    write_cmd(0xB1)
    write_data([0x00,0x11,0x19,0x0E,0x12,0x07,
                0x08,0x08,0x08,0x22,0x04,0x11,
                0x11,0xA9,0x32,0x18])

    # Befehlsseite 2
    write_cmd(0xFF)
    write_data([0x77, 0x01, 0x00, 0x00, 0x11])

    write_cmd(0xB0); write_data([0x60])   # VCOM
    write_cmd(0xB1); write_data([0x32])   # VRHA
    write_cmd(0xB2); write_data([0x07])   # VRHB
    write_cmd(0xB3); write_data([0x80])
    write_cmd(0xB5); write_data([0x49])   # VFP
    write_cmd(0xB7); write_data([0x85])
    write_cmd(0xB8); write_data([0x21])
    write_cmd(0xC1); write_data([0x78])
    write_cmd(0xC2); write_data([0x78])
    time.sleep_ms(20)

    write_cmd(0xE0); write_data([0x00, 0x1B, 0x02])
    write_cmd(0xE1)
    write_data([0x08,0xA0,0x00,0x00,0x07,0xA0,0x00,0x00,0x00,0x44,0x44])
    write_cmd(0xE2)
    write_data([0x11,0x11,0x44,0x44,0xED,0xA0,0x00,0x00,0xEC,0xA0,0x00,0x00])
    write_cmd(0xE3); write_data([0x00,0x00,0x11,0x11])
    write_cmd(0xE4); write_data([0x44,0x44])
    write_cmd(0xE5)
    write_data([0x0A,0xE9,0xD8,0xA0,0x0C,0xEB,0xD8,0xA0,
                0x0E,0xED,0xD8,0xA0,0x10,0xEF,0xD8,0xA0])
    write_cmd(0xE6); write_data([0x00,0x00,0x11,0x11])
    write_cmd(0xE7); write_data([0x44,0x44])
    write_cmd(0xE8)
    write_data([0x09,0xE8,0xD8,0xA0,0x0B,0xEA,0xD8,0xA0,
                0x0D,0xEC,0xD8,0xA0,0x0F,0xEE,0xD8,0xA0])
    write_cmd(0xEB)
    write_data([0x02,0x00,0xE4,0xE4,0x88,0x00,0x40])
    write_cmd(0xEC); write_data([0x3C,0x00])
    write_cmd(0xED)
    write_data([0xAB,0x89,0x76,0x54,0x02,0xFF,0xFF,0xFF,
                0xFF,0xFF,0xFF,0x20,0x45,0x67,0x98,0xBA])

    # Befehlsseite 0 (normal)
    write_cmd(0xFF)
    write_data([0x77, 0x01, 0x00, 0x00, 0x00])

    write_cmd(0x3A); write_data([0x55])   # Pixel Format: RGB565
    write_cmd(0x36); write_data([0x00])   # MADCTL

    write_cmd(0x11)   # Sleep Out
    time.sleep_ms(120)
    write_cmd(0x29)   # Display On
    time.sleep_ms(50)

    print("Display initialisiert ✓")

def set_window(x0, y0, x1, y1):
    write_cmd(0x2A)
    write_data([x0>>8, x0&0xFF, x1>>8, x1&0xFF])
    write_cmd(0x2B)
    write_data([y0>>8, y0&0xFF, y1>>8, y1&0xFF])
    write_cmd(0x2C)

def fill_color(color):
    """Ganzen Bildschirm mit RGB565-Farbe füllen."""
    set_window(0, 0, W-1, H-1)
    hi = color >> 8
    lo = color & 0xFF
    chunk = bytes([hi, lo] * 256)
    total = W * H
    dc.value(1); cs.value(0)
    for _ in range(total // 256):
        spi.write(chunk)
    rest = total % 256
    if rest:
        spi.write(bytes([hi, lo] * rest))
    cs.value(1)

def fill_rect(x, y, w, h, color):
    """Gefülltes Rechteck."""
    set_window(x, y, x+w-1, y+h-1)
    hi = color >> 8
    lo = color & 0xFF
    row = bytes([hi, lo] * w)
    dc.value(1); cs.value(0)
    for _ in range(h):
        spi.write(row)
    cs.value(1)

# ——— MAIN ———
print("Initialisiere Display...")
init_display()

# Backlight an (50% Helligkeit über PWM)
bl_pwm = machine.PWM(machine.Pin(PIN_BL), freq=1000, duty=512)
print("Backlight an ✓")

# ——— HELLO WORLD Sequenz ———

# 1. Schwarzer Hintergrund
print("Fülle Bildschirm schwarz...")
fill_color(0x0000)
time.sleep_ms(500)

# 2. Rotes Quadrat (Aufmerksamkeits-Test)
print("Rotes Rechteck...")
fill_rect(80, 80, 200, 200, 0xF800)    # Rot
time.sleep_ms(500)

# 3. Komplette Farbfüllung — IRON MAN ROT
print("Iron Man Rot...")
fill_color(0xF800)
time.sleep_ms(800)

# 4. Gold
print("Gold...")
fill_color(0xFFE0)
time.sleep_ms(800)

# 5. Blau
print("Blau...")
fill_color(0x001F)
time.sleep_ms(800)

# 6. Grün
print("Grün...")
fill_color(0x07E0)
time.sleep_ms(800)

# 7. Finaler Bildschirm: Dunkler Hintergrund + zentriertes Kreuz (Zifferblatt-Basis)
print("Final: Watch-Hintergrund...")
fill_color(0x0000)  # Schwarz

# Äußerer Ring: Roter Rahmen (vereinfacht mit Rechtecken)
fill_rect(0, 0, 360, 8, 0xF800)      # Oben
fill_rect(0, 352, 360, 8, 0xF800)    # Unten
fill_rect(0, 0, 8, 360, 0xF800)      # Links
fill_rect(352, 0, 8, 360, 0xF800)    # Rechts

# Goldenes Kreuz
fill_rect(176, 60, 8, 240, 0xFFE0)   # Vertikal
fill_rect(60, 176, 240, 8, 0xFFE0)   # Horizontal

# Zentrum-Punkt
fill_rect(172, 172, 16, 16, 0xFFFF)  # Weiß

print()
print("=================================")
print("✅ Hello World Display — fertig!")
print("=================================")
print("Angezeigt:")
print("  1. Schwarz       → Display sauber")
print("  2. Rot/Gold/Blau → Farben OK")
print("  3. Watch-Layout  → Framework bereit")
print()
print("Backlight läuft auf:", bl_pwm.duty(), "/ 1023")
