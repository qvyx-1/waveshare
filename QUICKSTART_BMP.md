# 🎨 Schnellstart: BMP-Hintergrund auf SD-Karte laden

## Das Wichtigste in 30 Sekunden

### 1. BMP-Datei auf Device kopieren:
```bash
cd /home/daniel/python-projects/waveshare/waveshare
python -m mpremote connect /dev/ttyACM0 cp ./tools/test_bg.bmp :assets/bg.bmp
```

**oder** Ihre eigene BMP-Datei:
```bash
python -m mpremote connect /dev/ttyACM0 cp pfad/zu/ihrer/bild.bmp :assets/bg.bmp
```

### 2. Watch starten
- Board powern
- Boot-Screen sehen
- Button drücken → Watch-Face wird geladen
- **500ms später**: BMP wird automatisch geladen und angezeigt!

### 3. Fertig! ✅
Das BMP ist jetzt Ihr Zifferblatt-Hintergrund mit Zeigern drauf.

---

## Details

| Aspekt | Info |
|--------|------|
| **Ladezeit** | ~3-5 Sekunden bei 320×320 BMP |
| **RAM-Nutzung** | +0 KB (nutzt nur Framebuffer) |
| **Datei-Pfade** | Durchsucht automatisch `/assets`, `/sd`, `/`, etc. |
| **Format** | 24-bit RGB BMP (Standard) |
| **Auto-Laden** | JA - 500ms nach Watch-Start |

---

## Dateien:

```
src/
  └── display/
      ├── sd_manager.py (NEU - DMA-optimierter Loader)
      ├── watch_face.py (UPDATED - BMP-Support)
      └── image_loader.py (Fallback bei Fehler)
```

**Sync**: `bash tools/sync.sh` - Alles auf Board!

---

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| BMP wird nicht angezeigt? | Checken: `/assets/bg.bmp` vorhanden? |
| Device hängt? | BMP zu groß? Max 360×360 |
| Zeiger fehlen? | Normal - BMP ersetzt Ziffern-Design |
| Zu langsam? | Versuchen Sie kleinere auflösung |

---

**Das System ist LIVE und einsatzbereit!** 🚀
