"""
EventRegistry - helper to track and cancel Kivy Clock events.
"""
from kivy.clock import Clock


class EventRegistry:
    """Register and cancel Clock events safely."""

    def __init__(self):
        self._events = []

    def schedule_once(self, fn, delay):
        event = Clock.schedule_once(fn, delay)
        self._events.append(event)
        return event

    def schedule_interval(self, fn, dt):
        event = Clock.schedule_interval(fn, dt)
        self._events.append(event)
        return event

    def cancel(self, handle):
        if not handle:
            return
        try:
            handle.cancel()
        except Exception:
            pass
        try:
            self._events.remove(handle)
        except ValueError:
            pass

    def cancel_all(self):
        for event in self._events[:]:
            try:
                event.cancel()
            except Exception:
                pass
        self._events.clear()
