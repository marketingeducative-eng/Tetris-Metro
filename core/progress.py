"""Progress tracking for line completion and stations."""
import json
from pathlib import Path


class ProgressManager:
    """Persist line progress in data/progress.json."""

    def __init__(self, path=None):
        if path is None:
            path = Path(__file__).resolve().parent.parent / "data" / "progress.json"
        self.path = Path(path)
        self.data = {}
        self.load()

    def load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as file:
                    self.data = json.load(file)
            except (json.JSONDecodeError, OSError):
                self.data = {}
        else:
            self.data = {}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=2, ensure_ascii=False)

    def ensure_line(self, line_id):
        if line_id not in self.data:
            self.data[line_id] = {
                "completed_stations": [],
                "completed_station_ids": [],
                "line_completed": False,
                "goals_completed": 0,
                "badges": {},
                "mini_routes_completed": 0
            }
        if "completed_station_ids" not in self.data[line_id]:
            self.data[line_id]["completed_station_ids"] = []
        if "goals_completed" not in self.data[line_id]:
            self.data[line_id]["goals_completed"] = 0
        if "badges" not in self.data[line_id]:
            self.data[line_id]["badges"] = {}
        if "mini_routes_completed" not in self.data[line_id]:
            self.data[line_id]["mini_routes_completed"] = 0

    def _ensure_daily(self):
        if "daily_completed_dates" not in self.data:
            self.data["daily_completed_dates"] = []

    def _migrate_station_ids(self, line_id):
        self.ensure_line(line_id)
        progress = self.data[line_id]
        station_ids = progress.get("completed_station_ids", [])
        if station_ids:
            return station_ids
        names = progress.get("completed_stations", [])
        if names:
            station_ids = names
            progress["completed_station_ids"] = station_ids
            self.save()
        return station_ids

    def get_line_progress(self, line_id):
        self.ensure_line(line_id)
        return self.data[line_id]

    def get_completed_station_ids(self, line_id):
        return self._migrate_station_ids(line_id)

    def mark_station_completed(self, line_id, station_id):
        self.ensure_line(line_id)
        station_ids = self.data[line_id].get("completed_station_ids", [])
        if station_id not in station_ids:
            station_ids.append(station_id)
            self.data[line_id]["completed_station_ids"] = station_ids
            self.save()

    def mark_line_completed(self, line_id):
        self.ensure_line(line_id)
        if not self.data[line_id].get("line_completed", False):
            self.data[line_id]["line_completed"] = True
            self.save()
    
    def mark_goal_completed(self, line_id):
        """Increment goals_completed counter for a line"""
        self.ensure_line(line_id)
        current_count = self.data[line_id].get("goals_completed", 0)
        self.data[line_id]["goals_completed"] = current_count + 1
        self.save()
    
    def get_goals_completed(self, line_id):
        """Get the number of goals completed for a line"""
        self.ensure_line(line_id)
        return self.data[line_id].get("goals_completed", 0)

    def get_daily_completed_dates(self):
        """Get list of completed daily challenge dates (YYYY-MM-DD)."""
        self._ensure_daily()
        return self.data.get("daily_completed_dates", [])

    def is_daily_completed(self, date_str):
        """Check if daily challenge was completed for a date."""
        self._ensure_daily()
        return date_str in self.data.get("daily_completed_dates", [])

    def mark_daily_completed(self, date_str):
        """Mark a daily challenge as completed, returns True if newly added."""
        self._ensure_daily()
        completed = self.data.get("daily_completed_dates", [])
        if date_str in completed:
            return False
        completed.append(date_str)
        self.data["daily_completed_dates"] = completed
        self.save()
        return True
    
    def mark_first_day_completed(self):
        """Mark the First Day journey as completed"""
        if "first_day_completed" not in self.data:
            self.data["first_day_completed"] = True
            self.save()
    
    def is_first_day_completed(self):
        """Check if First Day journey was completed"""
        return self.data.get("first_day_completed", False)
    
    def mark_badge_unlocked(self, line_id, badge_id):
        """Mark a badge as unlocked for a specific line
        
        Args:
            line_id (str): Line identifier (e.g., "L3")
            badge_id (str): Badge identifier (e.g., "modernisme")
        """
        self.ensure_line(line_id)
        badges = self.data[line_id].get("badges", {})
        if badge_id not in badges:
            badges[badge_id] = True
            self.data[line_id]["badges"] = badges
            
            # Also track globally
            if "global_badges" not in self.data:
                self.data["global_badges"] = {}
            self.data["global_badges"][badge_id] = True
            
            self.save()
    
    def get_line_badges(self, line_id):
        """Get all badges unlocked for a specific line
        
        Args:
            line_id (str): Line identifier
        
        Returns:
            dict: Dictionary of badge_id -> True
        """
        self.ensure_line(line_id)
        return self.data[line_id].get("badges", {})
    
    def get_global_badges(self):
        """Get all badges unlocked globally across all lines
        
        Returns:
            dict: Dictionary of badge_id -> True
        """
        return self.data.get("global_badges", {})
    
    def get_badge_count(self, line_id):
        """Get the number of badges unlocked for a line
        
        Args:
            line_id (str): Line identifier
        
        Returns:
            int: Number of badges unlocked
        """
        badges = self.get_line_badges(line_id)
        return len(badges)
    
    def is_first_day_completed(self):
        """Check if the First Day journey has been completed"""
        return self.data.get("first_day_completed", False)
    
    def mark_mini_route_completed(self, line_id):
        """Mark a mini-route completed for a line.
        
        Args:
            line_id (str): Line identifier
            
        Returns:
            bool: True if this is the first mini-route completion
        """
        self.ensure_line(line_id)
        current_count = self.data[line_id].get("mini_routes_completed", 0)
        is_first = (current_count == 0)
        self.data[line_id]["mini_routes_completed"] = current_count + 1
        self.save()
        return is_first
    
    def get_mini_routes_completed(self, line_id):
        """Get the number of mini-routes completed for a line.
        
        Args:
            line_id (str): Line identifier
            
        Returns:
            int: Number of mini-routes completed
        """
        self.ensure_line(line_id)
        return self.data[line_id].get("mini_routes_completed", 0)
