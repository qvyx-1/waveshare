# boot.py — Wird bei jedem Start zuerst ausgeführt
# Waveshare ESP32-S3-LCD-1.85 SuperHero Watch

import gc
import esp32
import machine

# Garbage Collection aktivieren
gc.enable()
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

# CPU auf Maximalgeschwindigkeit setzen (240 MHz)
machine.freq(240_000_000)

# Flash-Größe prüfen
try:
    flash_size = esp32.flash_size()
    print(f"[BOOT] Flash: {flash_size // (1024*1024)} MB")
except:
    print("[BOOT] Flash-Größe: unbekannt")

# Free RAM ausgeben
print(f"[BOOT] RAM frei: {gc.mem_free() // 1024} KB")
print(f"[BOOT] CPU: {machine.freq() // 1_000_000} MHz")
print("[BOOT] SuperHero Watch wird gestartet...")
