#!/usr/bin/env python3
"""
Überprüfe welche MicroPython-Module und Treiber auf dem Board verfügbar sind.
"""

import subprocess
import sys

def run_command(cmd):
    """Führe Befehl auf dem Board aus."""
    full_cmd = f"python -m mpremote connect /dev/ttyACM0 eval \"{cmd}\""
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"

def check_module(module_name):
    """Prüfe ob ein Modul verfügbar ist."""
    cmd = f"'try: import {module_name}; print(\"YES: \" + str({module_name})\\ndir: \" + str(dir({module_name}))[:100]); except Exception as e: print(\"NO: \" + str(e))'"
    return run_command(cmd)

print("🔍 MicroPython Module & Treiber Check")
print("=" * 60)

# CPU-Infos
print("\n[1] CPU-Infos:")
print(run_command("'import sys; print(sys.implementation)'; print()"))

# Key modules to check
modules = [
    "machine",
    "sdcard",
    "vfs",
    "os",
    "machine.SDCard",
    "machine.SPI",
    "machine.I2C",
]

print("\n[2] Modul-Verfügbarkeit:")
for mod in modules:
    print(f"\n  {mod}:")
    if '.' in mod:
        # Spezielle Klasse
        base, cls = mod.split('.')
        cmd = f"'try: from {base} import {cls}; print(\"✓ Verfügbar\"); except: print(\"✗ Nicht vorhanden\")'"
    else:
        cmd = f"'try: import {mod}; print(\"✓ Verfügbar\"); except: print(\"✗ Nicht vorhanden\")'"
    print(f"  {run_command(cmd)}")

# Versuche etwas SD-spezifisches
print("\n[3] SD-spezifische Versuche:")

commands = [
    ("SDCard-Instanz erstellen", "'try: s=machine.SDCard(slot=1); print(\"✓ machine.SDCard OK\"); except Exception as e: print(\"✗ \" + str(e))[:80]'"),
    ("GPIO14/17/16 Test", "'from machine import Pin; p14=Pin(14); p17=Pin(17); p16=Pin(16); print(\"✓ Pins OK\")'"),
    ("EXIO4 via TCA9554", "'from display.sd_mmc import TCA9554Helper; print(\"✓ EXIO Helper OK\")'"),
]

for name, cmd in commands:
    print(f"\n  {name}:")
    print(f"  {run_command(cmd)}")

print("\n" + "=" * 60)
print("✅ Check abgeschlossen!")
