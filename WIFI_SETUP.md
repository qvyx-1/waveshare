# 🌐 WiFi-Verbindung zum SuperHero Watch einrichten

## ✅ Status

**Board WiFi-AP ist AKTIV und bereit!**

```
SSID:        SuperHero-Watch
Passwort:    12345678
IP-Adresse:  192.168.4.1
Netzwerk:    192.168.4.0/24
Gateway:     192.168.4.1
DNS:         0.0.0.0
```

---

## 📱 So verbindest du dich vom Host-PC

### Option 1: Graphisch (bevorzugt)

1. **Öffne Netzwerk-Manager** (oben rechts in der Taskbar)
2. **Wähle "SuperHero-Watch"** aus der WiFi-Liste
3. **Gib Passwort ein**: `12345678`
4. **Verbinde dich**

### Option 2: Kommandozeile (Linux)

```bash
# Mit nmcli (NetworkManager)
nmcli device wifi connect "SuperHero-Watch" password "12345678"

# Mit iw (Advanced)
sudo ip link set wlan0 up
sudo iw wlan0 connect "SuperHero-Watch" password "12345678"
```

### Option 3: Manuell (WiFi-Einstellungen)

```bash
# Prüfe verfügbare Netzwerke
nmcli device wifi list

# Sollte etwa so aussehen:
# IN-USE  SSID                     MODE   CHAN  RATE       SIGNAL  BARS  SECURITY
#         SuperHero-Watch          Infra  1     54 Mbit/s  80      ████  WPA2
```

---

## ✅ Verbindung testen

```bash
# Ping zum Board
ping 192.168.4.1

# Output sollte sein:
# PING 192.168.4.1 (192.168.4.1) 56(84) bytes of data.
# 64 bytes from 192.168.4.1: icmp_seq=1 ttl=255 time=5.23 ms
```

---

## 🚀 SSH oder Telnet zum Board

Sobald verbunden, kannst du dich direkt ins Board verbinden:

```bash
# Option 1: Telnet (falls aktiviert)
telnet 192.168.4.1 23

# Option 2: Serielle WebREPL (falls aktiviert)
# Browser: http://192.168.4.1:8266/
```

---

## 📡 Board-Netzwerk-Informationen (vom Serial)

```python
import network
wlan = network.WLAN(network.AP_IF)
print("Aktiv:", wlan.active())
print("SSID:", wlan.config('essid'))
print("IP:", wlan.ifconfig())
print("MAC:", wlan.config('mac').hex())
```

---

## 🔧 Netzwerk Troubleshooting

### Problem: Kann keine Verbindung herstellen

```bash
# 1. Prüfe, ob AP aktiv ist
# → Board REPL: wlan.active() sollte True sein

# 2. Versuche Netzwerk zu "forgetzen"
nmcli connection delete SuperHero-Watch

# 3. Neu verbinden
nmcli device wifi connect "SuperHero-Watch" password "12345678"
```

### Problem: IP-Konflikt (ein anderes Gerät nutzt 192.168.4.1)

```bash
# IP-Adresse auf dem Board ändern:
# Im Board REPL:
import network
wlan = network.WLAN(network.AP_IF)
wlan.ifconfig(('192.168.5.1', '255.255.255.0', '192.168.5.1', '0.0.0.0'))
```

---

## 📊 Live-Verbindungsmonitor

```bash
# Zeige aktive WiFi-Verbindungen
while true; do
  clear
  echo "=== SuperHero Watch WiFi Status ==="
  date
  echo
  ping -c 1 192.168.4.1 && echo "✅ Board erreichbar" || echo "❌ Board nicht erreichbar"
  echo
  nmcli device wifi list | grep SuperHero
  sleep 2
done
```

---

## 🎯 Nächste Schritte

Sobald verbunden:

1. **WebREPL öffnen** (falls aktiviert)
2. **File-Transfer via Telnet/WebREPL**
3. **Live-Debugging über Remote-Konsole**

---

**Dokumentiert**: 2026-04-02 16:00 UTC  
**Status**: ✅ WiFi AP aktiv und bereit
