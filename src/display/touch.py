import time

class TouchCST816S:
    """
    Treiber für den kapazitiven Touch-Controller CST816S
    Nutzt I2C (geteilter Bus mit IMU und RTC).
    """
    
    # CST816S I2C Adresse (meist 0x15, manchmal reagiert das IC auf 0x5A)
    ADDRESS = 0x15

    # Register
    REG_GESTURE   = 0x00
    REG_FINGERNUM = 0x02
    REG_X_H       = 0x03
    REG_X_L       = 0x04
    REG_Y_H       = 0x05
    REG_Y_L       = 0x06

    # Gesten
    GESTURE_NONE       = 0x00
    GESTURE_SWIPE_UP   = 0x01
    GESTURE_SWIPE_DOWN = 0x02
    GESTURE_SWIPE_LEFT = 0x03
    GESTURE_SWIPE_RIGHT= 0x04
    GESTURE_SINGLE_TAP = 0x05
    GESTURE_DOUBLE_TAP = 0x0B
    GESTURE_LONG_PRESS = 0x0C

    def __init__(self, i2c, address=ADDRESS):
        self._i2c = i2c
        self.address = address
        
    def check(self):
        """Prüft, ob der Touch-Controller am I2C Bus antwortet."""
        devs = self._i2c.scan()
        if self.address in devs:
            return True
        return False

    def read_touch(self):
        """
        Liest aktuelle Touch-Daten aus.
        Gibt ein Dict zurück: {'x': x, 'y': y, 'gesture': gesture, 'pressed': bool}
        Gibt None zurück, wenn kein Touch vorliegt.
        """
        try:
            # Lese 7 Bytes ab Register 0x00
            data = self._i2c.readfrom_mem(self.address, 0x00, 7)
            
            finger_num = data[self.REG_FINGERNUM] & 0x0F
            gesture = data[self.REG_GESTURE]
            
            if finger_num > 0:
                x = ((data[self.REG_X_H] & 0x0F) << 8) | data[self.REG_X_L]
                y = ((data[self.REG_Y_H] & 0x0F) << 8) | data[self.REG_Y_L]
                return {
                    'x': x,
                    'y': y,
                    'gesture': gesture,
                    'pressed': True
                }
            return None
        except OSError:
            return None
