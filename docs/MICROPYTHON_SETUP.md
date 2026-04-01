# MicroPython Setup — ESP32-S3-LCD-1.85

## System-Voraussetzungen

```bash
# Python und pip
python3 --version  # >= 3.8 benötigt

# Benötigte Tools installieren
pip install esptool mpremote
```

---

## Schritt 1: Firmware herunterladen

### Empfohlene Firmware
**`ESP32_GENERIC_S3-SPIRAM_OCT`** — nutzt den 8MB OPI PSRAM des Boards

Download: https://micropython.org/download/ESP32_GENERIC_S3/

Dateiname-Muster: `ESP32_GENERIC_S3-SPIRAM_OCT-<version>.bin`

> **Warum SPIRAM_OCT?**  
> Das Board hat 8MB Octal-PSRAM. Die SPIRAM_OCT-Firmware nutzt diesen Speicher korrekt,
> was für das Rendern des 360×360 Displays (ca. 259KB Framebuffer) unerlässlich ist.

---

## Schritt 2: Board in Flash-Mode versetzen

1. Boot-Knopf **gedrückt halten**
2. USB-Kabel einstecken (oder Reset-Knopf drücken)
3. Boot-Knopf **loslassen**
4. Board erscheint als `ttyACM0` oder `ttyUSB0`

**Linux: Berechtigungen prüfen**
```bash
# Benutzer zur dialout-Gruppe hinzufügen
sudo usermod -aG dialout $USER
# Danach neu einloggen oder:
newgrp dialout
```

---

## Schritt 3: Flash löschen

```bash
esptool.py --chip esp32s3 --port /dev/ttyACM0 erase_flash
```

---

## Schritt 4: MicroPython flashen

```bash
esptool.py \
  --chip esp32s3 \
  --port /dev/ttyACM0 \
  --baud 921600 \
  write_flash -z 0x0 \
  ~/Downloads/ESP32_GENERIC_S3-SPIRAM_OCT-<VERSION>.bin
```

**Erwarteter Output:**
```
esptool.py v4.x.x
...
Writing at 0x00000000... (100 %)
Wrote 1638400 bytes
Hash of data verified.
Leaving...
```

---

## Schritt 5: Reset & Verify

```bash
# Reset (entweder Reset-Knopf drücken oder:)
esptool.py --chip esp32s3 --port /dev/ttyACM0 run

# MicroPython-Version prüfen
mpremote connect /dev/ttyACM0 exec "import sys; print(sys.version)"
```

---

## Schritt 6: Projekt-Code hochladen

```bash
# Mit Script
./tools/upload.sh

# Manuell
mpremote connect /dev/ttyACM0 cp -r src/. :
mpremote connect /dev/ttyACM0 reset
```

---

## Troubleshooting

### Board nicht erkannt
```bash
# USB-Gerät prüfen
dmesg | tail -30
ls /dev/tty*

# Falls kein Gerät: Boot-Mode erzwingen
# Knopf halten → USB einstecken → Knopf loslassen
```

### Flash schlägt fehl
```bash
# Niedrigere Baudrate versuchen
esptool.py --chip esp32s3 --port /dev/ttyACM0 --baud 115200 ...

# Falls immer noch Fehler: anderen USB-Port oder Kabel versuchen
```

### MicroPython startet nicht / Abstürze
- Falsche Firmware-Variante? → SPIRAM_OCT verwenden
- Flash-Fehler? → Nochmal löschen und flashen
- Code-Fehler? → `boot.py` und `main.py` prüfen

### REPL nicht erreichbar
```bash
# Prozesse die den Port blockieren beenden
sudo fuser -k /dev/ttyACM0

# Neu verbinden
mpremote connect /dev/ttyACM0
```

---

## Nützliche mpremote-Befehle

```bash
# Verbinden + REPL öffnen
mpremote connect /dev/ttyACM0

# Dateien auflisten
mpremote connect /dev/ttyACM0 ls :

# Datei hochladen
mpremote connect /dev/ttyACM0 cp local.py :remote.py

# Verzeichnis erstellen
mpremote connect /dev/ttyACM0 mkdir :sensors

# Verzeichnis hochladen
mpremote connect /dev/ttyACM0 cp -r src/. :

# Datei ausführen
mpremote connect /dev/ttyACM0 run test.py

# Python-Befehle ausführen
mpremote connect /dev/ttyACM0 exec "import gc; gc.collect(); print(gc.mem_free())"

# Board resetten
mpremote connect /dev/ttyACM0 reset
```
