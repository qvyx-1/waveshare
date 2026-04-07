# SD-Karte Treiber (Simplified - SPI-basiert)
# machine.SDCard hangt oft, daher: Fallback auf RohSPI

import os
import gc
import machine
import time


class SDCardSimple:
    """
    Minimal SD-Karten-Treiber über SPI für Diagnose.
    """
    
    def __init__(self, i2c=None):
        self.i2c = i2c
        self.spi = None
        self.cs_pin = None
        self.mounted = False
    
    def init(self):
        """Initialisiere SD-Verbindung."""
        print("[SD] Initialisiere SD-Karte...")
        
        try:
            # Setup
            self.cs_pin = machine.Pin(11, machine.Pin.OUT)
            self.cs_pin.value(1)
            time.sleep_ms(50)
            
            # SPI-Bus
            self.spi = machine.SPI(
                1,
                baudrate=400_000,
                polarity=0,
                phase=0,
                bits=8,
                firstbit=machine.SPI.MSB,
                sck=machine.Pin(36),
                mosi=machine.Pin(35),
                miso=machine.Pin(37)
            )
            
            print("[SD] ✓ SPI-Bus erstellt")
            
            # Test-Befehl
            if self._test_sd_cmd0():
                print("[SD] ✓ SD-Karte erkannt")
                self.mounted = True
                return True
            else:
                print("[SD] ⚠️  SD antwortet nicht")
                self.mounted = False
                return True  # Nicht fatal
        
        except Exception as e:
            print(f"[SD] Fehler: {type(e).__name__}")
            return False
    
    def _test_sd_cmd0(self):
        """Sende CMD0 an SD."""
        try:
            # Mindestens 74 Takte
            for _ in range(10):
                self.spi.write(b'\xFF')
            
            # CMD0: GO_IDLE_STATE
            self.cs_pin.value(0)
            time.sleep_us(1)
            self.spi.write(b'\x40\x00\x00\x00\x00\x95')
            resp = self.spi.read(1)
            self.spi.write(b'\xFF')
            time.sleep_us(1)
            self.cs_pin.value(1)
            
            return resp[0] == 0x01 if resp else False
        except:
            return False
    
    def is_mounted(self):
        return self.mounted


class SDCardMMC:
    """Kompatiblitäts-Wrapper."""
    
    def __init__(self, i2c=None):
        self.impl = SDCardSimple(i2c)
    
    def init(self):
        return self.impl.init()
    
    def is_mounted(self):
        return self.impl.is_mounted()
    
    def list_files(self, path='/sd'):
        return []


async def test_sd_mmc(display, i2c):
    """Teste SD."""
    import uasyncio as asyncio
    
    print("\n[SD-TEST] SD-Diagnose")
    try:
        sd = SDCardMMC(i2c)
        sd.init()
        if sd.is_mounted():
            print("[SD-TEST] ✓ SD erkannt")
        else:
            print("[SD-TEST] ⚠️  SD nicht erkannt")
        print("[SD-TEST] done\n")
    except Exception as e:
        print(f"[SD-TEST] Error: {e}\n")
    
    return True
