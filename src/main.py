# main.py — SuperHero Watch Einstiegspunkt (Asyncio-Architektur)
# MicroPython für Waveshare ESP32-S3-LCD-1.85
#
# Architektur:
#   - asyncio-basiertes kooperatives Multitasking
#   - Event-Bus für lose Kopplung zwischen Subsystemen
#   - Separate Tasks für: Display, Touch, Button, Timer
#   - PSRAM Framebuffer mit partiellem Update

import gc
import time
import machine

import config
from event_bus import (
    EventBus,
    EVT_BUTTON_PRESS, EVT_BUTTON_LONG,
    EVT_TOUCH_TAP, EVT_TOUCH_SWIPE_UP, EVT_TOUCH_SWIPE_DOWN,
    EVT_TOUCH_SWIPE_LEFT, EVT_TOUCH_SWIPE_RIGHT, EVT_TOUCH_LONG_PRESS,
    EVT_TICK_1S, EVT_TICK_1M,
)


def startup_banner():
    """ASCII-Banner beim Start ausgeben."""
    print()
    print("  ╔══════════════════════════════╗")
    print("  ║   ⚡ SUPERHERO WATCH ⚡      ║")
    print("  ║   Asyncio Edition v2.0       ║")
    print(f"  ║   {config.WATCH_NAME:<26s}  ║")
    print("  ╚══════════════════════════════╝")
    print()


def init_hardware():
    """Hardware-Module initialisieren. Gibt (display, i2c, rtc, imu, touch) zurück."""
    from sensors.rtc import RTC
    from sensors.imu import IMU
    from display.driver import Display
    from display.touch import TouchCST816S

    print("[INIT] I2C Bus 0 (Sensoren)...")
    i2c = machine.I2C(0,
                       sda=machine.Pin(config.I2C_SDA),
                       scl=machine.Pin(config.I2C_SCL),
                       freq=400_000)

    devices = i2c.scan()
    hex_devs = [hex(d) for d in devices]
    print(f"[INIT] I2C-0 Geräte: {hex_devs}")

    print("[INIT] Display (ST77916 QSPI)...")
    display = Display(i2c=i2c)
    display.init()
    display.backlight(config.BL_BRIGHTNESS)
    print("[INIT] Display OK ✓")

    print("[INIT] RTC (PCF85063)...")
    rtc = RTC(i2c)
    print(f"[INIT] RTC OK ✓ — Zeit: {rtc.datetime()}")

    print("[INIT] IMU (QMI8658)...")
    imu = IMU(i2c)
    print(f"[INIT] IMU OK ✓ — Chip ID: {hex(imu.chip_id())}")

    # Touch-Controller (separater I2C Bus 1!)
    print("[INIT] Touch (CST816S, I2C Bus 1)...")
    touch = TouchCST816S()  # Erstellt eigenen I2C Bus
    has_touch = touch.check()
    if has_touch:
        print("[INIT] Touch OK ✓")
    else:
        print("[INIT] Touch nicht gefunden (Non-Touch Board oder Sleep)")

    gc.collect()
    print(f"[INIT] RAM frei: {gc.mem_free() // 1024} KB")

    return display, i2c, rtc, imu, touch


# ═══════════════════════════════════════════════
# Asyncio Tasks
# ═══════════════════════════════════════════════

async def task_button(bus):
    """Task: BOOT-Button mit Debouncing überwachen."""
    import uasyncio as asyncio
    btn = machine.Pin(config.BTN_BOOT, machine.Pin.IN, machine.Pin.PULL_UP)
    
    last_state = 1
    press_start = 0
    DEBOUNCE_MS = 200
    LONG_PRESS_MS = 800
    
    while True:
        state = btn.value()
        now = time.ticks_ms()
        
        if state == 0 and last_state == 1:
            # Taste gedrückt (fallende Flanke)
            press_start = now
        
        elif state == 1 and last_state == 0:
            # Taste losgelassen (steigende Flanke)
            duration = time.ticks_diff(now, press_start)
            if duration > DEBOUNCE_MS:
                if duration >= LONG_PRESS_MS:
                    bus.emit(EVT_BUTTON_LONG)
                    print("[BTN] Long Press")
                else:
                    bus.emit(EVT_BUTTON_PRESS)
                    print("[BTN] Press")
        
        last_state = state
        await asyncio.sleep_ms(20)


async def task_touch(bus, touch):
    """Task: Touch-Controller pollen und Events emittieren."""
    import uasyncio as asyncio
    from display.touch import TouchCST816S
    
    # Mapping: CST816S Gesture-Codes → Event-Bus Events
    GESTURE_MAP = {
        TouchCST816S.GESTURE_SINGLE_TAP: EVT_TOUCH_TAP,
        TouchCST816S.GESTURE_SWIPE_UP: EVT_TOUCH_SWIPE_UP,
        TouchCST816S.GESTURE_SWIPE_DOWN: EVT_TOUCH_SWIPE_DOWN,
        TouchCST816S.GESTURE_SWIPE_LEFT: EVT_TOUCH_SWIPE_LEFT,
        TouchCST816S.GESTURE_SWIPE_RIGHT: EVT_TOUCH_SWIPE_RIGHT,
        TouchCST816S.GESTURE_LONG_PRESS: EVT_TOUCH_LONG_PRESS,
    }
    
    last_gesture_time = 0
    
    while True:
        t = touch.read_touch()
        if t and t['pressed']:
            now = time.ticks_ms()
            gesture = t['gesture']
            
            # Doppel-Events innerhalb 300ms unterdrücken
            if time.ticks_diff(now, last_gesture_time) > 300:
                evt_type = GESTURE_MAP.get(gesture)
                if evt_type:
                    bus.emit(evt_type, {'x': t['x'], 'y': t['y']})
                    last_gesture_time = now
            
            await asyncio.sleep_ms(30)
        else:
            await asyncio.sleep_ms(50)


async def task_timer(bus):
    """Task: UI-Updates (100ms) und GC generieren."""
    import uasyncio as asyncio
    import gc
    tick = 0
    
    while True:
        # Dieser Fast-Tick weckt die UI auf. Im Watch Mode pollt das Display so die
        # RTC (hardwarenah) und verpasst nie den exakten Sekunden-Übergang.
        # Im Boot-Screen sorgt der Tick für >10 FPS schnelle Animationen.
        bus.emit(EVT_TICK_1S, {'tick': tick})
        tick += 1
            
        if tick >= 600:  # 60s (600 * 100ms)
            bus.emit(EVT_TICK_1M)
            gc.collect()  # GC jede Minute
            tick = 0
        
        await asyncio.sleep_ms(100)


# ═══════════════════════════════════════════════
# State Machine
# ═══════════════════════════════════════════════

STATE_BOOT  = 0
STATE_WATCH = 1


async def task_ui(bus, display, rtc, imu, touch, audio):
    """Haupt-UI-Task: State-Machine + Event-Verarbeitung."""
    import uasyncio as asyncio
    from display.watch_face import WatchFace

    face = WatchFace(display, rtc, imu, config, use_background=False)
    state = STATE_BOOT
    
    # Boot-Screen zeichnen
    print("[UI] Boot Screen...")
    face.draw_boot_screen()

    while True:
        # Auf nächstes Event warten
        evt = await bus.wait()

        if state == STATE_BOOT:
            # Im Boot-Screen: Button oder Tap → Watch-Face
            if evt.type in (EVT_BUTTON_PRESS, EVT_TOUCH_TAP):
                print("[UI] → Watch Face!")
                state = STATE_WATCH
                face._last_dt = None
                face.draw_background()
                face.update()
                
                # Starte Background-Loader Task
                asyncio.create_task(task_background_loader(bus, face))
                
                # Startup-Sound
                if audio:
                    try:
                        audio.play_sine(freq=880, duration_ms=80, volume=0.4)
                    except:
                        pass
            
            elif evt.type == EVT_TICK_1S:
                # Animation im Boot-Screen
                face.animate_boot_screen(audio=audio)

        elif state == STATE_WATCH:
            if evt.type == EVT_TICK_1S:
                face.update()
            
            elif evt.type == EVT_BUTTON_PRESS:
                print("[UI] Button im Watch-Modus")
                # Zukünftig: Menü, App-Wechsel etc.
            
            elif evt.type == EVT_BUTTON_LONG:
                print("[UI] Long Press → zurück zum Boot")
                state = STATE_BOOT
                face.draw_boot_screen()
            
            elif evt.type == EVT_TOUCH_TAP:
                if evt.data:
                    print(f"[UI] Tap @ ({evt.data['x']}, {evt.data['y']})")
            
            elif evt.type == EVT_TOUCH_SWIPE_LEFT:
                print("[UI] Swipe Left → nächstes Gadget")
                # TODO: Gadget-Navigation
            
            elif evt.type == EVT_TOUCH_SWIPE_RIGHT:
                print("[UI] Swipe Right → vorheriges Gadget")
                # TODO: Gadget-Navigation


async def task_boot_animation(bus, display, imu, audio):
    """Separate Task für flüssige Boot-Animation (unabhängig von Events)."""
    import uasyncio as asyncio
    from display.watch_face import WatchFace
    import math
    
    # Wir animieren direkt, solange wir im BOOT-State sind.
    # Diese Task wird per Flag gesteuert.
    # Für jetzt: Wir lassen die Animation über den EVT_TICK laufen (s. task_ui).
    # In Zukunft könnte man hier eine hochfrequente Animation machen.
    pass


async def task_color_test(display):
    """
    5-Sekunden Farbverlaufs-Testbild für Diagnose der RGB565-Farbcodierung.
    Zeigt mehrere Testmuster zum Fotografieren und Visualchecken.
    """
    import uasyncio as asyncio
    
    print("[COLOR-TEST] Starte Farbtests...")
    
    try:
        from display.sd_manager import ColorTestPattern
        
        # Test 1: Bunte Streifen (Farbreferenz)
        print("[COLOR-TEST] [1/3] Farbstreifen...")
        ColorTestPattern.create_horizontal_gradient(display)
        print("[COLOR-TEST] Fotografiere Streifen!")
        await asyncio.sleep(4)
        
        # Test 2: Glatter Farbverlauf (Sanftheit prüfen)
        print("[COLOR-TEST] [2/3] Sanfter Regenbogen-Verlauf...")
        ColorTestPattern.create_smooth_gradient(display)
        print("[COLOR-TEST] Fotografiere Verlauf!")
        await asyncio.sleep(4)
        
        # Test 3: Farbkacheln (Referenzwerte)
        print("[COLOR-TEST] [3/3] Farbkacheln...")
        ColorTestPattern.create_color_squares(display)
        print("[COLOR-TEST] Fotografiere Kacheln!")
        await asyncio.sleep(3)
        
        print("[COLOR-TEST] ✓ Farbtests komplett")
        
    except Exception as e:
        print(f"[COLOR-TEST] ✗ Fehler: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


async def task_background_loader(bus, display, i2c=None):
    """
    DEAKTIVIERT - SD-Karten-Debugging benötigt freien GPIO.
    I2C_SDA (GPIO11) ist belegt, TCA9554 ist problematisch.
    Benötigt: Neue Pinzuweisung oder direktes MicroSD-Modul.
    """
    import uasyncio as asyncio
    
    print("[BG-LOADER] SD-Initialisierung wird übergangen (GPIO-Konflikt)")
    await asyncio.sleep(1)


# ═══════════════════════════════════════════════
# Einstiegspunkt
# ═══════════════════════════════════════════════

def main():
    import uasyncio as asyncio

    startup_banner()

    try:
        display, i2c, rtc, imu, touch = init_hardware()

        # Audio initialisieren
        audio = None
        try:
            from audio.driver import Audio
            audio = Audio(rate=44100, i2c=i2c)
            audio.play_sine(freq=880, duration_ms=100, volume=0.5)
            print("[AUDIO] Startup-Ping ✓")
        except Exception as e:
            print(f"[AUDIO] Fehler: {e}")

        # Event-Bus erstellen
        bus = EventBus(maxsize=32)
        print("[INIT] Event-Bus erstellt ✓")

        # Asyncio Tasks starten
        async def run():
            # Demo-Sequenz beim Start
            print("[INIT] Starte Demo-Sequenz...")
            from demo import run_demo
            await run_demo(display)
            
            # SD-Karte initialisieren (SD-MMC, nicht SPI!)
            print("[INIT] Initialisiere SD-Karte (SD-MMC)...")
            try:
                from display.sd_mmc import SDCardMMC, test_sd_mmc
                sd_card = SDCardMMC(i2c)
                sd_success = sd_card.init()
                
                if sd_success:
                    print("[INIT] SD-Karte erfolgreich initialisiert ✓")
                    # Test nur wenn erfolgreich
                    try:
                        await test_sd_mmc(display, i2c)
                    except Exception as e:
                        print(f"[INIT] SD-Test konnte nicht ausgeführt werden: {e}")
                else:
                    print("[INIT] ⚠️  SD-Karte Initialisierung fehlgeschlagen (wird ignoriert)")
            except ImportError as e:
                print(f"[INIT] ⚠️  SD-MMC Modul nicht verfügbar: {e}")
            except Exception as e:
                print(f"[INIT] SD-Fehler (ignoriert): {type(e).__name__}: {e}")
            
            # Hintergrund-Tasks erzeugen
            asyncio.create_task(task_button(bus))
            asyncio.create_task(task_timer(bus))
            asyncio.create_task(task_background_loader(bus, display, i2c))
            
            # Touch-Task nur starten wenn Touch verfügbar
            if touch.available:
                asyncio.create_task(task_touch(bus, touch))
                print("[INIT] Touch-Task gestartet ✓")
            else:
                print("[INIT] Touch-Task übersprungen (kein Touch)")

            # Haupt-UI-Task (blockiert)
            await task_ui(bus, display, rtc, imu, touch, audio)

        print("[INIT] Starte asyncio Event-Loop...")
        print("=" * 40)
        asyncio.run(run())

    except KeyboardInterrupt:
        print("\n[WATCH] Gestoppt (Ctrl+C)")

    except Exception as e:
        import sys
        print(f"[FEHLER] {type(e).__name__}: {e}")
        sys.print_exception(e)

        try:
            display.fill(0x0000)
            display.text("ERROR!", 140, 170, 0xF800)
            err_msg = str(e)[:30]
            display.text(err_msg, 80, 190, 0xFFFF)
            display.show()
        except:
            pass

        time.sleep(5)
        machine.reset()


if __name__ == "__main__":
    main()
