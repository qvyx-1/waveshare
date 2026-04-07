# Demo-Sequenz für SuperHero Watch Startup
# Waveshare ESP32-S3-LCD-1.85 (360x360 RGB565)
#
# Zeigt beim Start eine Demo-Sequenz:
#  1. Farbstreifen (Farb-Kalibrierung)
#  2. Sanfter Regenbogen-Verlauf (FIXED: Byte-Swap korrekt)
#  3. VGA-Font Intro-Slide
#  4. Bluemarble Bitmap (Earth aus NASA)
#  5. Animierte Kreise
#  6. Watch-Splash

import time
import gc


def _color(display, r, g, b):
    """Kurzform für display.color565()."""
    return display.color565(r, g, b)


# ═══════════════════════════════════════════════
# VGA Bitmap Font Renderer
# ═══════════════════════════════════════════════

def draw_char(display, font, ch, x, y, fg, bg=None):
    """Zeichne ein einzelnes Zeichen aus einem VGA-Bitmap-Font."""
    code = ord(ch)
    if code < font.FIRST or code > font.LAST:
        return font.WIDTH
    
    char_idx = code - font.FIRST
    W = font.WIDTH
    H = font.HEIGHT
    bytes_per_row = (W + 7) // 8
    offset = char_idx * H * bytes_per_row
    
    font_data = font._FONT
    
    for row in range(H):
        row_off = offset + row * bytes_per_row
        for byte_idx in range(bytes_per_row):
            bits = font_data[row_off + byte_idx]
            for bit in range(8):
                col = byte_idx * 8 + bit
                if col >= W:
                    break
                px = x + col
                py = y + row
                if bits & (1 << (7 - bit)):
                    display.pixel(px, py, fg)
                elif bg is not None:
                    display.pixel(px, py, bg)
    
    return W


def draw_text(display, font, text, x, y, fg, bg=None):
    """Zeichne einen Text-String mit VGA-Bitmap-Font."""
    cx = x
    for ch in text:
        cx += draw_char(display, font, ch, cx, y, fg, bg)
    return cx


def text_width(font, text):
    """Berechne Breite eines Strings in Pixeln."""
    return font.WIDTH * len(text)


def draw_text_centered(display, font, text, y, fg, bg=None):
    """Zeichne zentrierten Text auf der Y-Position."""
    w = text_width(font, text)
    x = (display.width - w) // 2
    draw_text(display, font, text, x, y, fg, bg)


# ═══════════════════════════════════════════════
# Demo Scenes
# ═══════════════════════════════════════════════

def scene_color_stripes(display, duration_ms=2000):
    """Farbstreifen zur Farb-Kalibrierung."""
    print("[DEMO] Szene: Farbstreifen")
    
    w, h = display.width, display.height
    stripe_w = w // 6
    colors = [
        (255, 0, 0),      # Rot
        (255, 128, 0),    # Orange
        (255, 255, 0),    # Gelb
        (0, 255, 0),      # Grün
        (0, 0, 255),      # Blau
        (255, 0, 255),    # Magenta
    ]
    
    for idx, (r, g, b) in enumerate(colors):
        display.fill_rect(idx * stripe_w, 0, stripe_w, h, _color(display, r, g, b))
    
    display.show()
    time.sleep_ms(duration_ms)


def scene_rainbow_gradient(display, duration_ms=3000):
    """Sanfter HSV Regenbogen-Farbverlauf."""
    print("[DEMO] Szene: Regenbogen-Verlauf")
    
    w, h = display.width, display.height
    
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
        
        display.vline(x, 0, h, _color(display, r, g, b))
    
    display.show()
    time.sleep_ms(duration_ms)


def scene_vga_intro(display, duration_ms=3000):
    """Intro-Slide mit VGA-Bitmap-Font."""
    print("[DEMO] Szene: VGA Font Intro")
    
    try:
        from bitmap import vga1_bold_16x32 as big_font
        has_big = True
    except ImportError:
        has_big = False
        print("[DEMO] vga1_bold_16x32 nicht gefunden, nutze built-in Font")
    
    try:
        from bitmap import vga1_8x8 as small_font
        has_small = True
    except ImportError:
        has_small = False
    
    w, h = display.width, display.height
    
    # Hintergrund: Dunkles Blau-Gradient
    for y in range(h):
        intensity = y * 80 // h
        c = _color(display, 0, 0, intensity + 40)
        display.hline(0, y, w, c)
    
    center_y = h // 2
    
    if has_big:
        # Großer Titel
        WHITE = _color(display, 255, 255, 255)
        CYAN = _color(display, 0, 255, 255)
        YELLOW = _color(display, 255, 220, 0)
        
        # "SUPER" in Weiß
        draw_text_centered(display, big_font, "SUPER", center_y - 80, WHITE)
        # "HERO" in Cyan
        draw_text_centered(display, big_font, "HERO", center_y - 40, CYAN)
        # "WATCH" in Gelb
        draw_text_centered(display, big_font, "WATCH", center_y + 8, YELLOW)
    else:
        # Fallback: built-in Font
        display.text("SUPERHERO WATCH", 60, center_y - 10, 
                     _color(display, 255, 255, 0))
    
    if has_small:
        GREY = _color(display, 160, 160, 160)
        draw_text_centered(display, small_font, "ESP32-S3 Edition", center_y + 60, GREY)
        draw_text_centered(display, small_font, "MicroPython v2.0", center_y + 80, GREY)
    else:
        display.text("Waveshare ESP32-S3", 50, center_y + 60,
                     _color(display, 128, 128, 128))
    
    display.show()
    time.sleep_ms(duration_ms)
    
    gc.collect()


def scene_bluemarble(display, duration_ms=4000):
    """Zeige Bluemarble Bitmap (Earth von NASA)."""
    print("[DEMO] Szene: Bluemarble Earth")
    
    try:
        import bluemarble
        
        w, h = display.width, display.height
        bmp_w, bmp_h = bluemarble.WIDTH, bluemarble.HEIGHT
        palette = bluemarble.PALETTE
        bitmap = bluemarble._bitmap
        
        # Schwarzer Hintergrund
        display.fill(_color(display, 0, 0, 0))
        
        # Offset zum Zentrieren der 240x240 Bitmap auf 360x360
        off_x = (w - bmp_w) // 2
        off_y = (h - bmp_h) // 2
        
        print(f"[DEMO] Bitmap {bmp_w}x{bmp_h} → Offset ({off_x}, {off_y})")
        
        # Rendern: Jedes Pixel als 1x1 Pixel
        for y in range(bmp_h):
            for x in range(bmp_w):
                idx = bitmap[y * bmp_w + x]
                c = palette[idx]
                display.pixel(off_x + x, off_y + y, c)
            
            if (y % 40) == 0:
                print(f"  [{y}/{bmp_h}]", end='\r')
        
        print()
        display.show()
        print("[DEMO] ✓ Bluemarble angezeigt")
        time.sleep_ms(duration_ms)
        gc.collect()
    
    except ImportError:
        print("[DEMO] bluemarble.py nicht gefunden, überspringe")
    except Exception as e:
        print(f"[DEMO] Fehler bei Bluemarble: {e}")


def scene_concentric_circles(display, duration_ms=3000):
    """Animierte konzentrische Kreise."""
    print("[DEMO] Szene: Animierte Kreise")
    
    w, h = display.width, display.height
    cx, cy = w // 2, h // 2
    max_r = min(cx, cy)
    
    display.fill(_color(display, 0, 0, 0))
    
    # Male Kreise von außen nach innen
    for i in range(max_r, 0, -8):
        hue = ((max_r - i) * 360) // max_r
        
        if hue < 60:
            r, g, b = 255, int(255 * hue / 60) + 40, 40
        elif hue < 120:
            r, g, b = int(255 * (120 - hue) / 60) + 40, 255, 40
        elif hue < 180:
            r, g, b = 40, 255, int(255 * (hue - 120) / 60) + 40
        elif hue < 240:
            r, g, b = 40, int(255 * (240 - hue) / 60) + 40, 255
        elif hue < 300:
            r, g, b = int(255 * (hue - 240) / 60) + 40, 40, 255
        else:
            r, g, b = 255, 40, int(255 * (360 - hue) / 60) + 40
        
        c = _color(display, min(r, 255), min(g, 255), min(b, 255))
        display.ellipse(cx, cy, i, i, c, True)
    
    display.show()
    time.sleep_ms(duration_ms)


def scene_watch_splash(display, duration_ms=2000):
    """Kurzer Watch-Splash vor dem Hauptbild."""
    print("[DEMO] Szene: Splash Screen")
    
    w, h = display.width, display.height
    cx, cy = w // 2, h // 2
    
    # Schwarzer Hintergrund
    display.fill(_color(display, 0, 0, 0))
    
    # Uhr-Zifferblatt-Rahmen
    display.ellipse(cx, cy, 170, 170, _color(display, 60, 60, 80), True)
    display.ellipse(cx, cy, 168, 168, _color(display, 0, 0, 20), True)
    
    # Ring-Dekoration
    for i in range(0, 360, 30):
        import math
        angle = i * 3.14159 / 180
        x1 = cx + int(150 * math.cos(angle))
        y1 = cy + int(150 * math.sin(angle))
        x2 = cx + int(162 * math.cos(angle))
        y2 = cy + int(162 * math.sin(angle))
        
        if i % 90 == 0:
            c = _color(display, 255, 220, 0)  # Gelb für 12/3/6/9
            display.fill_rect(x1 - 2, y1 - 2, 4, 4, c)
        else:
            c = _color(display, 100, 100, 120)
            display.pixel(x1, y1, c)
    
    # SUPER HERO Text
    try:
        from bitmap import vga1_bold_16x32 as bfont
        draw_text_centered(display, bfont, "SUPER", cy - 30, _color(display, 0, 200, 255))
        draw_text_centered(display, bfont, "HERO", cy + 14, _color(display, 255, 200, 0))
    except:
        display.text("SUPER HERO WATCH", 55, cy - 8, _color(display, 0, 200, 255))
    
    display.show()
    time.sleep_ms(duration_ms)


# ═══════════════════════════════════════════════
# Haupt-Demo-Funktion
# ═══════════════════════════════════════════════

async def run_demo(display):
    """
    Asyncio-kompatible Demo-Sequenz beim Startup.
    Kann auch synchron mit time.sleep() genutzt werden.
    """
    import uasyncio as asyncio
    
    print("[DEMO] ═══ SuperHero Watch Demo-Sequenz ═══")
    
    try:
        # Szene 1: Farbstreifen-Kalibrierung (2 sec)
        scene_color_stripes(display, 2000)
        await asyncio.sleep_ms(100)
        
        # Szene 2: Sanfter Regenbogen (3 sec)
        scene_rainbow_gradient(display, 3000)
        await asyncio.sleep_ms(100)
        
        # Szene 3: VGA Intro (3 sec)
        scene_vga_intro(display, 3000)
        await asyncio.sleep_ms(100)
        
        # Szene 4: Bluemarble (nur wenn Datei vorhanden)
        scene_bluemarble(display, 4000)
        await asyncio.sleep_ms(100)
        
        # Szene 5: Animierte Kreise (2 sec)
        scene_concentric_circles(display, 2000)
        await asyncio.sleep_ms(100)
        
        # Szene 6: Watch Splash (2 sec)
        scene_watch_splash(display, 2000)
        await asyncio.sleep_ms(100)
    
    except Exception as e:
        print(f"[DEMO] ✗ Fehler: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("[DEMO] ═══ Demo-Sequenz abgeschlossen ═══")
    gc.collect()
