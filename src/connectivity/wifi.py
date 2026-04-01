# WiFi-Manager
# Waveshare SuperHero Watch

import network
import time


class WiFiManager:
    """
    WiFi-Manager für die SuperHero Watch.
    Unterstützt: Station-Mode, automatische Wiederverbindung, Status-Callbacks.
    """

    def __init__(self, config):
        self.config = config
        self._wlan  = network.WLAN(network.STA_IF)
        self._connected = False

    def connect(self, ssid=None, password=None, timeout=None):
        """
        Mit WiFi verbinden.
        
        Args:
            ssid: Netzwerkname (falls None: aus config)
            password: Passwort (falls None: aus config)
            timeout: Timeout in Sekunden (falls None: aus config)
        
        Returns:
            True wenn verbunden, False bei Timeout/Fehler
        """
        ssid     = ssid     or self.config.WIFI_SSID
        password = password or self.config.WIFI_PASSWORD
        timeout  = timeout  or self.config.WIFI_TIMEOUT

        if not ssid:
            print("[WiFi] Kein SSID konfiguriert (secrets.py anlegen)")
            return False

        self._wlan.active(True)

        if self._wlan.isconnected():
            print(f"[WiFi] Bereits verbunden: {self._wlan.ifconfig()[0]}")
            return True

        print(f"[WiFi] Verbinde mit {ssid}...")
        self._wlan.connect(ssid, password)

        t = timeout
        while not self._wlan.isconnected() and t > 0:
            time.sleep(1)
            t -= 1
            print(f"[WiFi] Warte... ({t}s)")

        if self._wlan.isconnected():
            ip = self._wlan.ifconfig()[0]
            print(f"[WiFi] Verbunden! IP: {ip}")
            self._connected = True
            return True
        else:
            print("[WiFi] Verbindung fehlgeschlagen!")
            self._connected = False
            return False

    def disconnect(self):
        """WiFi trennen."""
        self._wlan.disconnect()
        self._wlan.active(False)
        self._connected = False
        print("[WiFi] Getrennt")

    @property
    def is_connected(self):
        return self._wlan.isconnected()

    @property
    def ip_address(self):
        if self.is_connected:
            return self._wlan.ifconfig()[0]
        return None

    def scan(self):
        """Verfügbare Netzwerke scannen."""
        self._wlan.active(True)
        networks = self._wlan.scan()
        return [(n[0].decode(), n[3]) for n in networks]  # (ssid, rssi)
