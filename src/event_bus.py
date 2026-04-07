# event_bus.py — Leichtgewichtiger Event-Bus für MicroPython
# SuperHero Watch — Asyncio-kompatibel

import uasyncio as asyncio


# Event-Typen
EVT_TOUCH_TAP    = 1
EVT_TOUCH_SWIPE_UP    = 2
EVT_TOUCH_SWIPE_DOWN  = 3
EVT_TOUCH_SWIPE_LEFT  = 4
EVT_TOUCH_SWIPE_RIGHT = 5
EVT_TOUCH_LONG_PRESS  = 6
EVT_BUTTON_PRESS = 10
EVT_BUTTON_LONG  = 11
EVT_IMU_SHAKE    = 20
EVT_IMU_TILT     = 21
EVT_TICK_1S      = 30   # Jede Sekunde
EVT_TICK_1M      = 31   # Jede Minute

# Event-Namen für Debugging
_EVT_NAMES = {
    EVT_TOUCH_TAP: "TAP",
    EVT_TOUCH_SWIPE_UP: "SWIPE_UP",
    EVT_TOUCH_SWIPE_DOWN: "SWIPE_DOWN",
    EVT_TOUCH_SWIPE_LEFT: "SWIPE_LEFT",
    EVT_TOUCH_SWIPE_RIGHT: "SWIPE_RIGHT",
    EVT_TOUCH_LONG_PRESS: "LONG_PRESS",
    EVT_BUTTON_PRESS: "BTN_PRESS",
    EVT_BUTTON_LONG: "BTN_LONG",
    EVT_IMU_SHAKE: "SHAKE",
    EVT_IMU_TILT: "TILT",
    EVT_TICK_1S: "TICK_1S",
    EVT_TICK_1M: "TICK_1M",
}


class Event:
    """Einzelnes Event mit Typ und optionalen Daten."""
    __slots__ = ('type', 'data')

    def __init__(self, evt_type, data=None):
        self.type = evt_type
        self.data = data

    def __repr__(self):
        name = _EVT_NAMES.get(self.type, str(self.type))
        return f"<Event:{name} data={self.data}>"


class EventBus:
    """
    Minimaler Event-Bus für MicroPython.
    
    Verwendet eine interne Liste und ein asyncio.Event, sodass Consumer-Tasks
    auf Events warten können ohne busy-looping.
    """

    def __init__(self, maxsize=16):
        self._queue = []
        self._maxsize = maxsize
        self._event = asyncio.Event()
        self._handlers = {}  # evt_type -> [callback, ...]

    def emit(self, evt_type, data=None):
        """Event in die Queue schieben (nicht-blockierend)."""
        evt = Event(evt_type, data)
        if len(self._queue) < self._maxsize:
            self._queue.append(evt)
            self._event.set()

        # Synchrone Handler sofort aufrufen
        handlers = self._handlers.get(evt_type)
        if handlers:
            for h in handlers:
                try:
                    h(evt)
                except Exception as e:
                    print(f"[EVT] Handler error: {e}")

    async def wait(self):
        """Wartet auf das nächste Event (async, blockiert den Task)."""
        while not self._queue:
            await self._event.wait()
            self._event.clear()
            
        # Nimm das älteste Event
        return self._queue.pop(0)

    def on(self, evt_type, handler):
        """Registriert einen synchronen Handler für einen Event-Typ."""
        if evt_type not in self._handlers:
            self._handlers[evt_type] = []
        self._handlers[evt_type].append(handler)

    def off(self, evt_type, handler=None):
        """Entfernt Handler."""
        if handler is None:
            self._handlers.pop(evt_type, None)
        elif evt_type in self._handlers:
            try:
                self._handlers[evt_type].remove(handler)
            except ValueError:
                pass

    def pending(self):
        """Anzahl wartender Events."""
        return self._queue.qsize() if hasattr(self._queue, 'qsize') else 0
