# Display-Treiber für ST7701 (360x360 LCD)
# Waveshare ESP32-S3-LCD-1.85

import machine
import time


class Display:
    """
    Treiber für den ST7701 LCD-Controller auf dem ESP32-S3-LCD-1.85.
    Interface: SPI (4-wire)
    
    Der ESP32-S3 kommuniziert mit dem ST7701 über SPI.
    Der ST7701 ist ein RGB/SPI-LCD-Controller für 16M-Farb-Displays.
    """

    # ST7701 Kommandos
    CMD_SWRESET = 0x01   # Software Reset
    CMD_SLPOUT  = 0x11   # Sleep Out
    CMD_NORON   = 0x13   # Normal Display Mode On
    CMD_DISPON  = 0x29   # Display On
    CMD_DISPOFF = 0x28   # Display Off
    CMD_CASET   = 0x2A   # Column Address Set
    CMD_RASET   = 0x2B   # Row Address Set
    CMD_RAMWR   = 0x2C   # Memory Write
    CMD_COLMOD  = 0x3A   # Pixel Format Set
    CMD_MADCTL  = 0x36   # Memory Data Access Control
    CMD_SLPIN   = 0x10   # Sleep In

    # RGB565 Farben
    BLACK   = 0x0000
    WHITE   = 0xFFFF
    RED     = 0xF800
    GREEN   = 0x07E0
    BLUE    = 0x001F
    YELLOW  = 0xFFE0
    CYAN    = 0x07FF
    MAGENTA = 0xF81F
    ORANGE  = 0xFC00

    def __init__(self, cs=12, clk=13, mosi=11, dc=4, rst=5, bl=38,
                 width=360, height=360, spi_id=1, baudrate=40_000_000):
        self.width  = width
        self.height = height
        self._dc  = machine.Pin(dc,  machine.Pin.OUT)
        self._rst = machine.Pin(rst, machine.Pin.OUT)
        self._bl  = machine.Pin(bl,  machine.Pin.OUT)
        self._cs  = machine.Pin(cs,  machine.Pin.OUT)

        # SPI initialisieren
        self._spi = machine.SPI(spi_id,
                                baudrate=baudrate,
                                polarity=0,
                                phase=0,
                                bits=8,
                                firstbit=machine.SPI.MSB,
                                sck=machine.Pin(clk),
                                mosi=machine.Pin(mosi))

        # Backlight über Timer-PWM
        self._bl_pwm = machine.PWM(self._bl, freq=1000, duty=0)

        # Framebuffer (optional — bei genug RAM)
        # 360*360*2 = ~259KB — benötigt PSRAM!
        self._buf = None

    def _write_cmd(self, cmd):
        self._dc.value(0)
        self._cs.value(0)
        self._spi.write(bytes([cmd]))
        self._cs.value(1)

    def _write_data(self, data):
        self._dc.value(1)
        self._cs.value(0)
        if isinstance(data, int):
            self._spi.write(bytes([data]))
        else:
            self._spi.write(bytes(data))
        self._cs.value(1)

    def _write_data16(self, val):
        """16-bit Wert senden (Hi-Byte zuerst)."""
        self._dc.value(1)
        self._cs.value(0)
        self._spi.write(bytes([val >> 8, val & 0xFF]))
        self._cs.value(1)

    def hardware_reset(self):
        """Hardware-Reset durchführen."""
        self._rst.value(1)
        time.sleep_ms(10)
        self._rst.value(0)
        time.sleep_ms(50)
        self._rst.value(1)
        time.sleep_ms(120)

    def init(self):
        """Display initialisieren und konfigurieren."""
        self.hardware_reset()

        # ST7701 Initialisierungssequenz für 360x360
        self._write_cmd(self.CMD_SWRESET)
        time.sleep_ms(150)

        self._write_cmd(self.CMD_SLPOUT)
        time.sleep_ms(120)

        # Pixel-Format: 16-bit RGB565
        self._write_cmd(self.CMD_COLMOD)
        self._write_data(0x55)   # 0x55 = 16-bit/pixel

        # Speicherzugriff-Kontrolle (Orientierung)
        self._write_cmd(self.CMD_MADCTL)
        self._write_data(0x00)   # Normal orientation

        # Display einschalten
        self._write_cmd(self.CMD_NORON)
        time.sleep_ms(10)
        self._write_cmd(self.CMD_DISPON)
        time.sleep_ms(50)

        print("[DISPLAY] Init abgeschlossen")

    def backlight(self, duty=512):
        """Backlight-Helligkeit setzen (0-1023)."""
        duty = max(0, min(1023, duty))
        self._bl_pwm.duty(duty)

    def set_window(self, x0, y0, x1, y1):
        """Schreibfenster setzen."""
        self._write_cmd(self.CMD_CASET)
        self._write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])

        self._write_cmd(self.CMD_RASET)
        self._write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])

        self._write_cmd(self.CMD_RAMWR)

    def pixel(self, x, y, color):
        """Einzelnen Pixel setzen."""
        self.set_window(x, y, x, y)
        self._write_data16(color)

    def fill(self, color):
        """Gesamtes Display mit Farbe füllen."""
        self.set_window(0, 0, self.width - 1, self.height - 1)
        # In Blöcken senden (RAM-schonend)
        chunk = bytearray(256 * 2)
        hi = color >> 8
        lo = color & 0xFF
        for i in range(0, len(chunk), 2):
            chunk[i]   = hi
            chunk[i+1] = lo
        total_pixels = self.width * self.height
        full_chunks  = total_pixels // 256
        remainder    = total_pixels % 256
        self._dc.value(1)
        self._cs.value(0)
        for _ in range(full_chunks):
            self._spi.write(chunk)
        if remainder:
            self._spi.write(chunk[:remainder * 2])
        self._cs.value(1)

    def hline(self, x, y, w, color):
        """Horizontale Linie."""
        self.set_window(x, y, x + w - 1, y)
        buf = bytes([color >> 8, color & 0xFF]) * w
        self._dc.value(1)
        self._cs.value(0)
        self._spi.write(buf)
        self._cs.value(1)

    def vline(self, x, y, h, color):
        """Vertikale Linie."""
        for row in range(h):
            self.pixel(x, y + row, color)

    def rect(self, x, y, w, h, color):
        """Rechteck zeichnen (nur Rahmen)."""
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)

    def fill_rect(self, x, y, w, h, color):
        """Gefülltes Rechteck."""
        self.set_window(x, y, x + w - 1, y + h - 1)
        buf = bytes([color >> 8, color & 0xFF]) * w
        self._dc.value(1)
        self._cs.value(0)
        for _ in range(h):
            self._spi.write(buf)
        self._cs.value(1)

    def circle(self, cx, cy, r, color, filled=False):
        """Kreis zeichnen (Bresenham-Algorithmus)."""
        x, y, err = 0, r, 1 - r
        while x <= y:
            if filled:
                self.hline(cx - x, cy + y, 2 * x + 1, color)
                self.hline(cx - x, cy - y, 2 * x + 1, color)
                self.hline(cx - y, cy + x, 2 * y + 1, color)
                self.hline(cx - y, cy - x, 2 * y + 1, color)
            else:
                for px, py in [(cx+x, cy+y), (cx-x, cy+y),
                                (cx+x, cy-y), (cx-x, cy-y),
                                (cx+y, cy+x), (cx-y, cy+x),
                                (cx+y, cy-x), (cx-y, cy-x)]:
                    self.pixel(px, py, color)
            if err < 0:
                err += 2 * x + 3
            else:
                err += 2 * (x - y) + 5
                y -= 1
            x += 1

    def text(self, string, x, y, color, bg=None, size=1):
        """
        Einfache 8x8 Textausgabe (benötigt framebuf).
        Für bessere Fonts: externes Font-Modul verwenden.
        """
        try:
            import framebuf
            # Einfacher 8x8 Zeichensatz via framebuf
            w = len(string) * 8 * size
            h = 8 * size
            buf = bytearray(w * h * 2)
            fb = framebuf.FrameBuffer(buf, w, h, framebuf.RGB565)
            if bg is not None:
                fb.fill(bg)
            fb.text(string, 0, 0, color)
            self.set_window(x, y, x + w - 1, y + h - 1)
            self._dc.value(1)
            self._cs.value(0)
            self._spi.write(buf)
            self._cs.value(1)
        except ImportError:
            print("[DISPLAY] framebuf nicht verfügbar")

    def show_bmp_buffer(self, buf, x=0, y=0, w=None, h=None):
        """Rohen RGB565-Puffer anzeigen."""
        w = w or self.width
        h = h or self.height
        self.set_window(x, y, x + w - 1, y + h - 1)
        self._dc.value(1)
        self._cs.value(0)
        self._spi.write(buf)
        self._cs.value(1)

    def off(self):
        """Display abschalten."""
        self._write_cmd(self.CMD_DISPOFF)
        self.backlight(0)

    def on(self):
        """Display einschalten."""
        self._write_cmd(self.CMD_DISPON)
        self.backlight(512)
