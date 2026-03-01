"""
Metro Content Manager - Loads and serves Barcelona metro stations
"""
import json
import random
from pathlib import Path


class MetroContentManager:
    """Manages metro station data"""
    
    def __init__(self, data_path='data/stations.json'):
        self.data_path = data_path
        self.stations = []
        self.metro_lines = {}
        self._load_content()
    
    def _load_content(self):
        """Load stations from JSON"""
        try:
            path = Path(self.data_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stations = data.get('stations', [])
                    self.metro_lines = data.get('metro_lines', {})
                    
                    print(f"Content loaded: {len(self.stations)} stations, {len(self.metro_lines)} lines")
            else:
                self._create_fallback_data()
        except Exception as e:
            print(f"Error loading content: {e}")
            self._create_fallback_data()
    
    def _create_fallback_data(self):
        """Fallback data if JSON fails"""
        self.stations = [
            {
                'station_id': 'catalunya',
                'name': 'Catalunya',
                'name_short': 'Catalunya',
                'lines': ['L1', 'L3'],
                'difficulty': 'A1',
                'frequency': 'high'
            },
            {
                'station_id': 'sagrada_familia',
                'name': 'Sagrada Família',
                'name_short': 'Sagrada F.',
                'lines': ['L2', 'L5'],
                'difficulty': 'A2',
                'frequency': 'high'
            },
            {
                'station_id': 'sants',
                'name': 'Sants Estació',
                'name_short': 'Sants',
                'lines': ['L3', 'L5'],
                'difficulty': 'A1',
                'frequency': 'high'
            }
        ]
        self.metro_lines = {
            'L1': {'name': 'Línia 1', 'color': '#E3000B'},
            'L2': {'name': 'Línia 2', 'color': '#9B3FA7'},
            'L3': {'name': 'Línia 3', 'color': '#049140'},
            'L4': {'name': 'Línia 4', 'color': '#FFD200'},
            'L5': {'name': 'Línia 5', 'color': '#0082C6'}
        }
    
    def get_random_station(self, difficulty=None):
        """
        Get random station by difficulty
        
        Args:
            difficulty: 'A1', 'A2', or 'B1' (None = any)
        
        Returns:
            Station dict
        """
        if not self.stations:
            return None
        
        # Filter by difficulty
        candidates = self.stations
        if difficulty:
            candidates = [s for s in self.stations if s.get('difficulty') == difficulty]
        
        if not candidates:
            candidates = self.stations
        
        # Weighted random by frequency
        weights = []
        for station in candidates:
            freq = station.get('frequency', 'medium')
            weight = {'high': 3, 'medium': 2, 'low': 1}.get(freq, 2)
            weights.append(weight)
        
        return random.choices(candidates, weights=weights)[0]
    
    def get_random_line(self):
        """Get random metro line ID"""
        if self.metro_lines:
            return random.choice(list(self.metro_lines.keys()))
        return 'L1'
    
    def format_station_label(self, station_data):
        """Format station for display"""
        if not station_data:
            return ""
        
        name = station_data.get('name_short', station_data.get('name', ''))
        lines = station_data.get('lines', [])
        
        if lines:
            return f"{name} ({', '.join(lines)})"
        return name
