# Display-Treiber für ST77916 (360x360 LCD)
# Waveshare ESP32-S3-LCD-1.85 Edition mit PSRAM Framebuffer
# v2.0 — Performance-Optimiert mit @micropython.native

import machine
import time
import framebuf
import micropython

# Lade Pins aus zentraler Konfig
try:
    from config import LCD_SDA0, LCD_SCK, LCD_CS, LCD_BL, LCD_W, LCD_H, I2C_SCL, I2C_SDA, TCA9554_ADDR
except ImportError:
    LCD_SDA0, LCD_SCK, LCD_CS, LCD_BL = 46, 40, 21, 5
    LCD_W, LCD_H = 360, 360
    I2C_SCL, I2C_SDA, TCA9554_ADDR = 10, 11, 0x20


@micropython.native
def color565(r, g, b):
    """RGB → RGB565 mit Byte-Swap für SPI-Übertragung."""
    c = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return (c >> 8) | ((c & 0xFF) << 8)


class Display:
    """
    Treiber für den ST77916 LCD-Controller auf dem ESP32-S3-LCD-1.85.
    Nutzt 1-wire SPI über QSPI-Hardwaredesign (D0 = MOSI).
    Eingebauter 259KB PSRAM Framebuffer (360x360 RGB565).
    
    v2.0: Performance-Optimiert
    - @micropython.native für häufig aufgerufene Methoden
    - Schnellere SPI-Baudrate (60MHz)
    - Optimierter show_region()
    """

    # Vordefinierte Farben (vorberechnet, kein Overhead zur Laufzeit)
    BLACK   = color565(0, 0, 0)
    WHITE   = color565(255, 255, 255)
    RED     = color565(255, 0, 0)
    GREEN   = color565(0, 255, 0)
    BLUE    = color565(0, 0, 255)
    YELLOW  = color565(255, 255, 0)
    CYAN    = color565(0, 255, 255)
    MAGENTA = color565(255, 0, 255)
    ORANGE  = color565(255, 165, 0)
    DARK_RED = color565(139, 0, 0)
    GREY    = color565(128, 128, 128)
    DARK_GREY = color565(40, 40, 40)

    def __init__(self, i2c=None):
        self.width = LCD_W
        self.height = LCD_H
        self.color565 = color565
        self._bl = machine.Pin(LCD_BL, machine.Pin.OUT, value=1)
        self._cs = machine.Pin(LCD_CS, machine.Pin.OUT, value=1)
        
        self._spi = None

        # I2C für Hardware-Reset via TCA9554
        if i2c is None:
            self._i2c = machine.I2C(0, scl=machine.Pin(I2C_SCL), sda=machine.Pin(I2C_SDA), freq=400_000)
        else:
            self._i2c = i2c
            
        # Puffer Allokation im PSRAM
        print("[DISPLAY] Allokiere 259KB Framebuffer im PSRAM...")
        self.buffer = bytearray(self.width * self.height * 2)
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)
        
        # Vorberechneter Write-Command Header
        self._write_cmd = b'\x02\x00\x2C\x00'

    def hardware_reset(self):
        """Reset via TCA9554 GPIO Expander (EXIO2 für LCD, EXIO0 für Touch)."""
        devs = self._i2c.scan()
        if TCA9554_ADDR in devs:
            self._i2c.writeto_mem(TCA9554_ADDR, 0x03, bytes([0x00]))
            self._i2c.writeto_mem(TCA9554_ADDR, 0x01, bytes([0xFF]))
            time.sleep_ms(10)
            # RST LOW für Touch (Bit 0) und LCD (Bit 2)
            mask = 0xFF & ~( (1<<0) | (1<<2) )
            self._i2c.writeto_mem(TCA9554_ADDR, 0x01, bytes([mask]))
            time.sleep_ms(50)
            self._i2c.writeto_mem(TCA9554_ADDR, 0x01, bytes([0xFF]))
            time.sleep_ms(120)
        else:
            print("[DISPLAY] WARNUNG: TCA9554 nicht gefunden! Reset übersprungen.")

    def _cmd(self, c, *args):
        """Sende Kommando im QSPI 1-1-1 Format."""
        buf = bytearray([0x02, 0x00, c, 0x00])
        for a in args:
            buf.append(a)
        self._cs.value(0)
        self._spi.write(buf)
        self._cs.value(1)

    def backlight(self, duty=1):
        """Hintergrundbeleuchtung ON/OFF. Für PWM: machine.PWM(Pin(5)) nutzen."""
        self._bl.value(1 if duty > 0 else 0)

    def init(self):
        """Init ST77916 Controller — vollständige Init-Sequenz."""
        self.hardware_reset()

        try:
            from config import LCD_SCK, LCD_SDA0
        except ImportError:
            LCD_SCK, LCD_SDA0 = 40, 46

        # SPI: 60MHz für bessere Performance (1-Wire Modus über QSPI D0)
        self._spi = machine.SPI(1, baudrate=60_000_000, polarity=0, phase=0,
                                bits=8, firstbit=machine.SPI.MSB,
                                sck=machine.Pin(LCD_SCK), mosi=machine.Pin(LCD_SDA0))

        self._cmd(0x36, 0x00)  # MADCTL: RGB Mode
        self._cmd(0x3A, 0x55)  # COLMOD 16-bit
        
        # Waveshare Custom Init Sequence
        self._cmd(0xF0, 0x28)
        self._cmd(0xF2, 0x28)
        self._cmd(0x73, 0xF0)
        self._cmd(0x7C, 0xD1)
        self._cmd(0x83, 0xE0)
        self._cmd(0x84, 0x61)
        self._cmd(0xF2, 0x82)
        self._cmd(0xF0, 0x00)
        self._cmd(0xF0, 0x01)
        self._cmd(0xF1, 0x01)
        self._cmd(0xB0, 0x56)
        self._cmd(0xB1, 0x4D)
        self._cmd(0xB2, 0x24)
        self._cmd(0xB4, 0x87)
        self._cmd(0xB5, 0x44)
        self._cmd(0xB6, 0x8B)
        self._cmd(0xB7, 0x40)
        self._cmd(0xB8, 0x86)
        self._cmd(0xBA, 0x00)
        self._cmd(0xBB, 0x08)
        self._cmd(0xBC, 0x08)
        self._cmd(0xBD, 0x00)
        self._cmd(0xC0, 0x80)
        self._cmd(0xC1, 0x10)
        self._cmd(0xC2, 0x37)
        self._cmd(0xC3, 0x80)
        self._cmd(0xC4, 0x10)
        self._cmd(0xC5, 0x37)
        self._cmd(0xC6, 0xA9)
        self._cmd(0xC7, 0x41)
        self._cmd(0xC8, 0x01)
        self._cmd(0xC9, 0xA9)
        self._cmd(0xCA, 0x41)
        self._cmd(0xCB, 0x01)
        self._cmd(0xD0, 0x91)
        self._cmd(0xD1, 0x68)
        self._cmd(0xD2, 0x68)
        
        self._cmd(0xF5, 0x00, 0xA5)
        self._cmd(0xDD, 0x4F)
        self._cmd(0xDE, 0x4F)
        self._cmd(0xF1, 0x10)
        self._cmd(0xF0, 0x00)
        self._cmd(0xF0, 0x02)
        
        self._cmd(0xE0, 0xF0, 0x0A, 0x10, 0x09, 0x09, 0x36, 0x35, 0x33, 0x4A, 0x29, 0x15, 0x15, 0x2E, 0x34)
        self._cmd(0xE1, 0xF0, 0x0A, 0x0F, 0x08, 0x08, 0x05, 0x34, 0x33, 0x4A, 0x39, 0x15, 0x15, 0x2D, 0x33)
        self._cmd(0xF0, 0x10)
        self._cmd(0xF3, 0x10)
        self._cmd(0xE0, 0x07)
        self._cmd(0xE1, 0x00)
        self._cmd(0xE2, 0x00)
        self._cmd(0xE3, 0x00)
        self._cmd(0xE4, 0xE0)
        self._cmd(0xE5, 0x06)
        self._cmd(0xE6, 0x21)
        self._cmd(0xE7, 0x01)
        self._cmd(0xE8, 0x05)
        self._cmd(0xE9, 0x02)
        self._cmd(0xEA, 0xDA)
        self._cmd(0xEB, 0x00)
        self._cmd(0xEC, 0x00)
        self._cmd(0xED, 0x0F)
        self._cmd(0xEE, 0x00)
        self._cmd(0xEF, 0x00)
        
        for p in [0xF8, 0xF9, 0xFA, 0xFB, 0xFC, 0xFD, 0xFE, 0xFF]:
            self._cmd(p, 0x00)
            
        self._cmd(0x60, 0x40)
        self._cmd(0x61, 0x04)
        self._cmd(0x62, 0x00)
        self._cmd(0x63, 0x42)
        self._cmd(0x64, 0xD9)
        self._cmd(0x65, 0x00)
        self._cmd(0x66, 0x00)
        self._cmd(0x67, 0x00)
        self._cmd(0x68, 0x00)
        self._cmd(0x69, 0x00)
        self._cmd(0x6A, 0x00)
        self._cmd(0x6B, 0x00)
        
        self._cmd(0x70, 0x40)
        self._cmd(0x71, 0x03)
        self._cmd(0x72, 0x00)
        self._cmd(0x73, 0x42)
        self._cmd(0x74, 0xD8)
        self._cmd(0x75, 0x00)
        self._cmd(0x76, 0x00)
        self._cmd(0x77, 0x00)
        self._cmd(0x78, 0x00)
        self._cmd(0x79, 0x00)
        self._cmd(0x7A, 0x00)
        self._cmd(0x7B, 0x00)
        
        self._cmd(0x80, 0x48)
        self._cmd(0x81, 0x00)
        self._cmd(0x82, 0x06)
        self._cmd(0x83, 0x02)
        self._cmd(0x84, 0xD6)
        self._cmd(0x85, 0x04)
        self._cmd(0x86, 0x00)
        self._cmd(0x87, 0x00)
        
        self._cmd(0x88, 0x48)
        self._cmd(0x89, 0x00)
        self._cmd(0x8A, 0x08)
        self._cmd(0x8B, 0x02)
        self._cmd(0x8C, 0xD8)
        self._cmd(0x8D, 0x04)
        self._cmd(0x8E, 0x00)
        self._cmd(0x8F, 0x00)
        
        self._cmd(0x90, 0x48)
        self._cmd(0x91, 0x00)
        self._cmd(0x92, 0x0A)
        self._cmd(0x93, 0x02)
        self._cmd(0x94, 0xDA)
        self._cmd(0x95, 0x04)
        self._cmd(0x96, 0x00)
        self._cmd(0x97, 0x00)
        
        self._cmd(0x98, 0x48)
        self._cmd(0x99, 0x00)
        self._cmd(0x9A, 0x0C)
        self._cmd(0x9B, 0x02)
        self._cmd(0x9C, 0xDC)
        self._cmd(0x9D, 0x04)
        self._cmd(0x9E, 0x00)
        self._cmd(0x9F, 0x00)
        
        self._cmd(0xA0, 0x48)
        self._cmd(0xA1, 0x00)
        self._cmd(0xA2, 0x05)
        self._cmd(0xA3, 0x02)
        self._cmd(0xA4, 0xD5)
        self._cmd(0xA5, 0x04)
        self._cmd(0xA6, 0x00)
        self._cmd(0xA7, 0x00)
        
        self._cmd(0xA8, 0x48)
        self._cmd(0xA9, 0x00)
        self._cmd(0xAA, 0x07)
        self._cmd(0xAB, 0x02)
        self._cmd(0xAC, 0xD7)
        self._cmd(0xAD, 0x04)
        self._cmd(0xAE, 0x00)
        self._cmd(0xAF, 0x00)
        
        self._cmd(0xB0, 0x48)
        self._cmd(0xB1, 0x00)
        self._cmd(0xB2, 0x09)
        self._cmd(0xB3, 0x02)
        self._cmd(0xB4, 0xD9)
        self._cmd(0xB5, 0x04)
        self._cmd(0xB6, 0x00)
        self._cmd(0xB7, 0x00)
        
        self._cmd(0xB8, 0x48)
        self._cmd(0xB9, 0x00)
        self._cmd(0xBA, 0x0B)
        self._cmd(0xBB, 0x02)
        self._cmd(0xBC, 0xDB)
        self._cmd(0xBD, 0x04)
        self._cmd(0xBE, 0x00)
        self._cmd(0xBF, 0x00)
        
        self._cmd(0xC0, 0x10)
        self._cmd(0xC1, 0x47)
        self._cmd(0xC2, 0x56)
        self._cmd(0xC3, 0x65)
        self._cmd(0xC4, 0x74)
        self._cmd(0xC5, 0x88)
        self._cmd(0xC6, 0x99)
        self._cmd(0xC7, 0x01)
        self._cmd(0xC8, 0xBB)
        self._cmd(0xC9, 0xAA)
        
        self._cmd(0xD0, 0x10)
        self._cmd(0xD1, 0x47)
        self._cmd(0xD2, 0x56)
        self._cmd(0xD3, 0x65)
        self._cmd(0xD4, 0x74)
        self._cmd(0xD5, 0x88)
        self._cmd(0xD6, 0x99)
        self._cmd(0xD7, 0x01)
        self._cmd(0xD8, 0xBB)
        self._cmd(0xD9, 0xAA)
        
        self._cmd(0xF3, 0x01)
        self._cmd(0xF0, 0x00)
        
        self._cmd(0x21)  # INVERT ON
        self._cmd(0x11)  # Sleep Out
        time.sleep_ms(120)
        self._cmd(0x29)  # Display ON
        time.sleep_ms(20)

    @micropython.native
    def _set_window(self, x0, y0, x1, y1):
        self._cmd(0x2A, x0>>8, x0&0xFF, x1>>8, x1&0xFF)
        self._cmd(0x2B, y0>>8, y0&0xFF, y1>>8, y1&0xFF)

    @micropython.native
    def show(self):
        """Kopiert den gesamten Framebuffer zum Display."""
        self._set_window(0, 0, self.width-1, self.height-1)
        self._cs.value(0)
        self._spi.write(self._write_cmd)
        self._spi.write(self.buffer)
        self._cs.value(1)

    @micropython.native
    def show_region(self, x, y, w, h):
        """Kopiert nur einen Teilbereich des Framebuffers zum Display."""
        if x < 0 or y < 0 or (x + w) > self.width or (y + h) > self.height:
            return
            
        self._set_window(x, y, x + w - 1, y + h - 1)
        self._cs.value(0)
        self._spi.write(self._write_cmd)
        
        buf = self.buffer
        pitch = self.width * 2
        offset = y * pitch + x * 2
        line_len = w * 2
        
        for _ in range(h):
            self._spi.write(memoryview(buf)[offset : offset + line_len])
            offset += pitch
            
        self._cs.value(1)

    # --- Wrapper Methoden für Framebuf ---
    def fill(self, color):
        self.fb.fill(color)
        
    @micropython.native
    def pixel(self, x, y, color):
        self.fb.pixel(x, y, color)
        
    def hline(self, x, y, w, color):
        self.fb.hline(x, y, w, color)
        
    def vline(self, x, y, h, color):
        self.fb.vline(x, y, h, color)
        
    def rect(self, x, y, w, h, color):
        self.fb.rect(x, y, w, h, color)
        
    def fill_rect(self, x, y, w, h, color):
        self.fb.fill_rect(x, y, w, h, color)
        
    def text(self, string, x, y, color):
        self.fb.text(string, x, y, color)

    def ellipse(self, x, y, xr, yr, color, fill=False):
        self.fb.ellipse(x, y, xr, yr, color, fill)
        
    def circle(self, cx, cy, r, color, filled=False):
        self.ellipse(cx, cy, r, r, color, filled)

    def line(self, x0, y0, x1, y1, color):
        """Hardware-beschleunigte Linie via framebuf.line()."""
        self.fb.line(x0, y0, x1, y1, color)

    def load_bmp_background(self, filepath):
        """
        Laden und anzeigen einer BMP-Datei als Hintergrund.
        
        Unterstützt:
        - 24-bit RGB (uncompressed)
        - 320x320 oder andere Auflösungen (wird auf Displaygröße skaliert)
        
        Args:
            filepath: Pfad zur BMP-Datei (z.B. '/assets/bg.bmp')
            
        Returns:
            (bool, str): (success, message)
        """
        try:
            with open(filepath, 'rb') as f:
                # BMP Header lesen (14 Bytes)
                header = f.read(14)
                if header[:2] != b'BM':
                    return False, "Ungültiges BMP-Format"
                
                # DIB Header lesen (BITMAPINFOHEADER, 40 Bytes)
                dib_header = f.read(40)
                if len(dib_header) < 40:
                    return False, "BMP-Header zu kurz"
                
                # Parse DIB Header
                width = int.from_bytes(dib_header[4:8], 'little', signed=True)
                height = int.from_bytes(dib_header[8:12], 'little', signed=True)
                bit_count = int.from_bytes(dib_header[14:16], 'little')
                compression = int.from_bytes(dib_header[16:20], 'little')
                
                if compression != 0:
                    return False, f"Komprimierte BMPs nicht unterstützt: {compression}"
                
                if bit_count not in [24, 32]:
                    return False, f"Nur 24-bit RGB und 32-bit ARGB unterstützt, nicht {bit_count}-bit"
                
                # Pixeldaten-Offset aus File Header
                pixel_offset = int.from_bytes(header[10:14], 'little')
                
                # Zu Pixeldaten springen
                f.seek(pixel_offset)
                
                # BMP: Daten von unten nach oben und BGR statt RGB
                bytes_per_pixel = bit_count // 8
                row_size = ((width * bit_count + 31) // 32) * 4
                
                # Puffer für eine Zeile
                row_buffer = bytearray(row_size)
                
                # Framebuffer in Zielformat konvertieren
                fb_pixels = memoryview(self.buffer)
                fb_pitch = self.width * 2
                
                # Zielposition im Framebuffer (oben-links)
                dst_y = 0
                dst_x = 0
                
                # BMPs sind bottom-up, also müssen wir rückwärts lesen
                f.seek(pixel_offset + (height - 1) * row_size)
                
                for src_y in range(height):
                    # Nur bis zur Display-Höhe
                    if dst_y >= self.height:
                        break
                    
                    row_buffer = f.read(row_size)
                    
                    # Zeile in RGB565 konvertieren
                    for src_x in range(min(width, self.width)):
                        if src_x >= self.width:
                            break
                        
                        # BGR Bytes aus Datei (BMP ist BGR)
                        pixel_offset_in_row = src_x * bytes_per_pixel
                        b = row_buffer[pixel_offset_in_row]
                        g = row_buffer[pixel_offset_in_row + 1]
                        r = row_buffer[pixel_offset_in_row + 2]
                        
                        # RGB565 konvertieren (Byte-Swap für SPI)
                        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                        rgb565_swapped = (rgb565 & 0xFF) << 8 | (rgb565 >> 8)
                        
                        # In Framebuffer schreiben
                        fb_offset = dst_y * fb_pitch + src_x * 2
                        fb_pixels[fb_offset:fb_offset + 2] = rgb565_swapped.to_bytes(2, 'big')
                    
                    # Eine Zeile rückwärts (BMP ist bottom-up)
                    f.seek(pixel_offset + (height - src_y - 2) * row_size)
                    dst_y += 1
                
                return True, f"BMP geladen: {width}x{height} -> {self.width}x{self.height}"
                
        except FileNotFoundError:
            return False, f"Datei nicht gefunden: {filepath}"
        except Exception as e:
            return False, f"Fehler beim BMP-Laden: {e}"
