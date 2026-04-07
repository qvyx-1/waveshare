#!/usr/bin/env python3
# Test-Skript für DMA-optimierten BMP-Loader mit SD/Filesystem
# Waveshare ESP32-S3-LCD-1.85

import subprocess
import time

PORT = "/dev/ttyACM0"

print("\n" + "="*60)
print("  DMA-OPTIMIERTER BMP-LOADER TEST")
print("="*60 + "\n")

test_code = """
import gc
import machine
import config

print("[TEST] Initialisiere Hardware...")
from display.driver import Display
from sensors.rtc import RTC

i2c = machine.I2C(0, 
                   sda=machine.Pin(config.I2C_SDA),
                   scl=machine.Pin(config.I2C_SCL),
                   freq=400_000)
display = Display(i2c=i2c)
display.init()
display.backlight(config.BL_BRIGHTNESS)

print(f"[TEST] Display: {display.width}x{display.height}")
print(f"[TEST] RAM frei: {gc.mem_free() // 1024} KB")

# Test 1: FileSystemManager
print("\\n[TEST 1] FileSystemManager...")
from display.sd_manager import FileSystemManager
fsm = FileSystemManager.get_instance()

available = fsm.list_images()
print(f"[TEST]   Verfügbare Bilder: {list(available.keys())}")

# Test 2: DMA-optimierter BMP-Loader
print("\\n[TEST 2] DMA-optimierter BMP-Loader...")

# Schwarzer Hintergrund
display.fill(display.BLACK)
display.show()
import time
time.sleep(1)

from display.sd_manager import BackgroundDMA
bg_dma = BackgroundDMA(display)

if available:
    # Teste mit erster verfügbarer Datei
    bmp_file = list(available.keys())[0]
    print(f"[TEST]   Lade {bmp_file}...")
    
    success, message = bg_dma.load_background_from_file(bmp_file)
    print(f"[TEST]   Ergebnis: {message}")
    
    if success:
        print("[TEST] ✓ BMP-Laden erfolgreich!")
    else:
        print("[TEST] ✗ BMP-Laden fehlgeschlagen")
else:
    print("[TEST] ⚠️  Keine verfügbaren Bilder gefunden")
    print("[TEST] Bitte kopiere bg.bmp zu /assets/bg.bmp oder /sd/bg.bmp")

print(f"\\n[TEST] RAM frei nach: {gc.mem_free() // 1024} KB")
print("\\n[TEST] Fertig!")
"""

# Sende Test-Code
print("[UPLOAD] Sende Test-Skript...")
cmd = [
    'python', '-m', 'mpremote',
    'connect', PORT,
    'exec', test_code
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
        
except subprocess.TimeoutExpired:
    print("✗ Test Timeout (>60s) - Device möglicherweise nicht erreichbar")
except Exception as e:
    print(f"✗ Fehler: {e}")

print("\n" + "="*60)
print("  TEST ABGESCHLOSSEN")
print("="*60 + "\n")
