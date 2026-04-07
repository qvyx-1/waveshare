# Simplifizierter BMP Image Loader für SuperHero Watch
# Waveshare ESP32-S3-LCD-1.85
#
# Features:
# - BMP-Loading (24-bit RGB, 32-bit ARGB)
# - RGB565 conversion
# - Performance-optimiert für MicroPython

import gc
import struct
import micropython


class ImageLoader:
    """Asynchrone BMP-Loader für Display-Framebuffer."""

    _cache = {}
    _cache_enabled = True
    
    @staticmethod
    def clear_cache():
        """Cache leeren."""
        ImageLoader._cache.clear()
        gc.collect()

    @staticmethod
    @micropython.native
    def _color_rgb_to_rgb565(r, g, b):
        """RGB → RGB565 (Byte-Swapped für SPI)."""
        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        return (rgb565 & 0xFF) << 8 | (rgb565 >> 8)

    @staticmethod
    def load_bmp(filepath, target_buffer, target_width, target_height):
        """
        BMP-Datei laden in Framebuffer.
        
        Args:
            filepath: Pfad zu BMP ('/assets/bg.bmp')
            target_buffer: Ziel-Framebuffer (bytearray)
            target_width: Breite (360)
            target_height: Höhe (360)
            
        Returns:
            (bool, str): (success, message)
        """
        try:
            # Cache-Check
            if ImageLoader._cache_enabled and filepath in ImageLoader._cache:
                cache_entry = ImageLoader._cache[filepath]
                target_buffer[:] = cache_entry['data']
                return True, f"Aus Cache: {cache_entry['width']}x{cache_entry['height']}"
            
            # BMP öffnen
            with open(filepath, 'rb') as f:
                # File Header (14 bytes)
                header = f.read(14)
                if header[:2] != b'BM':
                    return False, "Kein BMP (Magic falsch)"
                
                # DIB Header (40 bytes)
                dib = f.read(40)
                if len(dib) < 40:
                    return False, "DIB Header zu kurz"
                
                # Parse DIB Header mit struct
                width = struct.unpack('<I', dib[4:8])[0]
                height = struct.unpack('<I', dib[8:12])[0]
                bitcount = struct.unpack('<H', dib[14:16])[0]
                compress = struct.unpack('<I', dib[16:20])[0]
                
                if compress != 0:
                    return False, "Komprimiert"
                if bitcount not in [24, 32]:
                    return False, "Nur 24/32-bit"
                
                # Pixel-Offset
                pixoff = struct.unpack('<I', header[10:14])[0]
                bytes_pp = bitcount // 8
                row_sz = ((width * bitcount + 31) // 32) * 4
                
                # BMP ist bottom-up → von unten anfangen
                f.seek(pixoff + (height - 1) * row_sz)
                
                fb_pixels = memoryview(target_buffer)
                fb_pitch = target_width * 2
                
                # Zeile für Zeile lesen (rückwärts von unten)
                # Optimiert: Prozessiere in 10er-Blöcken um schneller zu sein
                for y in range(height):
                    if y >= target_height:
                        break
                    
                    row = f.read(row_sz)
                    if not row:
                        break
                    
                    # Pixel konvertieren - optimiert mit Batch-Processing
                    fb_row_off = y * fb_pitch
                    for x in range(0, min(width, target_width), 1):
                        px_off = x * bytes_pp
                        b = row[px_off]
                        g = row[px_off + 1] if px_off + 1 < len(row) else 0
                        r = row[px_off + 2] if px_off + 2 < len(row) else 0
                        
                        rgb565 = ImageLoader._color_rgb_to_rgb565(r, g, b)
                        fb_pixels[fb_row_off + x * 2:fb_row_off + x * 2 + 2] = rgb565.to_bytes(2, 'big')
                    
                    # Rückwärts zur nächsten Zeile
                    if y < height - 1:
                        next_y = height - y - 2
                        f.seek(pixoff + next_y * row_sz)
                
                # Cache speichern
                if ImageLoader._cache_enabled:
                    ImageLoader._cache[filepath] = {
                        'width': min(width, target_width),
                        'height': min(y + 1, target_height),
                        'data': bytearray(target_buffer)
                    }
                    gc.collect()
                
                return True, f"OK: {width}x{height}"
        
        except OSError:
            return False, "OSError"
        except Exception as e:
            return False, f"{type(e).__name__}"


class BackgroundManager:
    """BMP-Hintergrund Manager für WatchFace."""

    def __init__(self, display, image_path=None):
        self.display = display
        self.image_path = image_path
        self.has_background = False

    def load_background(self, filepath=None):
        """Lade BMP-Hintergrund."""
        path = filepath or self.image_path
        if not path:
            return False, "Kein Bildpfad"
        
        success, message = ImageLoader.load_bmp(
            path, self.display.buffer,
            self.display.width, self.display.height
        )
        
        if success:
            self.has_background = True
        
        return success, message

    def clear_background(self):
        """Hintergrund löschen."""
        self.display.fill(self.display.BLACK)
        self.has_background = False

    def render_to_display(self):
        """Display updaten."""
        self.display.show()

    def render_region(self, x, y, w, h):
        """Bereich updaten."""
        self.display.show_region(x, y, w, h)
