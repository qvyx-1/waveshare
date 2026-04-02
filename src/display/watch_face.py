# Watch-Face Rendering für die SuperHero Watch
# 360x360 rundes Display

import math
import time


class WatchFace:
    """
    Superhelden-Zifferblatt für das 360x360 runde Display.
    
    Design: "IRON WATCH" — Iron Man inspiriert
    - Äußerer Kreis-Rahmen (gold/rot)
    - Stunden-/Minuten-/Sekundenzeiger
    - Digitale Zeitanzeige in der Mitte
    - Gadget-Slots (oben/unten)
    """

    # Display-Zentrum
    CX = 180
    CY = 180
    R  = 168  # Nutzradius (etwas kleiner als Display-Rand)

    # Farben (Dynamisch via color565 generiert)
    COLOR_BG       = 0x0000 
    COLOR_RING     = 0x00F8 # Rot
    COLOR_ACCENT   = 0x0EFF # Gold
    COLOR_TEXT     = 0xFFFF # Weiß
    COLOR_SECOND   = 0x00F8 # Rot
    COLOR_MINUTE   = 0xFFFF # Weiß
    COLOR_HOUR     = 0x8DA0 # Gold
    COLOR_TICK     = 0x0842 # Graue Markierungen
    COLOR_DIM      = 0x0421 # Dunkel

    def __init__(self, display, rtc, imu, config):
        self.display = display
        self.rtc     = rtc
        self.imu     = imu
        self.config  = config
        self._last_dt = None
        self._tick = 0

    def _polar_to_xy(self, angle_deg, radius):
        """Polarkoordianten → Bildschirmkoordinaten."""
        angle_rad = math.radians(angle_deg - 90)
        x = int(self.CX + radius * math.cos(angle_rad))
        y = int(self.CY + radius * math.sin(angle_rad))
        return x, y

    def _draw_line(self, x0, y0, x1, y1, color):
        """Bresenham-Linie zeichnen."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.display.pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def _draw_thick_line(self, x0, y0, x1, y1, color, thickness=3):
        """Dicke Linie (mehrfach versetzt)."""
        for i in range(-thickness//2, thickness//2 + 1):
            self._draw_line(x0 + i, y0, x1 + i, y1, color)
            self._draw_line(x0, y0 + i, x1, y1 + i, color)

    def draw_background(self):
        """Hintergrund und feste Elemente zeichnen."""
        display = self.display

        # Schwarzer Hintergrund
        display.fill(self.COLOR_BG)

        # Äußerer Ring (Superhelden-Style, mehrfach)
        display.circle(self.CX, self.CY, 175, self.COLOR_RING)
        display.circle(self.CX, self.CY, 174, self.COLOR_RING)
        display.circle(self.CX, self.CY, 172, self.COLOR_ACCENT)
        display.circle(self.CX, self.CY, 170, self.COLOR_DIM)

        # Stunden-Markierungen (12 Stücke)
        for h in range(12):
            angle = h * 30
            x_outer, y_outer = self._polar_to_xy(angle, 160)
            x_inner, y_inner = self._polar_to_xy(angle, 145 if h % 3 == 0 else 150)
            color = self.COLOR_ACCENT if h % 3 == 0 else self.COLOR_TICK
            self._draw_thick_line(x_outer, y_outer, x_inner, y_inner, color, 2)

        # Minuten-Markierungen (60 Stücke)
        for m in range(60):
            if m % 5 != 0:  # Nur zwischen Stunden-Ticks
                angle = m * 6
                x_outer, y_outer = self._polar_to_xy(angle, 160)
                x_inner, y_inner = self._polar_to_xy(angle, 155)
                self._draw_line(x_outer, y_outer, x_inner, y_inner, self.COLOR_TICK)

        # Innerer dekorativer Ring
        display.circle(self.CX, self.CY, 100, 0x1084)   # Dunkler Innenring
        display.circle(self.CX, self.CY, 99, 0x1084)

        # Gadget-Slot Bereiche (oben/unten)
        # Oben: Datum
        display.hline(150, 105, 60, self.COLOR_ACCENT)
        # Unten: Schrittzähler
        display.hline(150, 255, 60, self.COLOR_ACCENT)

    def _draw_hand(self, angle_deg, length, width, color):
        """Zeiger zeichnen (vom Zentrum)."""
        tip_x, tip_y = self._polar_to_xy(angle_deg, length)
        # Gegen-Strich (kurz)
        tail_x, tail_y = self._polar_to_xy(angle_deg + 180, 15)
        self._draw_thick_line(tail_x, tail_y, tip_x, tip_y, color, width)

    def draw_hands(self, hour, minute, second):
        """Alle Zeiger zeichnen."""
        # Stundenzeiger (Winkel: Stunden × 30° + Minuten × 0.5°)
        hour_angle   = (hour % 12) * 30 + minute * 0.5
        minute_angle = minute * 6 + second * 0.1
        second_angle = second * 6

        self._draw_hand(hour_angle,   90, 4, self.COLOR_HOUR)
        self._draw_hand(minute_angle, 130, 3, self.COLOR_MINUTE)
        self._draw_hand(second_angle, 145, 1, self.COLOR_SECOND)

        # Zentrum-Kreis
        self.display.circle(self.CX, self.CY, 6, self.COLOR_ACCENT, filled=True)
        self.display.circle(self.CX, self.CY, 3, self.COLOR_RING, filled=True)

    def draw_digital_time(self, hour, minute):
        """Digitale Zeitanzeige in der Mitte."""
        time_str = f"{hour:02d}:{minute:02d}"
        # Zentriert (8px breite Zeichen × 5 Zeichen = 40px)
        x = self.CX - (len(time_str) * 4)
        self.display.text(time_str, x, 200, self.COLOR_TEXT)

    def draw_date(self, day, month, weekday_str):
        """Datum oben anzeigen."""
        date_str = f"{weekday_str} {day:02d}.{month:02d}"
        x = self.CX - (len(date_str) * 4)
        self.display.text(date_str, x, 113, self.COLOR_ACCENT)

    def draw_steps(self, steps):
        """Schrittzähler unten anzeigen."""
        step_str = f"{steps} Schr."
        x = self.CX - (len(step_str) * 4)
        self.display.text(step_str, x, 260, 0x07E0)   # Grün

    def draw_boot_screen(self):
        """Superhelden-Boot-Bildschirm."""
        d = self.display
        d.fill(0x0000)

        # Roter Ring
        d.circle(180, 180, 170, self.display.RED, filled=False) 
        d.circle(180, 180, 168, self.display.YELLOW, filled=False) 

        # Goldenes "SW" (SuperHero Watch)
        d.text("SUPERHERO", 118, 155, self.display.YELLOW)
        d.text("  WATCH  ", 130, 168, self.display.RED)
        d.text("IRON EDITION", 110, 195, self.display.RED)

        # Kleiner Arc-Reaktor in der Mitte
        d.circle(180, 230, 20, self.display.CYAN, filled=True)
        d.circle(180, 230, 14, self.display.WHITE, filled=True)
        d.circle(180, 230,  8, self.display.CYAN, filled=True)

        # Handlungsanweisung für Button
        d.text("PRESS [BOOT] TO START", 95, 290, self.display.WHITE)
        
        # Display aktualisieren (Framebuffer senden)
        self.display.show()

    def animate_boot_screen(self, audio=None):
        """High-FPS Boot Animation via Partial Updates (IMU)."""
        d = self.display
        try:
            # Beschleunigung auslesen
            ax, ay, az = self.imu.accel()
            
            # Offset berechnen (Dynamisch: +/- 120 Pixel)
            # 90° kalibriertes Mapping + Invertierte X-Achse + Max-Skalierung
            off_x = int(-ay * 120)
            off_y = int(ax * 120)
            
            # --- Dynamisches Audio ---
            if audio:
                # Distanz zur Mitte berechnen (0.0 bis ca. 1.4)
                dist = math.sqrt(ax**2 + ay**2)
                # Lautstärke skalieren (0.0 bis 0.6)
                vol = min(0.6, dist * 0.8)
                # Weicher Sound-Schnipsel mit Amplituden-Gleiten
                buf = audio.get_gliding_buffer(freq=200, new_vol=vol, num_samples=1024)
                try:
                    audio.i2s.write(buf)
                except:
                    pass

            # Fenster-Koordinaten (Zentrum 180, 230)
            # Fenster vergrößert für 120px Ausschlag (wx=180-70=110 -> wx=180-130=50)
            wx, wy, ww, wh = 50, 100, 260, 260
            
            # Nur das Fenster im Puffer löschen
            d.fill_rect(wx, wy, ww, wh, 0x0000)

            # Reaktor an neuer Position zeichnen
            cx, cy = 180 + off_x, 230 + off_y
            d.circle(cx, cy, 20, self.display.CYAN, filled=True)
            d.circle(cx, cy, 14, self.display.WHITE, filled=True)
            d.circle(cx, cy,  8, self.display.CYAN, filled=True)

            # Turbo-Update: Nur dieses Fenster zum Display schicken
            d.show_region(wx, wy, ww, wh)
        except Exception as e:
            print(f"[FACE] Animation Error: {e}")

    def update(self):
        """Watch-Face aktualisieren (jede Sekunde)."""
        # Zeit von RTC holen
        dt = self.rtc.datetime()
        year, month, day, weekday, hour, minute, second = dt

        # Nur neu zeichnen wenn sich Zeit geändert hat
        if self._last_dt == dt:
            return
        self._last_dt = dt

        # Hintergrund neu zeichnen (oder inkrementell)
        if self._tick == 0 or (self._tick % 60 == 0):
            # Vollständige Neuzeichnung jede Minute
            self.draw_background()

        # Zeiger (erst löschen durch Neuzeichnen der Hintergrundfarbe, dann neu)
        # Vereinfacht: kompletter Redraw der Zeigerbereich
        self.display.circle(self.CX, self.CY, 95, self.COLOR_BG, filled=True)
        self.display.circle(self.CX, self.CY, 100, 0x1084)
        self.display.circle(self.CX, self.CY, 99, 0x1084)

        # Zeiger neu zeichnen
        self.draw_hands(hour, minute, second)

        # Digitale Zeit & Datum
        self.draw_digital_time(hour, minute)
        self.draw_date(day, month, self.rtc.weekday_str())

        # Schrittzähler (UPDATE über IMU)
        try:
            steps = self.imu.count_steps()
            self.draw_steps(steps)
        except:
            pass

        self._tick += 1
        
        # Framebuffer final an Display pushen
        self.display.show()
