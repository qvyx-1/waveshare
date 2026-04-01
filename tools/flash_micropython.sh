#!/usr/bin/env bash
# flash_micropython.sh — MicroPython auf ESP32-S3-LCD-1.85 flashen
# Waveshare SuperHero Watch Setup Script

set -e

# ============================================================
# Konfiguration
# ============================================================
PORT="${PORT:-/dev/ttyACM0}"
FIRMWARE_DIR="$HOME/Downloads"
CHIP="esp32s3"
BAUD=921600

# ============================================================
# Farb-Output
# ============================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()    { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERR]${NC}  $1"; exit 1; }

# ============================================================
# Banner
# ============================================================
echo ""
echo -e "${RED}  ╔══════════════════════════════╗"
echo -e "  ║   ⚡ SuperHero Watch          ║"
echo -e "  ║   MicroPython Flash Script   ║"
echo -e "  ╚══════════════════════════════╝${NC}"
echo ""

# ============================================================
# Tool-Checks
# ============================================================
info "Prüfe benötigte Tools..."

if ! command -v esptool.py &> /dev/null && ! python3 -m esptool --help &>/dev/null; then
    error "esptool nicht gefunden! Installieren: pip install esptool"
fi

ESPTOOL="esptool.py"
if ! command -v esptool.py &> /dev/null; then
    ESPTOOL="python3 -m esptool"
fi
success "esptool gefunden"

# ============================================================
# Firmware-Erkennung
# ============================================================
info "Suche MicroPython-Firmware in $FIRMWARE_DIR..."

FIRMWARE=$(find "$FIRMWARE_DIR" -name "ESP32_GENERIC_S3*SPIRAM_OCT*.bin" 2>/dev/null | head -1)

if [ -z "$FIRMWARE" ]; then
    warn "Keine SPIRAM_OCT-Firmware gefunden!"
    echo ""
    echo "  Bitte lade die passende Firmware herunter von:"
    echo -e "  ${CYAN}https://micropython.org/download/ESP32_GENERIC_S3/${NC}"
    echo "  Empfehlung: ESP32_GENERIC_S3-SPIRAM_OCT-<version>.bin"
    echo ""
    read -p "Pfad zur Firmware eingeben: " FIRMWARE
fi

if [ ! -f "$FIRMWARE" ]; then
    error "Firmware nicht gefunden: $FIRMWARE"
fi
success "Firmware: $(basename $FIRMWARE)"

# ============================================================
# Port-Erkennung
# ============================================================
info "Suche Board auf $PORT..."

if [ ! -e "$PORT" ]; then
    warn "Port $PORT nicht gefunden. Verfügbare Ports:"
    ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || echo "  Keine Ports gefunden"
    echo ""
    echo "  Tipp: Board in Download-Mode versetzen:"
    echo "  1. Boot-Taste gedrückt halten"
    echo "  2. USB einstecken"
    echo "  3. Boot-Taste loslassen"
    echo ""
    read -p "Port eingeben (z.B. /dev/ttyACM0): " PORT
fi

success "Board-Port: $PORT"

# ============================================================
# Bestätigung
# ============================================================
echo ""
warn "⚠️  ACHTUNG: Der Flash-Speicher des Boards wird gelöscht!"
echo ""
echo "  Board:    Waveshare ESP32-S3-LCD-1.85"
echo "  Port:     $PORT"
echo "  Firmware: $(basename $FIRMWARE)"
echo "  Baudrate: $BAUD"
echo ""
read -p "Fortfahren? (j/N): " CONFIRM
if [[ "$CONFIRM" != "j" && "$CONFIRM" != "J" ]]; then
    echo "Abgebrochen."
    exit 0
fi

# ============================================================
# Flash löschen
# ============================================================
echo ""
info "Lösche Flash-Speicher..."
$ESPTOOL --chip $CHIP --port $PORT erase_flash
success "Flash gelöscht ✓"

sleep 2

# ============================================================
# MicroPython flashen
# ============================================================
info "Flashe MicroPython..."
$ESPTOOL --chip $CHIP \
         --port $PORT \
         --baud $BAUD \
         write_flash -z 0x0 "$FIRMWARE"
success "MicroPython geflasht ✓"

# ============================================================
# Verify
# ============================================================
echo ""
info "Warte auf Neustart..."
sleep 3

if command -v mpremote &> /dev/null; then
    info "Prüfe MicroPython-Version..."
    mpremote connect $PORT exec "import sys; print('MicroPython', sys.version)" 2>/dev/null \
        && success "Board läuft erfolgreich mit MicroPython!" \
        || warn "Konnte Version nicht prüfen — Reset-Knopf drücken und erneut versuchen"
fi

echo ""
echo -e "${GREEN}  ✅ MicroPython erfolgreich installiert!${NC}"
echo ""
echo "  Nächste Schritte:"
echo "  1. Code hochladen:  ./tools/upload.sh"
echo "  2. Monitor öffnen:  ./tools/monitor.sh"
echo "  3. REPL öffnen:     mpremote connect $PORT"
echo ""
