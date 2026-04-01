import time
import machine
import sys

# Damit der Import von config und display klappt, auch wenn es im root liegt
if '' not in sys.path:
    sys.path.insert(0, '')

from config import LCD_W, LCD_H, I2C_SCL, I2C_SDA, TOUCH_SCL, TOUCH_SDA
from display.driver import Display
from display.touch import TouchCST816S

print("=== SuperHero Watch: Touch Test ===")

# Gemeinsamer I2C Bus für Reset via TCA9554 und Sensoren
i2c_main = machine.I2C(0, scl=machine.Pin(I2C_SCL), sda=machine.Pin(I2C_SDA), freq=400_000)

# Eigener I2C Bus für Touch (laut Waveshare Schema getrennt!)
scl_pin = machine.Pin(TOUCH_SCL, machine.Pin.IN, machine.Pin.PULL_UP)
sda_pin = machine.Pin(TOUCH_SDA, machine.Pin.IN, machine.Pin.PULL_UP)
i2c_touch = machine.I2C(1, scl=scl_pin, sda=sda_pin, freq=400_000)

print("Main I2C Scanner:", [hex(a) for a in i2c_main.scan()])

print("Initialisiere Display (und wecke dabei den Touch-Controller auf!)...")
disp = Display(i2c=i2c_main)
disp.init()
disp.fill(disp.BLACK)
disp.text("Suche Touch...", 90, LCD_H//2, disp.YELLOW)
disp.text("(Bitte Display beruehren!)", 60, LCD_H//2 + 20, disp.YELLOW)
disp.show()

print("Scanne nun den Touch I2C Bus nach dem Hardware-Reset kontinuierlich...")

try:
    # Init I2C ohne explizite PULL_UPs (das Board hat vermutlich Hardware Pull-Ups)
    i2c_touch = machine.I2C(1, scl=machine.Pin(TOUCH_SCL), sda=machine.Pin(TOUCH_SDA), freq=100_000)
    
    while True:
        scanned = i2c_touch.scan()
        if scanned:
            print("Gefunden! Touch I2C Scanner:", [hex(a) for a in scanned])
            touch_addr = scanned[0]
            touch = TouchCST816S(i2c_touch, address=touch_addr)
            disp.fill(disp.BLACK)
            disp.text("Touch gefunden!", 90, LCD_H//2, disp.GREEN)
            disp.show()
            
            # Gehe in den Lese-Modus
            last_x, last_y = -1, -1
            while True:
                t = touch.read_touch()
                if t and t['pressed']:
                    x, y = t['x'], t['y']
                    if x != last_x or y != last_y:
                        print(f"Touch auf X={x}, Y={y} (Geste: {t['gesture']})")
                        disp.circle(x, y, 5, disp.RED, filled=True)
                        disp.show()
                        last_x, last_y = x, y
                    time.sleep_ms(10)
                else:
                    time.sleep_ms(50)
        else:
            print("Scanne... (bitte Display berühren, um ggf. aufzuwecken)")
            time.sleep_ms(500)
            
except KeyboardInterrupt:
    print("Test beendet.")
