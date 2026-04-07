import time
import machine

class TouchCST816S:
    """
    Treiber für den kapazitiven Touch-Controller CST816S.
    Nutzt I2C Bus 1 (separater Bus vom Sensor-Bus!).
    
    Features:
    - Gesten-Erkennung (Swipe, Tap, Long-Press)
    - Async-kompatibel (non-blocking read)
    - Auto-Wake nach Display-Berührung
    """
    
    # I2C Adresse
    ADDRESS = 0x15

    # Register
    REG_GESTURE   = 0x01
    REG_FINGERNUM = 0x02
    REG_X_H       = 0x03
    REG_X_L       = 0x04
    REG_Y_H       = 0x05
    REG_Y_L       = 0x06
    REG_CHIP_ID   = 0xA7
    REG_FW_VER    = 0xA9

    # Gesten-Codes (CST816S Datenblatt)
    GESTURE_NONE       = 0x00
    GESTURE_SWIPE_UP   = 0x01
    GESTURE_SWIPE_DOWN = 0x02
    GESTURE_SWIPE_LEFT = 0x03
    GESTURE_SWIPE_RIGHT= 0x04
    GESTURE_SINGLE_TAP = 0x05
    GESTURE_DOUBLE_TAP = 0x0B
    GESTURE_LONG_PRESS = 0x0C

    def __init__(self, i2c=None, address=ADDRESS):
        """
        Initialisiert den Touch-Controller.
        
        Args:
            i2c: I2C Bus-Objekt (Bus 1 für Touch!)
                 Falls None, wird Bus 1 mit den Standard-Pins erstellt.
        """
        if i2c is None:
            from config import TOUCH_SCL, TOUCH_SDA
            self._i2c = machine.I2C(1,
                                     scl=machine.Pin(TOUCH_SCL),
                                     sda=machine.Pin(TOUCH_SDA),
                                     freq=400_000)
        else:
            self._i2c = i2c
        self.address = address
        self._available = False
        self._last_gesture = self.GESTURE_NONE
        self._last_x = 0
        self._last_y = 0

    def check(self):
        """Prüft, ob der Touch-Controller am I2C Bus antwortet."""
        devs = self._i2c.scan()
        self._available = self.address in devs
        if self._available:
            try:
                chip_id = self._i2c.readfrom_mem(self.address, self.REG_CHIP_ID, 1)[0]
                print(f"[TOUCH] CST816S gefunden, Chip-ID: 0x{chip_id:02X}")
            except:
                print("[TOUCH] CST816S gefunden (ID nicht lesbar)")
        return self._available

    @property
    def available(self):
        return self._available

    def read_touch(self):
        """
        Liest aktuelle Touch-Daten aus.
        
        Returns:
            dict mit keys: x, y, gesture, pressed
            None wenn kein Touch vorliegt oder Controller nicht verfügbar
        """
        if not self._available:
            # Versuche erneut zu scannen (Touch wacht bei Berührung auf)
            devs = self._i2c.scan()
            if self.address not in devs:
                return None
            self._available = True

        try:
            data = self._i2c.readfrom_mem(self.address, 0x00, 7)
            
            finger_num = data[self.REG_FINGERNUM] & 0x0F
            gesture = data[self.REG_GESTURE]
            
            if finger_num > 0:
                x = ((data[self.REG_X_H] & 0x0F) << 8) | data[self.REG_X_L]
                y = ((data[self.REG_Y_H] & 0x0F) << 8) | data[self.REG_Y_L]
                self._last_x = x
                self._last_y = y
                self._last_gesture = gesture
                return {
                    'x': x,
                    'y': y,
                    'gesture': gesture,
                    'pressed': True
                }
            return None
        except OSError:
            self._available = False
            return None

    def gesture_name(self, gesture_code=None):
        """Gibt den Namen einer Geste zurück."""
        if gesture_code is None:
            gesture_code = self._last_gesture
        names = {
            self.GESTURE_NONE: "NONE",
            self.GESTURE_SWIPE_UP: "SWIPE_UP",
            self.GESTURE_SWIPE_DOWN: "SWIPE_DOWN",
            self.GESTURE_SWIPE_LEFT: "SWIPE_LEFT",
            self.GESTURE_SWIPE_RIGHT: "SWIPE_RIGHT",
            self.GESTURE_SINGLE_TAP: "TAP",
            self.GESTURE_DOUBLE_TAP: "DOUBLE_TAP",
            self.GESTURE_LONG_PRESS: "LONG_PRESS",
        }
        return names.get(gesture_code, f"UNKNOWN(0x{gesture_code:02X})")
