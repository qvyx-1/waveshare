# SD-Karten Status — Waveshare ESP32-S3-LCD-1.85

## ⚠️ Aktueller Status: Eingeschränkt funktionierend

Das Board hat **echte SD-MMC 1-Bit Hardware**, aber der MicroPython-Build hat `machine.SDCard()` **NICHT aktiviert**.

**Momentane Lösung**: SPI-basierte Diagnose (CMD0-Test funktioniert)
**Vollständige Lösung**: Braucht Firmware-Neucompilierung oder C-Extension

---

## Hardware-Realität

### ✓ Waveshare nutzt SD-MMC (clever designed):
```
Pins:
├── CLK (GPIO14)     - Takt
├── CMD (GPIO17)     - Befehl (echtes MMC-Protokoll!)
├── D0  (GPIO16)     - Daten Line 0
└── EXIO4 (TCA9554)  - Power-Enable (nicht GPIO11!)

Vorteil: Vermeidet GPIO11-Konflikt mit I2C_SDA
Speed: Bis 200 Mbps (vs. SPI ~50 Mbps)
```

### ✗ MicroPython-Build Problem:

Das Waveshare .uf2 wurde **OHNE** `machine.SDCard()` Support kompiliert:
```python
# Versucht man:
sd = machine.SDCard(slot=2, ...)
# Resultat: HANG oder AttributeError
```

---

## Entdeckungs-Prozess

1. **Problem**: SD-Init schien zu hängen
2. **Diagnose**: `machine.SDCard(slot=2, sck=14, mosi=17, miso=16)` existiert nicht
3. **Grund**: Waveshare MicroPython-Build kompiliert nicht alle Module
4. **Workaround**: SPI-Fallback mit CMD0-Diagnose

---

## Aktuell verfügbar: SPI-Diagnose-Modus

```python
# sd_mmc.py - vereinfachte SPI-Implementierung
from display.sd_mmc import SDCardMMC

sd = SDCardMMC()
sd.init()  # Sende CMD0

# Status:
# ✓ SD erkannt (CMD0 → 0x01)
# ✗ Filesystem nicht gemountet
# ✗ Datei-Zugriff nicht möglich
```

### Boot-Output:
```
[INIT] Initialisiere SD-Karte...
[SD] Initialisiere SD-Karte...
[SD] ✓ SPI-Bus erstellt
[SD] ✓ SD-Karte erkannt      ← nur Diagnose!
[INIT] OK (nicht fatal)
```

**Wichtig**: System **crasht nicht**. SD wird gracefully übersprungen.

---

## GPIO-Konflikt erklärt

```
I2C_SDA = GPIO11  ← PROBLEM: auch SPI_CS = GPIO11!
        ↙
Kann nicht beide gleichzeitig nutzen.
```

**Darum nutzt Arduino SD-MMC** statt SPI:
- GPIO14/17/16 sind NICHT I2C-Pins
- Kein Konflikt möglich

---

## Lösungs-Optionen

### Option A: Firmware neu-compilieren ⭐ RECOMMENDED
**Aufwand**: 1-2 Stunden  
**Komplexität**: Mittel

```bash
git clone https://github.com/micropython/micropython.git
cd ports/esp32

# Compiliere mit SD-Support
./mpy-cross -O2 --enable-sdcard \
  -DMICROPY_HW_SDCARD_MOUNT_POINT=/sd

# Flash das .uf2 auf Board
```

**Resultat**: Vollständiger SD-Zugriff, BMP-Loading möglich

---

### Option B: Kontakte Waveshare
> "Brauche MicroPython mit `machine.SDCard()` support für ESP32-S3-LCD-1.85"

**Aufwand**: Keine (nur Anfrage)
**Chancen**: Mittel-Hoch (wenn regelmäßig aktualisiert)

---

### Option C: Custom C-Extension
Schreibe native Wrapper um ESP-IDF `sdmmc_host`:

```c
// sdmmc_wrapper.c
#include "driver/sdmmc_host.h"
STATIC mp_obj_t mp_sdmmc_init(void) { ... }
MODULE_FUNCS(sdmmc)
```

Compiliere als `.mpy` Modul.

**Aufwand**: 3-5 Stunden (C-Kenntnisse erforderlich)
**Resultat**: Direkter SD-MMC Access in MicroPython

---

### Option D: Akzeptiere Diagnose-Modus
Bleibt bei aktueller Implementierung:
- SD wird diagnostiziert (CMD0-Test)
- Watch-Face nutzt hardcoded Hintergründe
- Keine echte Asset-Loading

**Aufwand**: Keine  
**Resultat**: System funktioniert, SD eingeschränkt

---

## Diagnostik: Überprüfe aktuelle Firmware

```python
# Im REPL auf dem Board:
import machine
print(machine.implementation())

# Versuche:
try:
    sd = machine.SDCard(slot=1)
    print("✓ SD-Support vorhanden!")
except AttributeError as e:
    print("✗ Kein machine.SDCard:", e)
```

---

## Vergleich: Arduino vs. MicroPython

### Arduino (funktioniert perfekt):
```cpp
#include "SD_MMC.h"

SD_MMC.setPins(14, 17, 16);  // CLK, CMD, D0
if(SD_MMC.begin("/sdcard", true, true)) {
    File f = SD_MMC.open("/bluemarble.bmp");
    byte buf[512];
    f.read(buf, 512);
    // ✓ Funktioniert!
}
```

### MicroPython (idealtheoretisch, nicht verfügbar):
```python
import machine
import vfs

sd = machine.SDCard(
    slot=2,
    sck=machine.Pin(14),
    mosi=machine.Pin(17),
    miso=machine.Pin(16)
)
vfs.mount(sd, '/sd')

# x = open('/sd/bluemarble.bmp', 'rb').read(512)
# → NICHT möglich, weil machine.SDCard nicht im Build
```

---

## Lektionen gelernt

1. **Hardware ≠ Software**
   - Waveshare hat SD-MMC Hardware
   - Aber MicroPython-Build kennt sie nicht

2. **ESP-IDF ≠ Arduino ≠ MicroPython**
   - Alle drei unterschiedliche Abstraktionsebenen
   - Arduino gut dokumentiert, MicroPython-Bindings oft fehlend

3. **GPIO-Konflikte früh finden**
   - GPIO11 für I2C_SDA + SPI_CS = Design-Problem
   - Arduino benutzt SD-MMC genau deswegen

4. **Graceful Fallback wichtig**
   - System crasht NICHT wenn SD-Feature fehlt
   - Nur Funktionalität eingeschränkt

---

## Links & Referenzen

- **Waveshare Wiki**: https://www.waveshare.com/wiki/ESP32-S3-LCD-1.85
- **MicroPython**: https://docs.micropython.org/
- **ESP-IDF SD-MMC**: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/storage/sdmmc_host.html
- **Arduino SD**: https://github.com/espressif/arduino-esp32 (SD_MMC.h)

---

## Nächste Schritte (falls SD voll gewünscht)

1. Entscheide für Option A, B, oder C
2. Implementiere neueste Solution
3. Flash neues .uf2
4. Test: CMD0 sollte arbeiten + Filesystem mounten
5. Aktiviere `task_background_loader` in main.py
6. Lade BMPs von /sd/

---

**Stand**: 2025 März — SPI-Diagnose funktioniert; vollständige Lösung pending Firmware-Update
