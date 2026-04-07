================================================================================
WAVESHARE ESP32-S3-LCD-1.85 BOARD — DIAGNOSE
================================================================================
Datum: 2026-04-02 15:42:55

[VERBINDUNG]
----------------------------------------
✓ Serieller Port: /dev/ttyACM0
✓ Baudrate: 115200
✓ Handshake erkannt

[STARTUP-AUSGABE]
----------------------------------------


[REPL-BEFEHLE]
----------------------------------------

MicroPython-Version:
  import sys; print('MicroPython Version:', sys.implementation[3])
  MicroPython Version: 11014

Flash-Größe:
  import esp32; print('Flash-Gre:', esp32.flash_size(), 'bytes')
  Traceback (most recent call last):
  File "<stdin>", line 1, in <module>

CPU-Frequenz:
  import machine; print('CPU-Frequenz:', machine.freq() // 1000000, 'MHz')
  CPU-Frequenz: 240 MHz

Speicherstatus:
  import gc; gc.collect(); print('RAM frei:', gc.mem_free(), 'bytes'); print('RAM alloc:', gc.mem_alloc(), 'bytes')
  RAM frei: 7940464 bytes
  RAM alloc: 311504 bytes

Dateisystem:
  import os; print('Filesystem:', os.listdir('/'))
  Filesystem: ['audio', 'boot.py', 'config.py', 'connectivity', 'display', 'event_bus.py', 'gadgets', 'main.py', 'sensors', 'watch_face.py']

WiFi MAC:
  import network; wlan = network.WLAN(network.STA_IF); print('WiFi MAC:', wlan.config('mac').hex())
  WiFi MAC: 30eda0ad969c


[I2C-SCAN]
----------------------------------------
I2C Import:
  from machine import I2C, Pin
I2C Bus 0 (RTC/IMU):
  i2c0 = I2C(0, scl=Pin(7), sda=Pin(6), freq=400000); devices0 = i2c0.scan(); print('I2C Bus 0:', [hex(d) for d in devices0])

================================================================================
DIAGNOSE ERFOLGREICH ABGESCHLOSSEN
================================================================================