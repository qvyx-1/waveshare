import time
import machine

print("\n--- TOUCH HARDWARE DEBUGGER ---")

# TCA9554 Setup
TCA9554_ADDR = 0x20
i2c0 = machine.I2C(0, scl=machine.Pin(10), sda=machine.Pin(11), freq=100000)

devs0 = i2c0.scan()
if TCA9554_ADDR in devs0:
    print("TCA9554 GPIO Expander gefunden auf Bus 0!")
    
    # 1. Configure pins 0 and 2 as outputs, rest as inputs maybe?
    # Config = 0: Output, 1: Input. Bit 0 (Touch), Bit 2 (LCD). 
    # Let's just set all to output for reset
    i2c0.writeto_mem(TCA9554_ADDR, 0x03, bytes([0x00]))
    
    # All HIGH
    i2c0.writeto_mem(TCA9554_ADDR, 0x01, bytes([0xFF]))
    time.sleep_ms(50)
    
    # Both LOW
    print("Pulling Touch-Reset (EXIO0) LOW...")
    i2c0.writeto_mem(TCA9554_ADDR, 0x01, bytes([0xFF & ~1])) 
    time.sleep_ms(50)
    
    # Both HIGH
    print("Pulling Touch-Reset (EXIO0) HIGH (Wakeup)...")
    i2c0.writeto_mem(TCA9554_ADDR, 0x01, bytes([0xFF]))
    time.sleep_ms(200)

print("\nScanning Touch Bus 1 (SCL=3, SDA=1)...")
# Try with pullups
scl = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
sda = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
try:
    i2c1 = machine.I2C(1, scl=scl, sda=sda, freq=100000)
    for _ in range(3):
        devs1 = i2c1.scan()
        print("SCL=3/SDA=1 ->", [hex(d) for d in devs1])
        if devs1:
            break
        time.sleep_ms(300)
except Exception as e:
    print("Fehler SCL=3/SDA=1:", e)

# Hard Reset via TCA9554 again
print("Pulling Touch-Reset (EXIO0) LOW...")
i2c0.writeto_mem(TCA9554_ADDR, 0x01, bytes([0xFF & ~1])) 
time.sleep_ms(50)
print("Pulling Touch-Reset (EXIO0) HIGH (Wakeup)...")
i2c0.writeto_mem(TCA9554_ADDR, 0x01, bytes([0xFF]))
time.sleep_ms(200)

print("\nScanning Touch Bus 1 (SCL=1, SDA=3 - SWAPPED)...")
scl = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
sda = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
try:
    i2c2 = machine.I2C(1, scl=scl, sda=sda, freq=100000)
    for _ in range(3):
        devs2 = i2c2.scan()
        print("SCL=1/SDA=3 ->", [hex(d) for d in devs2])
        if devs2:
            break
        time.sleep_ms(300)
except Exception as e:
    print("Fehler SCL=1/SDA=3:", e)

print("\nHardware Debugger: Teste Touch Interrupt Pin (GPIO 4)...")
touch_int = machine.Pin(4, machine.Pin.IN)

print("Bitte beruehre das Display mehrmals in den naechsten 10 Sekunden...")
initial_state = touch_int.value()
triggered = False

for _ in range(100): # 10 seconds total
    if touch_int.value() != initial_state:
        print("BINGO! Interrupt ausgelöst -> Touch Panel lebt!")
        triggered = True
        break
    time.sleep_ms(100)
    
if not triggered:
    print("Kein Hardware Interrupt auf GPIO 4 detektiert.")

print("\nHARDWARE DEBUGGER ENDE.")
