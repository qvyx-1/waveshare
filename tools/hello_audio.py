import time
import sys

# Füge src/ zum Pfad hinzu, damit wir den Treiber finden
sys.path.append('src')

from audio.driver import Audio

def test_sound():
    print("--- Waveshare Audio Test ---")
    print("DAC: PCM5101 (I2S Pins: 17, 18, 16)")
    
    try:
        # Audio initialisieren
        audio = Audio(rate=44100)
        
        print("Spiele 1-sekündigen Test-Sinuston (440Hz)...")
        # 1 Sekunde lang 440 Hz (Kammerton A) abspielen
        audio.play_sine(freq=440, duration_ms=1000, volume=0.5)
        
        print("Test abgeschlossen.")
        
        # Sauber aufräumen
        audio.deinit()
    except Exception as e:
        print(f"Fehler beim Audio-Test: {e}")

if __name__ == "__main__":
    test_sound()
