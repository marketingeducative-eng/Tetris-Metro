"""
AppContext - shared application state and dependencies.
"""
from pathlib import Path

from data.metro_loader import load_metro_network
from core.progress import ProgressManager
from core.settings import SettingsManager
from core.modes import FreeMode, GoalMode


class AppContext:
    """Owns shared state and services for the app."""

    def __init__(self):
        self.metro_network = None
        self.progress_manager = ProgressManager()
        self.settings_manager = SettingsManager()
        self.settings = {
            "practice_mode": False,
            "direction_mode": False,
            "subtitles_enabled": True,
        }
        self.current_line_id = "L3"
        self.current_mode = "FREE"
        self.mode_instance = FreeMode()

    def load_all(self):
        data_path = Path(__file__).resolve().parent.parent / "data" / "barcelona_metro_lines_stations.json"
        self.metro_network = load_metro_network(str(data_path))
        self.progress_manager.load()
        self.settings = {
            "practice_mode": self.settings_manager.get("practice_mode", False),
            "direction_mode": self.settings_manager.get("direction_mode", False),
            "subtitles_enabled": self.settings_manager.get("subtitles_enabled", True),
        }
        if self.metro_network and self.metro_network.lines:
            default_line = self.metro_network.get_line(self.current_line_id)
            if not default_line:
                self.current_line_id = self.metro_network.lines[0].id

    def save_all(self):
        self.settings_manager.set("practice_mode", self.settings.get("practice_mode", False))
        self.settings_manager.set("direction_mode", self.settings.get("direction_mode", False))
        self.settings_manager.set("subtitles_enabled", self.settings.get("subtitles_enabled", True))
        self.progress_manager.save()

    def set_line(self, line_id):
        if line_id:
            self.current_line_id = line_id

    def set_settings(self, practice_mode=None, direction_mode=None, subtitles_enabled=None):
        if practice_mode is not None:
            self.settings["practice_mode"] = bool(practice_mode)
        if direction_mode is not None:
            self.settings["direction_mode"] = bool(direction_mode)
        if subtitles_enabled is not None:
            self.settings["subtitles_enabled"] = bool(subtitles_enabled)

    def set_mode(self, mode_name=None, goal_station_id=None):
        name = (mode_name or "FREE").upper()
        if name == "GOAL":
            self.mode_instance = GoalMode(goal_station_id=goal_station_id)
            self.current_mode = "GOAL"
        else:
            self.mode_instance = FreeMode()
            self.current_mode = "FREE"
