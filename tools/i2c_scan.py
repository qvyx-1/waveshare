import machine

i2c = machine.I2C(0, sda=machine.Pin(6), scl=machine.Pin(7), freq=400000)
devs = i2c.scan()
names = {0x51: 'PCF85063 RTC', 0x6B: 'QMI8658 IMU', 0x20: 'TCA9554 GPIO-Exp', 0x6A: 'QMI8658 IMU (alt)'}
print('I2C Geraete:')
for d in devs:
    print('  0x{:02X} = {}'.format(d, names.get(d, 'Unbekannt')))
print('Gesamt:', len(devs))
