# IMU-Treiber für QMI8658 (6-Achsen: Gyro + Accel)
# Waveshare ESP32-S3-LCD-1.85

import machine
import time
import math


class IMU:
    """
    Treiber für den QMI8658A 6-Achsen-IMU (Gyroscope + Accelerometer).
    I2C-Adresse: 0x6B (CS=High) oder 0x6A (CS=Low)
    
    Auflösung:
    - Accelerometer: ±2g, ±4g, ±8g, ±16g
    - Gyroscope: ±16, ±32, ±64, ±128, ±256, ±512, ±1024, ±2048 dps
    """

    ADDR = 0x6B

    # Register
    REG_WHO_AM_I   = 0x00   # Chip ID (sollte 0x05 sein)
    REG_REVISION   = 0x01
    REG_CTRL1      = 0x02   # SPI/I2C Konfiguration
    REG_CTRL2      = 0x03   # Accelerometer Einstellungen
    REG_CTRL3      = 0x04   # Gyroscope Einstellungen
    REG_CTRL5      = 0x06   # Low-pass Filter
    REG_CTRL7      = 0x08   # Enable-Register
    REG_CTRL8      = 0x09   # Reset + andere
    REG_STATUS0    = 0x2E   # Sensor Data Available
    REG_STATUS1    = 0x2F
    REG_TEMP_L     = 0x33
    REG_TEMP_H     = 0x34
    REG_AX_L       = 0x35
    REG_AX_H       = 0x36
    REG_AY_L       = 0x37
    REG_AY_H       = 0x38
    REG_AZ_L       = 0x39
    REG_AZ_H       = 0x3A
    REG_GX_L       = 0x3B
    REG_GX_H       = 0x3C
    REG_GY_L       = 0x3D
    REG_GY_H       = 0x3E
    REG_GZ_L       = 0x3F
    REG_GZ_H       = 0x40

    # Accelerometer Skalierung (bei ±4g Einstellung)
    ACCEL_SCALE = 4.0 / 32768.0  # g pro LSB

    # Gyroscope Skalierung (bei ±512 dps)
    GYRO_SCALE  = 512.0 / 32768.0  # dps pro LSB

    def __init__(self, i2c):
        self.i2c = i2c
        self._verify()
        self._init_sensor()

        # Schrittzähler
        self._steps = 0
        self._last_accel_mag = 0

    def _verify(self):
        """Chip-ID prüfen."""
        chip_id = self._read_reg(self.REG_WHO_AM_I)
        if chip_id != 0x05:
            raise RuntimeError(f"QMI8658 nicht gefunden! Chip-ID: 0x{chip_id:02X} (erwartet: 0x05)")
        print(f"[IMU] QMI8658 gefunden, Revision: {self._read_reg(self.REG_REVISION)}")

    def _read_reg(self, reg, n=1):
        data = self.i2c.readfrom_mem(self.ADDR, reg, n)
        return data[0] if n == 1 else data

    def _write_reg(self, reg, val):
        self.i2c.writeto_mem(self.ADDR, reg, bytes([val]))

    def _init_sensor(self):
        """Sensor initialisieren."""
        # Reset
        self._write_reg(self.REG_CTRL8, 0xB0)
        time.sleep_ms(10)

        # I2C Modus, 4-wire
        self._write_reg(self.REG_CTRL1, 0x40)

        # Accel: ±4g, ODR 58.83 Hz
        self._write_reg(self.REG_CTRL2, 0x15)

        # Gyro: ±512 dps, ODR 58.83 Hz
        self._write_reg(self.REG_CTRL3, 0x75)

        # Low-pass Filter aktivieren
        self._write_reg(self.REG_CTRL5, 0x11)

        # Accel + Gyro aktivieren
        self._write_reg(self.REG_CTRL7, 0x03)

        time.sleep_ms(30)

    def chip_id(self):
        return self._read_reg(self.REG_WHO_AM_I)

    def _read_int16(self, reg_l, reg_h):
        """Zwei Register als vorzeichenbehafteten 16-bit Int lesen."""
        raw = self._read_reg(reg_l, 2)
        val = (raw[1] << 8) | raw[0]
        if val > 32767:
            val -= 65536
        return val

    def accel(self):
        """
        Beschleunigung lesen.
        Gibt zurück: (ax, ay, az) in g
        """
        ax = self._read_int16(self.REG_AX_L, self.REG_AX_H) * self.ACCEL_SCALE
        ay = self._read_int16(self.REG_AY_L, self.REG_AY_H) * self.ACCEL_SCALE
        az = self._read_int16(self.REG_AZ_L, self.REG_AZ_H) * self.ACCEL_SCALE
        return (ax, ay, az)

    def gyro(self):
        """
        Drehrate lesen.
        Gibt zurück: (gx, gy, gz) in dps (Grad pro Sekunde)
        """
        gx = self._read_int16(self.REG_GX_L, self.REG_GX_H) * self.GYRO_SCALE
        gy = self._read_int16(self.REG_GY_L, self.REG_GY_H) * self.GYRO_SCALE
        gz = self._read_int16(self.REG_GZ_L, self.REG_GZ_H) * self.GYRO_SCALE
        return (gx, gy, gz)

    def temperature(self):
        """Chip-Temperatur in °C."""
        raw_l = self._read_reg(self.REG_TEMP_L)
        raw_h = self._read_reg(self.REG_TEMP_H)
        temp = (raw_h << 8) | raw_l
        return temp / 256.0

    def tilt_angles(self):
        """
        Neigungswinkel aus Accelerometer berechnen.
        Gibt zurück: (roll, pitch) in Grad
        """
        ax, ay, az = self.accel()
        roll  = math.atan2(ay, az) * 180 / math.pi
        pitch = math.atan2(-ax, math.sqrt(ay*ay + az*az)) * 180 / math.pi
        return (roll, pitch)

    def compass_heading(self):
        """
        Vereinfachte Kompass-Richtung aus Gyro (ohne Magnetometer).
        Nur als Referenz — für echten Kompass wäre ein Magnetometer nötig.
        """
        ax, ay, _ = self.accel()
        heading = math.atan2(ay, ax) * 180 / math.pi
        if heading < 0:
            heading += 360
        return heading

    def count_steps(self):
        """
        Einfacher Peak-Detection Schrittzähler.
        Zählt Schritte basierend auf Accel-Magnitude-Peaks.
        """
        ax, ay, az = self.accel()
        magnitude = math.sqrt(ax*ax + ay*ay + az*az)

        # Peak detection — Threshold bei 1.2g
        if magnitude > 1.2 and self._last_accel_mag <= 1.2:
            self._steps += 1

        self._last_accel_mag = magnitude
        return self._steps

    def reset_steps(self):
        """Schrittzähler zurücksetzen."""
        self._steps = 0

    @property
    def steps(self):
        return self._steps
