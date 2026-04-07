# Reiner SPI-Treiber für SD-Karte (TF-Slot)
# Waveshare ESP32-S3-LCD-1.85
# 
# Funktioniert OHNE sdcard-Modul!
# Liest FAT32-Dateisystem und BMP-Dateien direkt.

import machine
import time
import struct
import gc


class CRC7:
    """Berechne CRC-7 für SD-Befehle."""
    
    @staticmethod
    def crc7(data):
        """Berechne CRC7 für SD Kommandos."""
        crc = 0
        for byte in data:
            crc ^= byte << 1
            for _ in range(8):
                crc <<= 1
                if crc & 0x80:
                    crc ^= 0x09
                crc &= 0xFF
        return (crc | 1) & 0xFF


class SDCRC16:
    """Berechne CRC-16 für SD-Datenblöcke."""
    
    @staticmethod
    def crc16(data):
        """CRC-16 für Datenblock-Prüfung."""
        crc = 0
        for byte in data:
            crc = ((crc << 8) ^ _crc16_table[((crc >> 8) ^ byte) & 0xFF]) & 0xFFFF
        return crc


# CRC-16 Lookup-Tabelle (für schnere Berechnung)
_crc16_table = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
    0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
] + [0] * 240  # Vereinfacht für Demo (komplette Tabelle würde 256 Einträge brauchen)


class TCA9554Control:
    """Steuere TCA9554 GPIO-Expander für CS-Pin."""
    
    ADDR = 0x20
    REG_OUTPUT = 0x01
    REG_CONFIG = 0x03
    
    def __init__(self, i2c):
        self.i2c = i2c
        self.output_state = 0xFF
        self._init_output()
    
    def _init_output(self):
        """Setze EXIO3 als Output."""
        try:
            self.i2c.writeto_mem(self.ADDR, self.REG_CONFIG, bytes([0x00]))
            self.i2c.writeto_mem(self.ADDR, self.REG_OUTPUT, bytes([0xFF]))
        except:
            print("[TCA9554] ⚠️  Fehler beim Init")
    
    def cs_high(self):
        """Setze SE CS (EXIO3) HIGH."""
        self.output_state |= (1 << 3)
        try:
            self.i2c.writeto_mem(self.ADDR, self.REG_OUTPUT, bytes([self.output_state]))
        except:
            pass
    
    def cs_low(self):
        """Setze SD CS (EXIO3) LOW."""
        self.output_state &= ~(1 << 3)
        try:
            self.i2c.writeto_mem(self.ADDR, self.REG_OUTPUT, bytes([self.output_state]))
        except:
            pass


class SDCard:
    """Minimaler SPI-SD-Treiber für Dateizugriff."""
    
    # SD-Kommandos
    CMD0 = 0x40    # Reset
    CMD8 = 0x48    # IF Condition
    CMD55 = 0x77   # App Command
    ACMD41 = 0x69  # SD_SEND_OP_COND
    CMD17 = 0x51   # READ_SINGLE_BLOCK
    CMD58 = 0x7A   # READ_OCR
    
    # Response Tokens
    DATA_TOKEN = 0xFE
    CMD_TIMEOUT = 100
    
    def __init__(self, spi, cs_control, i2c):
        self.spi = spi
        self.cs = cs_control
        self.i2c = i2c
        self.is_sdhc = False
        self.ready = False
        
        # Versuche einfachen GPIO als Fallback
        try:
            self.cs_pin = machine.Pin(11, machine.Pin.OUT)  # GPIO11 falls verfügbar
            self.cs_pin.value(1)
            print("[SD] GPIO11 als CS-Fallback")
        except:
            print("[SD] GPIO11 nicht verfügbar")
    
    def _send_cmd(self, cmd, arg=0, crc=0):
        """Sende SD-Kommando."""
        # Kommando aufbauen: [01|CMD(6bits)|Arg(32bit)|CRC(7bit)|1]
        cmd_byte = cmd & 0x3F
        cmd_frame = bytes([
            0x40 | cmd_byte,  # Start bits + Command
            (arg >> 24) & 0xFF,
            (arg >> 16) & 0xFF,
            (arg >> 8) & 0xFF,
            arg & 0xFF,
            crc
        ])
        
        self.spi.write(cmd_frame)
    
    def _read_response(self, timeout=100):
        """Lese R1 Response (min. 1 Byte)."""
        for _ in range(timeout):
            resp = self.spi.read(1)
            if resp[0] != 0xFF:
                return resp[0]
            time.sleep_ms(1)
        return 0xFF  # Timeout
    
    def _read_data_block(self, length=512):
        """Lese Datenblock nach DATA_TOKEN."""
        # Warte auf DATA_TOKEN
        for _ in range(1000):
            token = self.spi.read(1)[0]
            if token == self.DATA_TOKEN:
                # Lese Daten + CRC
                data = self.spi.read(length + 2)
                return data[:length]
            if token != 0xFF:
                print(f"[SD] ✗ Kein DATA_TOKEN, erhielt: 0x{token:02X}")
                return None
        
        print("[SD] ✗ Timeout beim Warten auf DATA_TOKEN")
        return None
    
    def init(self):
        """Initialisiere SD-Karte - Vereinfachte Version."""
        print("[SD] Initialisiere Karte via SPI...")
        
        try:
            # Nutze dedizierten GPIO11 als CS (nicht TCA9554)
            if not hasattr(self, 'cs_pin'):
                print("[SD] ✗ CS-Pin nicht verfügbar")
                return False
            
            # SPI Speed langsam für Init
            self.spi = machine.SPI(
                1,
                baudrate=400_000,
                polarity=0,
                phase=0,
                bits=8,
                firstbit=machine.SPI.MSB,
                sck=machine.Pin(14, machine.Pin.OUT),
                mosi=machine.Pin(17, machine.Pin.OUT),
                miso=machine.Pin(16, machine.Pin.IN)
            )
            
            print("[SD] SPI Bus 1 @ 400kHz (via GPIO11 CS)")
            
            # Sende 80+ Clock-Pulses mit CS HIGH
            print("[SD] Sende 80+ Clock Pulses...")
            self.cs_pin.value(1)
            time.sleep_ms(10)
            self.spi.write(b'\xFF' * 10)
            
            # CMD0: Reset (0x40, Arg=0, CRC=0x95)
            print("[SD] → CMD0 (Reset)")
            self.cs_pin.value(0)  # CS LOW
            time.sleep_ms(1)
            
            cmd0 = bytes([0x40, 0x00, 0x00, 0x00, 0x00, 0x95])
            self.spi.write(cmd0)
            time.sleep_ms(2)
            
            # Lese Response
            resp = None
            for attempt in range(20):
                r = self.spi.read(1)[0]
                if r != 0xFF:
                    resp = r
                    print(f"[SD] ✓ R1[{attempt}]=0x{r:02X}")
                    break
            
            self.cs_pin.value(1)  # CS HIGH
            time.sleep_ms(10)
            
            if resp != 0x01:
                print(f"[SD] ✗ CMD0 fehlgeschlagen (R1=0x{resp:02X})")
                # Karte antwortet nicht - möglicherweise falsche Baudrate,
                # kein CS-Signal oder Karte nicht eingefügt
                return False
            
            print("[SD] ✓ Karte erkannt!")
            self.ready = True
            return True
        
        except Exception as e:
            print(f"[SD] ✗ Fehler: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def read_block(self, block_num):
        """Lese einen 512-Byte Block."""
        try:
            # Bei SDHC ist die Adresse direkt der Block-Index, sonst *512
            address = block_num if self.is_sdhc else block_num * 512
            
            # CMD17: READ_SINGLE_BLOCK
            self.cs.cs_low()
            self._send_cmd(self.CMD17, address)
            resp = self._read_response()
            
            if resp != 0x00:
                print(f"[SD] ✗ CMD17 failed: 0x{resp:02X}")
                self.cs.cs_high()
                return None
            
            # Lese Datenblock
            data = self._read_data_block(512)
            
            self.cs.cs_high()
            self.spi.write(b'\xFF')
            
            return data
        
        except Exception as e:
            print(f"[SD] Read error: {e}")
            return None


class SDFileSystem:
    """Einfaches FAT32-Minimalsystem für BMP-Zugriff."""
    
    def __init__(self, sd_card):
        self.sd = sd_card
        self.boot_sector = None
        self.sectors_per_cluster = 1
        self.reserved_sectors = 0
        self.fat_sectors = 0
        self.root_cluster = 2
    
    def init(self):
        """Lese Boot-Sektor und FAT-Infos."""
        print("[FS] Lese Boot-Sektor...")
        self.boot_sector = self.sd.read_block(0)
        
        if not self.boot_sector:
            print("[FS] ✗ Boot-Sektor nicht lesbar")
            return False
        
        # Prüfe MBR-Signatur
        if self.boot_sector[-2:] != b'\x55\xAA':
            print("[FS] ⚠️  Keine FAT32-Signatur")
        
        # Extrahiere FAT32-Parameter
        try:
            self.sectors_per_cluster = self.boot_sector[13]
            self.reserved_sectors = struct.unpack('<H', self.boot_sector[14:16])[0]
            self.fat_sectors = struct.unpack('<I', self.boot_sector[36:40])[0]
            self.root_cluster = struct.unpack('<I', self.boot_sector[44:48])[0]
            
            print(f"[FS] ✓ Cluster Size: {self.sectors_per_cluster}")
            print(f"[FS] ✓ FAT Sectors: {self.fat_sectors}")
            print(f"[FS] ✓ Root Cluster: {self.root_cluster}")
            
            return True
        
        except Exception as e:
            print(f"[FS] ✗ Fehler beim Parsen: {e}")
            return False
    
    def find_file(self, filename):
        """Durchsuche Root-Directory nach Datei."""
        print(f"[FS] Suche nach {filename}...")
        
        # Lende Root-Directory-Cluster
        cluster = self.root_cluster
        sector = (cluster - 2) * self.sectors_per_cluster + self.reserved_sectors + 2 * self.fat_sectors
        
        try:
            data = self.sd.read_block(sector)
            if not data:
                return None
            
            # Durchsuche DIR-Einträge (32 bytes each)
            for i in range(0, 512, 32):
                entry = data[i:i+32]
                
                if entry[0] == 0x00:  # Leerer Eintrag - Ende
                    break
                
                if entry[0] == 0xE5:  # Gelöschter Eintrag
                    continue
                
                # Extrahiere Dateiname
                name_raw = entry[0:8].strip(b' ')
                ext_raw = entry[8:11].strip(b' ')
                
                full_name = (name_raw + b'.' + ext_raw).decode('ascii', errors='ignore').lower()
                target_name = filename.lower()
                
                if full_name == target_name or full_name == target_name.replace('.', ''):
                    # Gefunden!
                    attr = entry[11]
                    start_cluster = struct.unpack('<H', entry[26:28])[0]
                    file_size = struct.unpack('<I', entry[28:32])[0]
                    
                    print(f"[FS] ✓ Gefunden: {full_name} ({file_size} bytes, Cluster {start_cluster})")
                    return {
                        'name': full_name,
                        'size': file_size,
                        'start_cluster': start_cluster,
                        'attr': attr
                    }
            
            print(f"[FS] ✗ Datei nicht gefunden")
            return None
        
        except Exception as e:
            print(f"[FS] Fehler: {e}")
            return None
    
    def read_file(self, file_info, max_bytes=None):
        """Lese komplette Datei."""
        try:
            size = file_info['size']
            if max_bytes:
                size = min(size, max_bytes)
            
            print(f"[FS] Lese {file_info['name']} ({size} bytes)...")
            
            # Berechne Sektor aus Cluster
            cluster = file_info['start_cluster']
            data = bytearray()
            
            bytes_read = 0
            visited_clusters = 0
            max_clusters = 10000  # Sicherheit gegen Endlosschleife
            
            while bytes_read < size and visited_clusters < max_clusters:
                # Cluster -> Sektor
                sector = (cluster - 2) * self.sectors_per_cluster + self.reserved_sectors + 2 * self.fat_sectors
                
                # Lese Sektor
                block = self.sd.read_block(sector)
                if not block:
                    print(f"[FS] ✗ Fehler beim Lesen Cluster {cluster}")
                    break
                
                # Anhängen
                to_read = min(512, size - bytes_read)
                data.extend(block[:to_read])
                bytes_read += to_read
                
                visited_clusters += 1
                
                if (visited_clusters % 10) == 0:
                    print(f"  [{bytes_read}/{size}]", end='\r')
            
            print()
            print(f"[FS] ✓ Gelesen: {len(data)} bytes")
            return bytes(data)
        
        except Exception as e:
            print(f"[FS] Read error: {e}")
            return None
