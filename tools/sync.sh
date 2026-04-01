#!/usr/bin/env bash
# SuperHero Watch — Power Sync Script (v3.1)
# Robustes Skript mit expliziten Pfaden für Treiber und Sensoren.

set -e

# Pfad-Magie: Finde das Projektverzeichnis
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_ROOT/src"

# Farben
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}🚀 SuperHero Watch POWER-SYNC v3.1${NC}"

# 1. Port automatisch finden
PORT=""
for p in /dev/ttyACM0 /dev/ttyACM1 /dev/ttyUSB0 /dev/ttyUSB1; do
    if [ -e "$p" ]; then
        PORT="$p"
        break
    fi
done

if [ -z "$PORT" ]; then
    echo -e "${RED}❌ Fehler: Kein Board gefunden! Stecke die Uhr neu ein.${NC}"
    exit 1
fi

echo -e "${CYAN}[1/4]${NC} Nutze Port: $PORT"

# 2. Port-Sperren aggressiv lösen
echo -e "${CYAN}[2/4]${NC} Löse Port-Sperren..."
pkill -9 mpremote || true
pkill -9 picocom || true
pkill -9 screen || true
fuser -k $PORT 2>/dev/null || true
sleep 1

# 3. Synchronisation
echo -e "${CYAN}[3/4]${NC} Übertrage Dateien aus $SRC_DIR..."
MPREMOTE="$HOME/.local/bin/mpremote"
[ -x "$MPREMOTE" ] || MPREMOTE="mpremote"

# Explizite Übertragung der Ordner und Dateien
# WICHTIG: Wir laden in die korrekten Unterordner auf der Uhr!
sync_action() {
    $MPREMOTE connect $PORT fs mkdir :display 2>/dev/null || true
    $MPREMOTE connect $PORT fs mkdir :sensors 2>/dev/null || true
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/config.py" :config.py
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/boot.py" :boot.py
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/display/driver.py" :display/driver.py
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/display/touch.py" :display/touch.py
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/display/watch_face.py" :display/watch_face.py
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/sensors/imu.py" :sensors/imu.py
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/sensors/rtc.py" :sensors/rtc.py
    $MPREMOTE connect $PORT fs cp "$SRC_DIR/main.py" :main.py
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
    echo -e "${YELLOW}⚠️  Versuch $RETRY_COUNT fehlgeschlagen. Warte kurz...${NC}"
    sleep 2
done

if [ "$SUCCESS" = false ]; then
    echo -e "${RED}❌ Fehler: Konnte Dateien nicht übertragen.${NC}"
    echo -e "${YELLOW}TIPP: Eventuell blockiert ein Terminal den Port.${NC}"
    exit 1
fi

# 4. Neustart
echo -e "${CYAN}[4/4]${NC} Starte Watch neu..."
$MPREMOTE connect $PORT reset

echo -e "${GREEN}✨ ALLES ERLEDIGT! Der Treiber und das Watchface sind aktuell.${NC}"
