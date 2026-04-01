# RTC-Treiber für PCF85063 (I2C)
# Onboard-RTC des Waveshare ESP32-S3-LCD-1.85

import machine


class RTC:
    """
    Treiber für den PCF85063A Real-Time Clock Chip.
    I2C-Adresse: 0x51
    Unterstützt: Datum, Uhrzeit, Alarm
    """

    ADDR = 0x51

    # Register
    REG_CTRL1   = 0x00
    REG_CTRL2   = 0x01
    REG_SECONDS = 0x04
    REG_MINUTES = 0x05
    REG_HOURS   = 0x06
    REG_DAYS    = 0x07
    REG_WEEKDAYS = 0x08
    REG_MONTHS  = 0x09
    REG_YEARS   = 0x0A

    DAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

    def __init__(self, i2c):
        self.i2c = i2c
        self._verify()

    def _verify(self):
        """Prüft ob der Chip erreichbar ist."""
        devices = self.i2c.scan()
        if self.ADDR not in devices:
            raise RuntimeError(f"PCF85063 nicht gefunden! (Adresse 0x{self.ADDR:02X})")

    @staticmethod
    def _bcd_to_int(bcd):
        return (bcd >> 4) * 10 + (bcd & 0x0F)

    @staticmethod
    def _int_to_bcd(val):
        return ((val // 10) << 4) | (val % 10)

    def _read_reg(self, reg, n=1):
        return self.i2c.readfrom_mem(self.ADDR, reg, n)

    def _write_reg(self, reg, data):
        if isinstance(data, int):
            data = bytes([data])
        self.i2c.writeto_mem(self.ADDR, reg, data)

    def datetime(self):
        """
        Aktuelle Zeit und Datum auslesen.
        Gibt zurück: (year, month, day, weekday, hour, minute, second)
        """
        data = self._read_reg(self.REG_SECONDS, 7)
        second  = self._bcd_to_int(data[0] & 0x7F)
        minute  = self._bcd_to_int(data[1] & 0x7F)
        hour    = self._bcd_to_int(data[2] & 0x3F)
        day     = self._bcd_to_int(data[3] & 0x3F)
        weekday = data[4] & 0x07
        month   = self._bcd_to_int(data[5] & 0x1F)
        year    = self._bcd_to_int(data[6]) + 2000
        return (year, month, day, weekday, hour, minute, second)

    def set_datetime(self, year, month, day, weekday, hour, minute, second):
        """Datum und Uhrzeit setzen."""
        buf = bytes([
            self._int_to_bcd(second),
            self._int_to_bcd(minute),
            self._int_to_bcd(hour),
            self._int_to_bcd(day),
            weekday & 0x07,
            self._int_to_bcd(month),
            self._int_to_bcd(year - 2000),
        ])
        self._write_reg(self.REG_SECONDS, buf)

    def time_string(self):
        """Zeit als formatierter String: HH:MM:SS"""
        dt = self.datetime()
        return f"{dt[4]:02d}:{dt[5]:02d}:{dt[6]:02d}"

    def date_string(self):
        """Datum als String: DD.MM.YYYY"""
        dt = self.datetime()
        return f"{dt[2]:02d}.{dt[1]:02d}.{dt[0]}"

    def weekday_str(self):
        """Wochentag als Kürzel."""
        dt = self.datetime()
        return self.DAYS[dt[3] % 7]

    def sync_from_ntp(self, ssid=None, password=None):
        """
        Zeit via NTP synchronisieren (benötigt WiFi-Verbindung).
        Falls ssid angegeben, wird WiFi zuerst verbunden.
        """
        import network
        import ntptime
        import time

        if ssid:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            if not wlan.isconnected():
                wlan.connect(ssid, password)
                timeout = 10
                while not wlan.isconnected() and timeout > 0:
                    time.sleep(1)
                    timeout -= 1
                if not wlan.isconnected():
                    raise RuntimeError("WiFi-Verbindung fehlgeschlagen")

        ntptime.settime()
        t = time.localtime()
        self.set_datetime(t[0], t[1], t[2], t[6], t[3], t[4], t[5])
        print(f"[RTC] NTP sync: {self.date_string()} {self.time_string()}")
