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
    print(f"  ║   {config.HERO_NAME:<26s}  ║")
    print("  ╚══════════════════════════════╝")
    print()


def init_hardware():
    """Hardware-Module initialisieren."""
    from sensors.rtc import RTC
    from sensors.imu import IMU
    from display.driver import Display

    print("[INIT] Display...")
    display = Display()
    display.init()
    display.backlight(config.BL_DEFAULT_DUTY)
    print("[INIT] Display OK ✓")

    print("[INIT] I2C Bus...")
    i2c = machine.I2C(0,
                       sda=machine.Pin(config.I2C_SDA),
                       scl=machine.Pin(config.I2C_SCL),
                       freq=config.I2C_FREQ)

    # I2C-Geräte scannen
    devices = i2c.scan()
    hex_devs = [hex(d) for d in devices]
    print(f"[INIT] I2C Geräte: {hex_devs}")

    print("[INIT] RTC...")
    rtc = RTC(i2c)
    print(f"[INIT] RTC OK ✓ — Zeit: {rtc.datetime()}")

    print("[INIT] IMU...")
    imu = IMU(i2c)
    print(f"[INIT] IMU OK ✓ — Chip ID: {hex(imu.chip_id())}")

    gc.collect()
    print(f"[INIT] RAM frei nach Init: {gc.mem_free() // 1024} KB")

    return display, i2c, rtc, imu


def run_watch(display, rtc, imu):
    """Haupt-Watch-Loop."""
    from display.watch_face import WatchFace

    face = WatchFace(display, rtc, imu, config)
    face.draw_boot_screen()

    print("[WATCH] Starte SuperHero Watch Loop...")

    last_update = 0
    tick = 0

    while True:
        now = time.ticks_ms()

        # Display-Update (jede Sekunde)
        if time.ticks_diff(now, last_update) >= 1000:
            face.update()
            last_update = now
            tick += 1

        # GC alle 60 Sekunden
        if tick % 60 == 0 and tick > 0:
            gc.collect()

        time.sleep_ms(50)


def main():
    startup_banner()

    try:
        display, i2c, rtc, imu = init_hardware()
        run_watch(display, rtc, imu)

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
