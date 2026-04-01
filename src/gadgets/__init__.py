# Gadget-System für die SuperHero Watch
# Registrierung und Interface-Definition

class Gadget:
    """
    Basis-Klasse für alle SuperHero Watch Gadgets.
    
    Gadgets sind modulare Erweiterungen, die:
    - auf dem Zifferblatt angezeigt werden können
    - auf Buttons reagieren können
    - Hintergrundaufgaben ausführen können
    """

    def __init__(self, name, icon="🔧"):
        self.name     = name
        self.icon     = icon
        self.enabled  = True
        self._display = None
        self._config  = None

    def setup(self, display, config):
        """Von der Watch aufgerufen nach Registrierung."""
        self._display = display
        self._config  = config

    def update(self):
        """Wird jede Sekunde aufgerufen. Override in Unterklassen."""
        pass

    def render(self, x, y):
        """Zeichnet Gadget-Info an Position (x, y)."""
        pass

    def on_button(self, button_id):
        """Button-Event. Gibt True zurück wenn verarbeitet."""
        return False

    def __repr__(self):
        return f"<Gadget:{self.name}>"


class GadgetRegistry:
    """Verwaltet alle registrierten Gadgets."""

    def __init__(self):
        self._gadgets = {}

    def register(self, gadget_id, gadget):
        """Gadget registrieren."""
        self._gadgets[gadget_id] = gadget
        print(f"[GADGET] Registriert: {gadget.icon} {gadget.name}")
        return gadget

    def get(self, gadget_id):
        return self._gadgets.get(gadget_id)

    def update_all(self):
        """Alle Gadgets aktualisieren."""
        for gadget in self._gadgets.values():
            if gadget.enabled:
                try:
                    gadget.update()
                except Exception as e:
                    print(f"[GADGET] Fehler in {gadget.name}: {e}")

    def on_button_all(self, button_id):
        """Button an alle Gadgets weitergeben."""
        for gadget in self._gadgets.values():
            if gadget.enabled:
                if gadget.on_button(button_id):
                    return True
        return False

    def list_gadgets(self):
        return list(self._gadgets.values())
