# Test-Skript für BMP-Image Loading
# Waveshare ESP32-S3-LCD-1.85
# Führe via mpremote aus: python -m mpremote connect /dev/ttyACM0 run test_image.py

import gc
import time
import machine
import config

print("\n" + "="*50)
print("  BMP IMAGE LOADER TEST")
print("="*50)

# Hardware initialisieren
print("[TEST] Initialisiere Display...")
from display.driver import Display
from sensors.rtc import RTC

i2c = machine.I2C(0, 
                   sda=machine.Pin(config.I2C_SDA),
                   scl=machine.Pin(config.I2C_SCL),
                   freq=400_000)
display = Display(i2c=i2c)
display.init()
display.backlight(config.BL_BRIGHTNESS)

rtc = RTC(i2c)

print(f"[TEST] Display: {display.width}x{display.height}")
print(f"[TEST] RAM frei vor: {gc.mem_free() // 1024} KB")

# ImageLoader Test
print("\n[TEST] Teste ImageLoader...")
from display.image_loader import ImageLoader

# Erst schwarzen Hintergrund anzeigen
print("[TEST] Fülle mit schwarz...")
display.fill(display.BLACK)
display.show()
time.sleep(1)

# Versuche BMP zu laden
bmp_path = '/assets/bg.bmp'
print(f"[TEST] Lade {bmp_path}...")
success, message = ImageLoader.load_bmp(
    bmp_path,
    display.buffer,
    display.width,
    display.height
)

print(f"[TEST] Ergebnis: {message}")

if success:
    print("[TEST] ✓ Zeige Bild...")
    display.show()
    print("[TEST] ✓ BMP wird angezeigt!")
else:
    print("[TEST] ✗ BMP-Laden fehlgeschlagen")
    display.fill(display.RED)
    display.text("BMP FEHLER!", 100, 170, display.WHITE)
    display.show()

print(f"[TEST] RAM frei nach: {gc.mem_free() // 1024} KB")

# WatchFace Test
print("\n[TEST] Teste WatchFace mit BMP...")
from display.watch_face import WatchFace
from sensors.imu import IMU

imu = IMU(i2c)
face = WatchFace(display, rtc, imu, config, use_background=True)

print("[TEST] Lade BMP via WatchFace...")
success, msg = face.load_background_image(bmp_path)
print(f"[TEST] {msg}")

if success:
    # Zeichne ein paar Zeiger darauf
    print("[TEST] Zeichne Zeiger...")
    face.draw_hands(10, 30, 45)
    display.show()
    time.sleep(2)
    print("[TEST] ✓ Watchface mit BMP funktioniert!")
else:
    print("[TEST] ✗ WatchFace BMP-Laden fehlgeschlagen")

print("\n[TEST] Test abgeschlossen!")
print("="*50 + "\n")
