import math
import struct
import machine
from machine import I2S, Pin, I2C
from config import SPEAK_DIN, SPEAK_LRCK, SPEAK_BCK, I2C_SDA, I2C_SCL, TCA9554_ADDR, EXIO1

class Audio:
    """
    Audio-Treiber für den PCM5101 DAC am ESP32-S3-LCD-1.85.
    VERIFIZIERTE PINS: DIN=47, LRCK=38, BCK=48.
    Nutzt zusätzlich den TCA9554 Expander (EXIO1), um den Verstärker einzuschalten.
    """
    
    def __init__(self, rate=44100, i2c=None):
        self.rate = rate
        self._phase = 0 # Phasen-Tracker für Knack-freie Übergänge
        self._last_vol = 0.0 # Lautstärken-Tracker für weiches Gleiten
        
        # I2C für Hardware-Enable (TCA9554)
        if i2c is None:
            self._i2c = machine.I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400_000)
        else:
            self._i2c = i2c
            
        print(f"[AUDIO] Init I2S: DIN={SPEAK_DIN}, LRCK={SPEAK_LRCK}, BCK={SPEAK_BCK}")
        
        # I2S Konfiguration (ESP32-S3 Pin-Mapping)
        self.i2s = I2S(
            1, 
            sck=Pin(SPEAK_BCK), 
            ws=Pin(SPEAK_LRCK), 
            sd=Pin(SPEAK_DIN),
            mode=I2S.TX, 
            bits=16, 
            format=I2S.STEREO,
            rate=rate, 
            ibuf=8192 # Größerer Puffer für flüssigere Wiedergabe
        )
        
        # Power-Amplifier aktivieren (PA_EN on EXIO1 via TCA9554)
        self.enable_amplifier(True)

    def get_gliding_buffer(self, freq=440, new_vol=0.5, num_samples=1024):
        """Erzeugt einen Sinus-Puffer mit fließendem Lautstärken-Übergang (Interpolation)."""
        buf = bytearray(num_samples * 4) # 16-bit Stereo
        
        # Berechnungsschritt pro Sample (Phase & Lautstärke)
        step_phase = 2 * math.pi * freq / self.rate
        step_vol = (new_vol - self._last_vol) / num_samples
        
        current_vol = self._last_vol
        
        for i in range(num_samples):
            amplitude = int(32767 * current_vol)
            val = int(amplitude * math.sin(self._phase))
            
            # 16-bit Signed Little-Endian (Stereo: L + R gleich)
            struct.pack_into('<hh', buf, i * 4, val, val)
            
            # Phase und Lautstärke inkrementieren
            self._phase += step_phase
            current_vol += step_vol
            
            # Phase im Bereich 2*pi halten
            if self._phase > 2 * math.pi:
                self._phase -= 2 * math.pi
                
        # Status für nächsten Puffer speichern
        self._last_vol = new_vol
        return buf

    def get_sine_buffer(self, freq=440, volume=0.5, num_samples=512):
        """Erzeugt einen Sinus-Puffer und aktualisiert die interne Phase."""
        amplitude = int(32767 * volume)
        buf = bytearray(num_samples * 4) # 16-bit Stereo
        
        # Berechnungsschritt pro Sample
        step = 2 * math.pi * freq / self.rate
        
        for i in range(num_samples):
            val = int(amplitude * math.sin(self._phase))
            struct.pack_into('<hh', buf, i * 4, val, val)
            self._phase += step
            
            # Phase im Bereich 2*pi halten, um Präzisionsverluste zu vermeiden
            if self._phase > 2 * math.pi:
                self._phase -= 2 * math.pi
                
        return buf

    def enable_amplifier(self, state=True):
        """Schaltet den Audio-Verstärker via TCA9554 ein (True) oder aus (False)."""
        try:
            # Register 0x03: Konfiguration (0 = Output)
            # Wir lesen den aktuellen Zustand, um andere Pins nicht zu stören
            config = self._i2c.readfrom_mem(TCA9554_ADDR, 0x03, 1)[0]
            # Bit EXIO1 (Verstärker) auf Output setzen (0)
            config &= ~(1 << EXIO1)
            self._i2c.writeto_mem(TCA9554_ADDR, 0x03, bytes([config]))
            
            # Register 0x01: Output Port
            output = self._i2c.readfrom_mem(TCA9554_ADDR, 0x01, 1)[0]
            if state:
                output |= (1 << EXIO1)  # HIGH = Aktiviert
                print("[AUDIO] Amplifier ENABLED (EXIO1 HIGH)")
            else:
                output &= ~(1 << EXIO1) # LOW = Shutdown
                print("[AUDIO] Amplifier DISABLED (EXIO1 LOW)")
            self._i2c.writeto_mem(TCA9554_ADDR, 0x01, bytes([output]))
        except Exception as e:
            print(f"[AUDIO] Fehler bei Amplifier Enable: {e}")

    def play_sine(self, freq=440, duration_ms=1000, volume=0.5):
        """Spielt einen Sinuston mit der angegebenen Frequenz und Dauer."""
        amplitude = int(32767 * volume)
        
        # Puffer für eine Periode berechnen
        samples_per_cycle = self.rate // freq
        buf = bytearray(samples_per_cycle * 4) 
        
        for i in range(samples_per_cycle):
            val = int(amplitude * math.sin(2 * math.pi * i / samples_per_cycle))
            struct.pack_into('<hh', buf, i * 4, val, val)
            
        total_samples = int(self.rate * (duration_ms / 1000))
        written_samples = 0
        
        print(f"[AUDIO] Spiele {freq}Hz...")
        
        while written_samples < total_samples:
            # Puffer in den I2S-Bus schreiben
            self.i2s.write(buf)
            written_samples += samples_per_cycle
            
    def deinit(self):
        """Gibt den I2S-Bus frei und schaltet Verstärker aus."""
        # Optional: Verstärker aus, um Strom zu sparen
        self.enable_amplifier(False)
        self.i2s.deinit()
