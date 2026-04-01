#!/usr/bin/env bash
# test_connection.sh — Vollständiger Verbindungstest
# Waveshare ESP32-S3-LCD-1.85

PORT="${PORT:-/dev/ttyACM0}"

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

ok()   { echo -e "${GREEN}  ✅ $1${NC}"; }
fail() { echo -e "${RED}  ❌ $1${NC}"; }
info() { echo -e "${CYAN}  🔍 $1${NC}"; }

echo ""
echo "  ⚡ SuperHero Watch — Verbindungstest"
echo "  ======================================"
echo ""

# Port vorhanden?
info "Suche Board auf $PORT..."
if [ -e "$PORT" ]; then
    ok "Board gefunden auf: $PORT"
else
    fail "Port $PORT nicht gefunden!"
    echo "  Verfügbare Ports:"
    ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null | sed 's/^/    /'
    exit 1
fi

# mpremote verfügbar?
if ! command -v mpremote &> /dev/null; then
    fail "mpremote nicht installiert (pip install mpremote)"
    exit 1
fi

# MicroPython-Version
info "Prüfe MicroPython..."
VERSION=$(mpremote connect "$PORT" exec "import sys; print(sys.version)" 2>/dev/null || echo "FEHLER")
if [[ "$VERSION" != "FEHLER" ]]; then
    ok "MicroPython Version: $VERSION"
else
    fail "MicroPython nicht erreichbar — Reset-Knopf drücken und erneut versuchen"
    exit 1
fi

# RAM-Check
info "Prüfe PSRAM..."
RAM=$(mpremote connect "$PORT" exec "import gc; gc.collect(); print(gc.mem_free())" 2>/dev/null || echo "0")
if [ "$RAM" -gt "100000" ] 2>/dev/null; then
    ok "RAM verfügbar: $((RAM / 1024)) KB frei"
else
    fail "Wenig RAM: $RAM Bytes — SPIRAM_OCT Firmware empfohlen!"
fi

# I2C scan
info "I2C-Bus scannen..."
I2C_DEVS=$(mpremote connect "$PORT" exec "
import machine
i2c = machine.I2C(0, sda=machine.Pin(6), scl=machine.Pin(7), freq=400000)
devs = i2c.scan()
print([hex(d) for d in devs])
" 2>/dev/null || echo "[]")
ok "I2C Geräte: $I2C_DEVS"

# RTC prüfen
if echo "$I2C_DEVS" | grep -q "0x51"; then
    ok "RTC PCF85063 erreichbar (0x51)"
else
    fail "RTC PCF85063 nicht gefunden (0x51)"
fi

# IMU prüfen
if echo "$I2C_DEVS" | grep -q "0x6b\|0x6B"; then
    ok "IMU QMI8658 erreichbar (0x6B)"
else
    fail "IMU QMI8658 nicht gefunden (0x6B)"
fi

echo ""
echo "  ======================================"
echo "  Verbindungstest abgeschlossen!"
echo ""
