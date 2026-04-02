# main.py — SuperHero Watch Einstiegspunkt
# MicroPython für Waveshare ESP32-S3-LCD-1.85

import gc
import time
import machine

import config


def startup_banner():
    """ASCII-Banner beim Start ausgeben."""
    print()
    print("  ╔══════════════════════════════╗")
    print("  ║   ⚡ SUPERHERO WATCH ⚡      ║")
    print("  ║   Waveshare ESP32-S3-LCD     ║")
    print(f"  ║   {config.WATCH_NAME:<26s}  ║")
    print("  ╚══════════════════════════════╝")
    print()


def init_hardware():
    """Hardware-Module initialisieren."""
    from sensors.rtc import RTC
    from sensors.imu import IMU
    from display.driver import Display

    print("[INIT] I2C Bus...")
    i2c = machine.I2C(0,
                       sda=machine.Pin(config.I2C_SDA),
                       scl=machine.Pin(config.I2C_SCL),
                       freq=400_000)

    # I2C-Geräte scannen
    devices = i2c.scan()
    hex_devs = [hex(d) for d in devices]
    print(f"[INIT] I2C Geräte: {hex_devs}")

    print("[INIT] Display...")
    # WICHTIG: I2C-Bus explizit mitgeben, damit der TCA9554-GPIO-Expander für
    # den Hardware-Reset des Displays ordentlich angesprochen werden kann!
    display = Display(i2c=i2c)
    display.init()
    display.backlight(config.BL_BRIGHTNESS)
    print("[INIT] Display OK ✓")

    print("[INIT] RTC...")
    rtc = RTC(i2c)
    print(f"[INIT] RTC OK ✓ — Zeit: {rtc.datetime()}")

    print("[INIT] IMU...")
    imu = IMU(i2c)
    print(f"[INIT] IMU OK ✓ — Chip ID: {hex(imu.chip_id())}")

    gc.collect()
    print(f"[INIT] RAM frei nach Init: {gc.mem_free() // 1024} KB")

    return display, i2c, rtc, imu


# Zustände für die State-Machine
STATE_BOOT_SCREEN = 0
STATE_WATCH_FACE  = 1

def run_watch(display, rtc, imu, btn_boot, audio=None):
    """Haupt-Watch-Loop mit State-Machine."""
    from display.watch_face import WatchFace

    face = WatchFace(display, rtc, imu, config)
    
    print("[WATCH] Zeige Boot Screen...")
    face.draw_boot_screen()

    print("[WATCH] Warte auf BOOT Button...")
    
    state = STATE_BOOT_SCREEN
    last_update = 0
    tick = 0

    # Button Debouncing Variablen
    btn_last_state = 1
    btn_last_press_time = 0

    while True:
        now = time.ticks_ms()
        
        # --- BUTTON DEBOUNCING LOGIK ---
        btn_state = btn_boot.value()
        btn_pressed = False
        
        # Flankenerkennung: Wechsel von High (1) auf Low (0) = Gedrückt
        if btn_state == 0 and btn_last_state == 1:
            if time.ticks_diff(now, btn_last_press_time) > 250: # 250ms Entprellung
                btn_pressed = True
                btn_last_press_time = now
        btn_last_state = btn_state

        # --- STATE MACHINE ---
        if state == STATE_BOOT_SCREEN:
            if btn_pressed:
                print("[WATCH] BOOT Button gedrückt -> Wechsele zum Ziffernblatt!")
                # Vorbereitung für Watch Face
                face._last_dt = None # Erzwinge komplettes Redraw
                face.draw_background()
                face.update()
                state = STATE_WATCH_FACE
            else:
                # High-FPS Floating Arc Reactor Animation mit dynamischem Sound
                face.animate_boot_screen(audio=audio)
                time.sleep_ms(1) 
                
        elif state == STATE_WATCH_FACE:
            # Display-Update (jede Sekunde)
            if time.ticks_diff(now, last_update) >= 1000:
                face.update()
                last_update = now
                tick += 1

            # GC alle 60 Sekunden
            if tick % 60 == 0 and tick > 0:
                gc.collect()

            # Zukünftig: Hier können Button-Eingaben für Menüs im Watch-State verarbeitet werden
            if btn_pressed:
                print("[WATCH] Knopf im Uhr-Modus gedrückt!")
                # Beispiel: Animation, App-Wechsel etc.

            time.sleep_ms(50)


def main():
    from audio.driver import Audio
    startup_banner()

    try:
        # Initialisiere Hardware und Buttons
        display, i2c, rtc, imu = init_hardware()
        
        # Startup Ping (0.1s Jarvis Beep)
        try:
            audio = Audio(rate=44100, i2c=i2c)
            audio.play_sine(freq=880, duration_ms=100, volume=0.5)
            #audio.deinit()
        except Exception as e:
            print(f"[AUDIO] Startup-Ping fehlgeschlagen: {e}")
        
        # BOOT Button (GPIO 0, internes Pull-up oft physikalisch schon vorhanden, PULL_UP sicherheitshalber aktivieren)
        btn_boot = machine.Pin(config.BTN_BOOT, machine.Pin.IN, machine.Pin.PULL_UP)
        print("[INIT] BOOT-Button auf GPIO 0 initialisiert.")
        
        # Starte State-Machine (jetzt mit Audio-Pass-through)
        run_watch(display, rtc, imu, btn_boot, audio=audio)

    except KeyboardInterrupt:
        print("\n[WATCH] Gestoppt (Ctrl+C)")

    except Exception as e:
        import sys
        print(f"[FEHLER] {type(e).__name__}: {e}")
        sys.print_exception(e)

        # Fehlermeldung auf Display
        try:
            display.fill(0x0000)
            display.text("ERROR!", 140, 170, 0xF800)
            display.show()
        except:
            pass

        # Nach Fehler neu starten
        time.sleep(5)
        machine.reset()


if __name__ == "__main__":
    main()
