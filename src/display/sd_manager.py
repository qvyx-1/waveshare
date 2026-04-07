# SD-Karte Manager mit echtem SPI (TF-Card on Waveshare Board)
# Waveshare ESP32-S3-LCD-1.85
#
# SPI SD-Karte:
# - MISO: GPIO16
# - MOSI: GPIO17
# - SCK: GPIO14
# - CS: EXIO3 (über TCA9554 GPIO-Expander!)

import os
import gc
import struct
import machine
import time


class TCA9554Helper:
    """Helper zum Steuern von EXIO-Pins über TCA9554 GPIO-Expander."""
    
    TCA9554_ADDR = 0x20
    TCA9554_REG_OUTPUT = 0x01
    TCA9554_REG_CONFIG = 0x03
    
    def __init__(self, i2c):
        self.i2c = i2c
        self.output_state = 0xFF  # Alle Pins HIGH
    
    def set_exio_pin(self, pin, value):
        """Setze EXIO-Pin (0-7) auf HIGH/LOW."""
        if value:
            self.output_state |= (1 << pin)  # Bit setzen (HIGH)
        else:
            self.output_state &= ~(1 << pin)  # Bit löschen (LOW)
        
        self.i2c.writeto_mem(self.TCA9554_ADDR, self.TCA9554_REG_OUTPUT, 
                            bytes([self.output_state]))


class SDCardSPI:
    """SD-Karte über Hardware-SPI (echte TF-Card)."""
    
    # Pins (laut Waveshare Wiki)
    SD_SPI_MISO = 16   # GPIO16
    SD_SPI_MOSI = 17   # GPIO17
    SD_SPI_SCK = 14    # GPIO14
    SD_SPI_CS_EXIO = 3 # EXIO3 (via TCA9554)
    
    _instance = None
    
    def __init__(self, i2c=None):
        self.i2c = i2c
        self.spi = None
        self.expander = None
        self.mounted = False
        
        if i2c:
            self.expander = TCA9554Helper(i2c)
    
    @staticmethod
    def get_instance(i2c=None):
        """Singleton für SD-Karte."""
        if SDCardSPI._instance is None:
            SDCardSPI._instance = SDCardSPI(i2c)
        return SDCardSPI._instance
    
    def init(self):
        """Initialisiere SD-Karte über SPI."""
        try:
            print("[SD] Initialisiere TF-Card über SPI...")
            
            # SPI-Bus für SD
            self.spi = machine.SPI(
                1,  # SPI Bus 1
                baudrate=25_000_000,
                polarity=0,
                phase=0,
                bits=8,
                firstbit=machine.SPI.MSB,
                sck=machine.Pin(self.SD_SPI_SCK, machine.Pin.OUT),
                mosi=machine.Pin(self.SD_SPI_MOSI, machine.Pin.OUT),
                miso=machine.Pin(self.SD_SPI_MISO, machine.Pin.IN)
            )
            
            print("[SD] ✓ SPI-Bus initialisiert")
            
            # Versuche sdcard-Modul zu nutzen
            try:
                import sdcard
                import vfs
                print("[SD] sdcard-Modul gefunden")
                
                # CS-Pin über Expander steuern
                if self.expander:
                    self.expander.set_exio_pin(self.SD_SPI_CS_EXIO, 1)  # CS HIGH
                
                # Dummy CS für sdcard.SDCard()
                cs = machine.Pin(15, machine.Pin.OUT)
                cs.value(1)
                
                # SD-Karte initialisieren
                sd = sdcard.SDCard(self.spi, cs)
                
                # Filesystem mounten
                vfs.mount(sd, '/sd')
                
                self.mounted = True
                print("[SD] ✓ TF-Card gemountet auf /sd")
                
                # Zeige Dateien
                try:
                    files = os.listdir('/sd')
                    bmp_files = [f for f in files if f.lower().endswith('.bmp')]
                    print(f"[SD] {len(files)} Dateien, {len(bmp_files)} BMP-Dateien")
                    if bmp_files:
                        print(f"[SD] BMPs: {bmp_files}")
                except Exception as e:
                    print(f"[SD] Fehler beim Listieren: {e}")
                
                return True
            
            except ImportError as e:
                print(f"[SD] ⚠️  sdcard-Modul nicht verfügbar: {e}")
                print("[SD] (Das ist OK, BMP-Laden wird übersprungen)")
                return False
            except OSError as e:
                print(f"[SD] ⚠️  TF-Card nicht erkannt/gemountet: {e}")
                print("[SD] (Stelle sicher, dass eine Karte eingefügt ist)")
                return False
        
        except Exception as e:
            print(f"[SD] ✗ Fehler: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def list_files(self, path='/sd'):
        """Liste Dateien auf SD."""
        try:
            return os.listdir(path)
        except:
            return []
    
    def find_bmp(self, path='/sd'):
        """Finde BMP-Dateien auf SD."""
        try:
            files = os.listdir(path)
            return [f for f in files if f.lower().endswith('.bmp')]
        except:
            return []


class ColorTestPattern:
    """Farbverlaufs-Testbilder für Diagnose."""
    
    @staticmethod
    def create_horizontal_gradient(display):
        """
        Erstelle horizontalen Farbverlauf.
        WICHTIG: display.color565() für korrekten Byte-Swap verwenden!
        """
        print("[TEST] Erstelle horizontalen Regenbogen-Farbverlauf...")
        
        w = display.width
        h = display.height
        
        try:
            stripe_w = w // 6
            colors = [
                (255, 0, 0),      # Rot
                (255, 255, 0),    # Gelb
                (0, 255, 0),      # Grün
                (0, 255, 255),    # Cyan
                (0, 0, 255),      # Blau
                (255, 0, 255),    # Magenta
            ]
            
            for idx, (r, g, b) in enumerate(colors):
                # display.color565() macht den nötigen Byte-Swap!
                c = display.color565(r, g, b)
                display.fill_rect(idx * stripe_w, 0, stripe_w, h, c)
            
            print("[TEST] ✓ Farbverlauf erstellt")
            display.show()
            
        except Exception as e:
            print(f"[TEST] Fehler bei Gradient: {e}")
    
    @staticmethod
    def create_smooth_gradient(display):
        """Erstelle sanften HSV-Farbverlauf über das ganze Display."""
        print("[TEST] Erstelle sanften Farbverlauf...")
        
        w = display.width
        h = display.height
        
        try:
            for x in range(w):
                hue = (x * 360) // w
                
                if hue < 60:
                    r, g, b = 255, int(255 * hue / 60), 0
                elif hue < 120:
                    r, g, b = int(255 * (120 - hue) / 60), 255, 0
                elif hue < 180:
                    r, g, b = 0, 255, int(255 * (hue - 120) / 60)
                elif hue < 240:
                    r, g, b = 0, int(255 * (240 - hue) / 60), 255
                elif hue < 300:
                    r, g, b = int(255 * (hue - 240) / 60), 0, 255
                else:
                    r, g, b = 255, 0, int(255 * (360 - hue) / 60)
                
                # display.color565() für korrekten Byte-Swap
                c = display.color565(r, g, b)
                display.vline(x, 0, h, c)
                
                if (x % 40) == 0:
                    print(f"  [{x}/{w}]", end='\r')
            
            print()
            print("[TEST] ✓ Sanfter Farbverlauf erstellt")
            display.show()
        
        except Exception as e:
            print(f"[TEST] Fehler: {e}")

    
    @staticmethod
    def create_color_squares(display):
        """8 Farbquadrate für Farbdiagnose (2 Reihen x 4 Spalten)."""
        print("[TEST] Erstelle Farbdiagnose-Quadrate...")
        
        colors = [
            (0, 0, 0),        # Schwarz
            (255, 255, 255),  # Weiß
            (255, 0, 0),      # Rot
            (0, 255, 0),      # Grün
            (0, 0, 255),      # Blau
            (255, 255, 0),    # Gelb
            (0, 255, 255),    # Cyan
            (255, 0, 255),    # Magenta
        ]
        
        try:
            w = display.width
            h = display.height
            sq_w = w // 4
            sq_h = h // 2
            
            for idx, (r, g, b) in enumerate(colors):
                row = idx // 4
                col = idx % 4
                
                # display.color565() für korrekten Byte-Swap!
                c = display.color565(r, g, b)
                x = col * sq_w
                y = row * sq_h
                
                display.fill_rect(x, y, sq_w, sq_h, c)
            
            print("[TEST] ✓ Farbquadrate erstellt")
            display.show()
            
        except Exception as e:
            print(f"[TEST] Fehler bei Quadraten: {e}")


class BMPLoaderSD:
    """Schneller BMP-Loader von SD-Karte."""
    
    @staticmethod
    def load_bmp(filepath, display):
        """Lade BMP schnell von SD mit RGB565-Konvertierung."""
        try:
            print(f"[BMP] Lade {filepath}...")
            
            fb = display.buffer
            w_max = display.width
            h_max = display.height
            
            with open(filepath, 'rb') as f:
                # BMP Header
                header = f.read(14)
                if header[:2] != b'BM':
                    return False, "Keine BMP"
                
                dib = f.read(40)
                width = struct.unpack('<I', dib[4:8])[0]
                height = struct.unpack('<I', dib[8:12])[0]
                bitcount = struct.unpack('<H', dib[14:16])[0]
                
                if bitcount not in [24, 32]:
                    return False, f"Nur 24/32-Bit"
                
                pixoff = struct.unpack('<I', header[10:14])[0]
                bpp = bitcount // 8
                row_sz = ((width * bitcount + 31) // 32) * 4
                
                # BMP ist bottom-up
                f.seek(pixoff + (height - 1) * row_sz)
                
                w = min(width, w_max)
                h = min(height, h_max)
                
                print(f"[BMP] Konvertiere {w}x{h}...")
                
                for y in range(h):
                    row = f.read(row_sz)
                    if not row:
                        break
                    
                    for x in range(w):
                        px_off = x * bpp
                        b = row[px_off]
                        g = row[px_off + 1]
                        r = row[px_off + 2]
                        
                        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                        rgb565_s = ((rgb565 & 0xFF) << 8) | (rgb565 >> 8)
                        
                        fb_off = y * w_max * 2 + x * 2
                        fb[fb_off] = (rgb565_s >> 8) & 0xFF
                        fb[fb_off + 1] = rgb565_s & 0xFF
                    
                    if (y + 1) % 100 == 0:
                        print(f"  [{y+1}/{h}]", end='\r')
                    
                    if y < h - 1:
                        f.seek(pixoff + (height - y - 2) * row_sz)
                
                print()
                display.show()
                print(f"[BMP] ✓ {w}x{h}")
                gc.collect()
                return True, f"{w}x{h}"
        
        except Exception as e:
            return False, str(e)
