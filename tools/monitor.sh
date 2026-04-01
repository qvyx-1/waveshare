#!/usr/bin/env bash
# monitor.sh — Serielles Terminal für ESP32-S3-LCD-1.85
# Waveshare SuperHero Watch

PORT="${PORT:-/dev/ttyACM0}"

echo ""
echo "  ⚡ SuperHero Watch — Serial Monitor"
echo "  Port:    $PORT"
echo "  Beenden: Ctrl+C oder Ctrl+]"
echo ""

if command -v mpremote &> /dev/null; then
    mpremote connect "$PORT"
elif command -v picocom &> /dev/null; then
    picocom -b 115200 "$PORT"
elif command -v screen &> /dev/null; then
    screen "$PORT" 115200
else
    echo "Kein Terminal-Tool gefunden!"
    echo "Installiere: pip install mpremote"
    echo "         oder: sudo apt install picocom"
fi
