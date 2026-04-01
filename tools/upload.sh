#!/usr/bin/env bash
# upload.sh — Projektcode auf ESP32-S3-LCD-1.85 übertragen
# Waveshare SuperHero Watch

set -e

PORT="${PORT:-/dev/ttyACM0}"
SRC_DIR="$(dirname "$0")/../src"

# Farben
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${CYAN}[UPLOAD]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}     $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}   $1"; }
error()   { echo -e "${RED}[ERR]${NC}    $1"; exit 1; }

# Tool-Check — prüfe sowohl PATH als auch ~/.local/bin
MPREMOTE=""
if command -v mpremote &> /dev/null; then
    MPREMOTE="mpremote"
elif [ -f "$HOME/.local/bin/mpremote" ]; then
    MPREMOTE="$HOME/.local/bin/mpremote"
else
    error "mpremote nicht gefunden! Installieren: pip install mpremote"
fi

# Port-Check
if [ ! -e "$PORT" ]; then
    warn "Port $PORT nicht gefunden."
    ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || true
    error "Verbinde das Board und versuche es erneut"
fi

echo ""
echo -e "${CYAN}  ⚡ SuperHero Watch — Code Upload${NC}"
echo "  Port: $PORT"
echo ""

M="$MPREMOTE connect $PORT"

# Verzeichnisse erstellen
info "Erstelle Verzeichnisse..."
$M mkdir :sensors   2>/dev/null || true
$M mkdir :display   2>/dev/null || true
$M mkdir :audio     2>/dev/null || true
$M mkdir :gadgets   2>/dev/null || true
$M mkdir :connectivity 2>/dev/null || true

# Konfiguration (zuerst!)
if [ -z "$1" ] || [ "$1" = "config.py" ]; then
    info "Übertrage config.py..."
    $M cp "$SRC_DIR/config.py" :config.py
    success "config.py"
fi

# Boot-Script
if [ -z "$1" ] || [ "$1" = "boot.py" ]; then
    info "Übertrage boot.py..."
    $M cp "$SRC_DIR/boot.py" :boot.py
    success "boot.py"
fi

# Sensoren
if [ -z "$1" ] || [[ "$1" == sensors/* ]]; then
    for f in "$SRC_DIR/sensors/"*.py; do
        [ -f "$f" ] || continue
        fname=$(basename "$f")
        info "Übertrage sensors/$fname..."
        $M cp "$f" ":sensors/$fname"
        success "sensors/$fname"
    done
fi

# Display
if [ -z "$1" ] || [[ "$1" == display/* ]]; then
    for f in "$SRC_DIR/display/"*.py; do
        [ -f "$f" ] || continue
        fname=$(basename "$f")
        info "Übertrage display/$fname..."
        $M cp "$f" ":display/$fname"
        success "display/$fname"
    done
fi

# Gadgets
if [ -z "$1" ] || [[ "$1" == gadgets/* ]]; then
    for f in "$SRC_DIR/gadgets/"*.py; do
        [ -f "$f" ] || continue
        fname=$(basename "$f")
        info "Übertrage gadgets/$fname..."
        $M cp "$f" ":gadgets/$fname"
        success "gadgets/$fname"
    done
fi

# Main (zuletzt!)
if [ -z "$1" ] || [ "$1" = "main.py" ]; then
    info "Übertrage main.py..."
    $M cp "$SRC_DIR/main.py" :main.py
    success "main.py"
fi

# Spezifische Datei?
if [ -n "$1" ] && [[ "$1" != */* ]]; then
    if [ -f "$SRC_DIR/$1" ]; then
        info "Übertrage $1..."
        $M cp "$SRC_DIR/$1" ":$1"
        success "$1"
    fi
fi

echo ""
success "Upload abgeschlossen! Board wird neugestartet..."
$M reset

echo ""
echo -e "${GREEN}  ✅ Fertig! Die SuperHero Watch startet ...${NC}"
echo "  Monitor öffnen: ./tools/monitor.sh"
echo ""
