#!/usr/bin/env bash
# SuperHero Watch — Power Sync Script (v4.0 Asyncio Edition)
# Überträgt alle Dateien aufs Board und startet neu.

set -e

# Pfad-Magie
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_ROOT/src"

# Farben
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}🚀 SuperHero Watch POWER-SYNC v4.0 (Asyncio Edition)${NC}"

# 1. Port automatisch finden
PORT=""
for p in /dev/ttyACM0 /dev/ttyACM1 /dev/ttyUSB0 /dev/ttyUSB1; do
    if [ -e "$p" ]; then
        PORT="$p"
        break
    fi
done

if [ -z "$PORT" ]; then
    echo -e "${RED}❌ Fehler: Kein Board gefunden!${NC}"
    exit 1
fi

echo -e "${CYAN}[1/4]${NC} Nutze Port: $PORT"

# 2. Port-Sperren lösen
echo -e "${CYAN}[2/4]${NC} Löse Port-Sperren..."
pkill -9 mpremote 2>/dev/null || true
pkill -9 picocom 2>/dev/null || true
pkill -9 screen 2>/dev/null || true
fuser -k $PORT 2>/dev/null || true
sleep 1

# 3. Synchronisation
echo -e "${CYAN}[3/4]${NC} Übertrage Dateien aus $SRC_DIR..."
# Nutze python -m mpremote für bessere venv-Kompatibilität
MPREMOTE="python -m mpremote"

sync_action() {
    # Ordnerstruktur erstellen
    $MPREMOTE connect $PORT fs mkdir :display 2>/dev/null || true
    $MPREMOTE connect $PORT fs mkdir :sensors 2>/dev/null || true
    $MPREMOTE connect $PORT fs mkdir :audio 2>/dev/null || true
    $MPREMOTE connect $PORT fs mkdir :gadgets 2>/dev/null || true
    $MPREMOTE connect $PORT fs mkdir :connectivity 2>/dev/null || true

    # Kern-Dateien
    echo -e "  ${CYAN}→${NC} config.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/config.py" :config.py
    echo -e "  ${CYAN}→${NC} boot.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/boot.py" :boot.py
    echo -e "  ${CYAN}→${NC} event_bus.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/event_bus.py" :event_bus.py

    # Display
    echo -e "  ${CYAN}→${NC} display/driver.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/display/driver.py" :display/driver.py
    echo -e "  ${CYAN}→${NC} display/touch.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/display/touch.py" :display/touch.py
    echo -e "  ${CYAN}→${NC} display/watch_face.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/display/watch_face.py" :display/watch_face.py
    echo -e "  ${CYAN}→${NC} display/image_loader.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/display/image_loader.py" :display/image_loader.py
    echo -e "  ${CYAN}→${NC} display/sd_manager.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/display/sd_manager.py" :display/sd_manager.py
    echo -e "  ${CYAN}→${NC} display/sd_mmc.py (SD-Karte SD-MMC Treiber)"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/display/sd_mmc.py" :display/sd_mmc.py

    # Sensoren
    echo -e "  ${CYAN}→${NC} sensors/imu.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/sensors/imu.py" :sensors/imu.py
    echo -e "  ${CYAN}→${NC} sensors/rtc.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/sensors/rtc.py" :sensors/rtc.py

    # Audio
    echo -e "  ${CYAN}→${NC} audio/driver.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/audio/driver.py" :audio/driver.py

    # Gadgets
    echo -e "  ${CYAN}→${NC} gadgets/__init__.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/gadgets/__init__.py" :gadgets/__init__.py

    # Connectivity
    echo -e "  ${CYAN}→${NC} connectivity/wifi.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/connectivity/wifi.py" :connectivity/wifi.py

    # Main (zuletzt!)
    echo -e "  ${CYAN}→${NC} main.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/main.py" :main.py

    # Demo Sequenz
    echo -e "  ${CYAN}→${NC} demo.py"
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/demo.py" :demo.py

    # Bitmap-Fonts aus Examples (für VGA-Text-Renderer)
    EXAMPLE_DIR="$PROJECT_ROOT/example"
    if [ -d "$EXAMPLE_DIR/bitmap" ]; then
        echo -e "  ${CYAN}→${NC} Erstelle /bitmap Ordner..."
        $MPREMOTE connect $PORT fs mkdir :bitmap 2>/dev/null || true
        for font in vga1_8x8 vga1_bold_16x32 vga1_16x32 vga1_16x16; do
            if [ -f "$EXAMPLE_DIR/bitmap/${font}.py" ]; then
                echo -e "  ${CYAN}→${NC} bitmap/${font}.py"
                $MPREMOTE connect $PORT fs cp "$EXAMPLE_DIR/bitmap/${font}.py" ":bitmap/${font}.py"
            fi
        done
    fi

    # Bluemarble Bitmap (NASA Earth) für Demo
    if [ -f "$EXAMPLE_DIR/bluemarble.mpy" ]; then
        echo -e "  ${CYAN}→${NC} bluemarble.mpy (Earth Bitmap)"
        $MPREMOTE connect $PORT fs cp "$EXAMPLE_DIR/bluemarble.mpy" ":bluemarble.mpy"
    elif [ -f "$EXAMPLE_DIR/bluemarble.py" ]; then
        echo -e "  ${CYAN}→${NC} bluemarble.py (Earth Bitmap)"
        $MPREMOTE connect $PORT fs cp "$EXAMPLE_DIR/bluemarble.py" ":bluemarble.py"
    fi
}

MAX_RETRIES=3
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if sync_action; then
        SUCCESS=true
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo -e "${YELLOW}⚠️  Versuch $RETRY_COUNT fehlgeschlagen. Warte...${NC}"
    sleep 2
done

if [ "$SUCCESS" = false ]; then
    echo -e "${RED}❌ Fehler: Konnte Dateien nicht übertragen.${NC}"
    exit 1
fi

# 4. Neustart
echo -e "${CYAN}[4/4]${NC} Starte Watch neu..."
$MPREMOTE connect $PORT reset

echo -e "${GREEN}✨ ALLES ERLEDIGT! SuperHero Watch v2.0 (Asyncio) ist deployed.${NC}"
