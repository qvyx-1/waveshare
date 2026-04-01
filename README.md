# ⚡ SuperHero Watch — Waveshare ESP32-S3 Project

> **MicroPython-basierte Superhelden-Uhr** für das Waveshare ESP32-S3-LCD-1.85 Development Board

---

## 🦸 Projektübersicht

Dieses Projekt implementiert eine interaktive **Superhelden-Uhr** auf Basis des Waveshare ESP32-S3-LCD-1.85 Boards.
Die Uhr läuft unter **MicroPython**, nutzt alle Onboard-Ressourcen und kann mit Gadgets erweitert werden.

### Projektstruktur

```
waveshare/
├── .github/
│   └── agents/
│       └── waveshare_connect_agent.md   # Verbindungs- & Setup-Agent
├── docs/
│   ├── BOARD.md                         # Board-Dokumentation
│   ├── MICROPYTHON_SETUP.md             # MicroPython Installationsanleitung
│   ├── PIN_MAP.md                       # Pin-Belegungen
│   └── HARDWARE.md                      # Onboard-Hardware Übersicht
├── src/
│   ├── main.py                          # Einstiegspunkt
│   ├── boot.py                          # Boot-Konfiguration
│   ├── config.py                        # Zentrale Konfiguration
│   ├── display/                         # Display-Treiber & UI
│   │   ├── driver.py                    # ST7701 LCD-Treiber
│   │   ├── watch_face.py               # Zifferblatt-Rendering
│   │   └── gadgets/                     # Erweiterbare Gadgets
│   ├── sensors/                         # Sensor-Module
│   │   ├── imu.py                       # QMI8658 IMU (6-Achsen)
│   │   └── rtc.py                       # PCF85063 RTC
│   ├── audio/                           # Audio-System
│   │   └── player.py                    # PCM5101 Audio-Decoder
│   ├── connectivity/                    # WiFi & BLE
│   │   ├── wifi.py                      # WiFi-Manager
│   │   └── ble.py                       # Bluetooth LE
│   └── gadgets/                         # Gadget-System
│       ├── __init__.py
│       ├── compass.py                   # Kompass-Gadget
│       ├── weather.py                   # Wetter-Gadget
│       └── steps.py                     # Schrittzähler-Gadget
├── tools/
│   ├── flash_micropython.sh             # MicroPython flashen
│   ├── upload.sh                        # Code auf Board übertragen
│   └── monitor.sh                       # Serielles Terminal
└── requirements.txt                     # Entwickler-Dependencies (Host)
```

---

## 🚀 Quick Start

### 1. MicroPython flashen
```bash
./tools/flash_micropython.sh
```

### 2. Dateien übertragen
```bash
./tools/upload.sh
```

### 3. Monitor öffnen
```bash
./tools/monitor.sh
```

---

## 🎯 Features

| Feature | Status | Beschreibung |
|---------|--------|-------------|
| ⏱️ Uhrzeit & Datum | ✅ | RTC PCF85063 Echtzeituhr |
| 🎨 Animiertes Zifferblatt | 🔄 | Superhelden-Design mit LVGL-Stil |
| 🧭 Kompass-Gadget | 🔄 | QMI8658 IMU-basiert |
| 🌤️ Wetter-Gadget | 🔄 | WiFi OpenWeatherMap |
| 👣 Schrittzähler | 🔄 | IMU-basierte Pedometer |
| 🔊 Audio-Feedback | 🔄 | PCM5101 Decoder |
| 📊 Systeminfo | 🔄 | Flash, RAM, Batterie |

**Status:** ✅ Fertig | 🔄 In Entwicklung | 📋 Geplant

---

## 🔧 Hardware

**Board:** Waveshare ESP32-S3-LCD-1.85
- **Prozessor:** Xtensa LX7 Dual-Core, bis 240 MHz
- **Display:** 1.85" rund, 360×360px, 262K Farben, SPI
- **RAM:** 512KB SRAM + 8MB PSRAM
- **Flash:** 16MB
- **Connectivity:** WiFi 802.11 b/g/n, Bluetooth 5 BLE
- **IMU:** QMI8658 (6-Achsen Gyro/Accel)
- **RTC:** PCF85063
- **Audio:** PCM5101 Decoder + MIC
- **TF-Slot:** MicroSD-Karte

---

## 📚 Dokumentation

- [Board Reference](docs/BOARD.md)
- [MicroPython Setup](docs/MICROPYTHON_SETUP.md)
- [Pin-Belegung](docs/PIN_MAP.md)
- [Agent-Anleitung](.github/agents/waveshare_connect_agent.md)

---

## 🤖 Agenten

Der **Verbindungs-Agent** übernimmt:
- Board-Erkennung & Verbindung
- MicroPython-Firmware flashen
- Code hochladen & ausführen
- Dokumentation aktuell halten

```
Starte Agent: .github/agents/waveshare_connect_agent.md
```
