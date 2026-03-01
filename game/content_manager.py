"""
Content Manager - loads and manages station data from JSON
"""
import json
import random
import os


class ContentManager:
    """
    Manages game content (stations, lines) loaded from JSON files
    """
    
    def __init__(self, data_path='data/stations.json'):
        """
        Initialize content manager
        
        Args:
            data_path: Path to stations JSON file
        """
        self.data_path = data_path
        self.stations = []
        self.metro_lines = {}
        self.version = "unknown"
        
        self._load_content()
    
    def _load_content(self):
        """Load content from JSON file"""
        try:
            # Try to load from data path
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                # Fallback to default minimal data
                print(f"Warning: {self.data_path} not found, using default data")
                data = self._get_default_data()
            
            self.version = data.get('version', 'unknown')
            self.metro_lines = data.get('metro_lines', {})
            self.stations = data.get('stations_pool', [])
            
            print(f"Content loaded: {len(self.stations)} stations, {len(self.metro_lines)} lines")
            
        except Exception as e:
            print(f"Error loading content: {e}")
            # Use minimal fallback data
            data = self._get_default_data()
            self.stations = data['stations_pool']
            self.metro_lines = data['metro_lines']
    
    def _get_default_data(self):
        """Fallback minimal data if JSON not available"""
        return {
            "version": "1.0",
            "metro_lines": {
                "L1": {"name": "Línia 1", "color": "#E2001A"},
                "L3": {"name": "Línia 3", "color": "#00A651"}
            },
            "stations_pool": [
                {
                    "id": "st_001",
                    "name": "Catalunya",
                    "name_short": "Catalunya",
                    "lines": ["L1", "L3"],
                    "difficulty": "A1",
                    "frequency": "high"
                },
                {
                    "id": "st_002",
                    "name": "Sagrada Família",
                    "name_short": "Sagrada Família",
                    "lines": ["L2", "L5"],
                    "difficulty": "A1",
                    "frequency": "high"
                },
                {
                    "id": "st_003",
                    "name": "Espanya",
                    "name_short": "Espanya",
                    "lines": ["L1", "L3"],
                    "difficulty": "A1",
                    "frequency": "high"
                }
            ]
        }
    
    def get_random_station(self, difficulty=None):
        """
        Get random station, optionally filtered by difficulty
        
        Args:
            difficulty: Filter by difficulty level (A1, A2, B1) or None for any
            
        Returns:
            Station dictionary or None
        """
        if not self.stations:
            return None
        
        # Filter by difficulty if specified
        if difficulty:
            filtered = [s for s in self.stations if s.get('difficulty') == difficulty]
            pool = filtered if filtered else self.stations
        else:
            pool = self.stations
        
        # Weight by frequency
        weights = []
        for station in pool:
            freq = station.get('frequency', 'medium')
            if freq == 'high':
                weights.append(3)
            elif freq == 'medium':
                weights.append(2)
            else:
                weights.append(1)
        
        return random.choices(pool, weights=weights, k=1)[0]
    
    def get_station_by_id(self, station_id):
        """
        Get station by ID
        
        Args:
            station_id: Station identifier
            
        Returns:
            Station dictionary or None
        """
        for station in self.stations:
            if station.get('id') == station_id:
                return station
        return None
    
    def get_line_info(self, line_id):
        """
        Get metro line information
        
        Args:
            line_id: Line identifier (e.g., "L1")
            
        Returns:
            Line dictionary or None
        """
        return self.metro_lines.get(line_id)
    
    def format_station_label(self, station):
        """
        Format station for display
        
        Args:
            station: Station dictionary
            
        Returns:
            Formatted string
        """
        if not station:
            return "Sense estació"
        
        name = station.get('name_short', station.get('name', 'Unknown'))
        lines = station.get('lines', [])
        
        if lines:
            lines_str = ' · '.join(lines)
            return f"{name} ({lines_str})"
        else:
            return name
    
    def get_station_hint(self, station):
        """
        Get hint/description for a station
        
        Args:
            station: Station dictionary
            
        Returns:
            Hint string
        """
        if not station:
            return ""
        
        lines = station.get('lines', [])
        if not lines:
            return ""
        
        # Get line info
        line_names = []
        for line_id in lines:
            line_info = self.get_line_info(line_id)
            if line_info:
                line_names.append(line_info['name'])
        
        if line_names:
            return f"Línies: {', '.join(line_names)}"
        
        return ""
