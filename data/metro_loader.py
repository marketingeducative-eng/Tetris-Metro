"""
Metro Network Loader
Loads and validates Barcelona Metro network data from JSON
"""
import json
import os
import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union
from pathlib import Path


@dataclass
class Station:
    """Represents a metro station with name, contextual description, and zone"""
    id: str = ""
    name: str = ""
    zone: str = ""  # Barcelona district/zone (e.g., "Eixample", "Ciutat Vella")
    description: str = ""  # Max 60 characters contextual description
    tourist_highlight: bool = False
    tourist_priority: int = 0
    tourist_tags: List[str] = field(default_factory=list)
    tourist_tip_ca: str = ""
    image_url: str = ""  # URL to tourist image for Ken Burns animation
    
    def __post_init__(self):
        """Normalize station data with safe defaults"""
        self.name = "" if self.name is None else str(self.name)
        self.zone = "" if self.zone is None else str(self.zone)
        self.description = "" if self.description is None else str(self.description)
        self.tourist_tip_ca = "" if self.tourist_tip_ca is None else str(self.tourist_tip_ca)
        self.image_url = "" if self.image_url is None else str(self.image_url)

        if len(self.description) > 60:
            self.description = self.description[:60]
        if len(self.tourist_tip_ca) > 120:
            self.tourist_tip_ca = self.tourist_tip_ca[:120]

        self.tourist_highlight = bool(self.tourist_highlight)
        try:
            self.tourist_priority = int(self.tourist_priority or 0)
        except (TypeError, ValueError):
            self.tourist_priority = 0

        if self.tourist_tags is None:
            self.tourist_tags = []
        elif isinstance(self.tourist_tags, str):
            self.tourist_tags = [self.tourist_tags]
        else:
            try:
                self.tourist_tags = list(self.tourist_tags)
            except TypeError:
                self.tourist_tags = []

        if not self.id:
            self.id = normalize_station_id(self.name)


@dataclass
class Line:
    """Represents a metro line"""
    id: str = ""
    name: str = ""
    color: str = "#000000"
    endpoints: Dict[str, str] = field(default_factory=dict)  # {"from": "...", "to": "..."}
    stations: List[Station] = field(default_factory=list)
    
    def __post_init__(self):
        """Normalize line data with safe defaults"""
        self.id = "" if self.id is None else str(self.id)
        self.name = "" if self.name is None else str(self.name)
        self.color = self.color or "#000000"
        if not self.id:
            self.id = "UNKNOWN"
        if not self.name:
            self.name = self.id

        if self.stations is None:
            self.stations = []

        if not isinstance(self.endpoints, dict):
            self.endpoints = {}

        station_names = [s.name for s in self.stations]
        from_name = self.endpoints.get("from", "")
        to_name = self.endpoints.get("to", "")

        if station_names:
            if from_name not in station_names:
                from_name = station_names[0]
            if to_name not in station_names:
                to_name = station_names[-1]

        self.endpoints = {"from": from_name, "to": to_name}
    
    def get_station_index(self, station_name: str) -> Optional[int]:
        """
        Get the index of a station in this line
        
        Args:
            station_name: Name of the station
            
        Returns:
            Index (0-based) or None if not found
        """
        for i, station in enumerate(self.stations):
            if station.name == station_name:
                return i
        return None
    
    def get_station(self, index: int) -> Optional[Station]:
        """
        Get station at given index
        
        Args:
            index: Station index
            
        Returns:
            Station object or None if out of bounds
        """
        if 0 <= index < len(self.stations):
            return self.stations[index]
        return None
    
    def get_station_names(self) -> List[str]:
        """Get list of all station names"""
        return [s.name for s in self.stations]
    
    def __len__(self):
        """Return number of stations"""
        return len(self.stations)


@dataclass
class MetroNetwork:
    """Represents a complete metro network"""
    network: str
    lines: List[Line] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate network data"""
        # Check for duplicate line IDs
        line_ids = [line.id for line in self.lines]
        if len(line_ids) != len(set(line_ids)):
            duplicates = [lid for lid in line_ids if line_ids.count(lid) > 1]
            raise ValueError(f"Duplicate line IDs found: {set(duplicates)}")
    
    def get_line(self, line_id: str) -> Optional[Line]:
        """
        Get a line by its ID
        
        Args:
            line_id: Line identifier (e.g., "L3")
            
        Returns:
            Line object or None if not found
        """
        for line in self.lines:
            if line.id == line_id:
                return line
        return None
    
    def get_all_stations(self) -> List[str]:
        """Get all unique station names across all lines"""
        all_stations = set()
        for line in self.lines:
            all_stations.update(s.name for s in line.stations)
        return sorted(all_stations)
    
    def __len__(self):
        """Return number of lines"""
        return len(self.lines)


def validate_overlay(network: "MetroNetwork", overlay: Dict[str, dict]):
    """Log overlay mismatches when DEBUG=1."""
    if os.getenv("DEBUG") != "1":
        return
    overlay = overlay or {}
    station_ids = set()
    for line in network.lines:
        for station in line.stations:
            station_ids.add(normalize_station_id(station.name))

    matched_keys = station_ids.intersection(set(overlay.keys()))
    unmatched_overlay_keys = sorted([key for key in overlay.keys() if key not in matched_keys])
    stations_without_overlay = sorted([sid for sid in station_ids if sid not in overlay])

    print("\n" + "=" * 60)
    print("TOURIST OVERLAY MERGE DEBUG")
    print("=" * 60)
    print(f"Total stations in network: {len(station_ids)}")
    print(f"Overlay station keys count: {len(overlay)}")
    print(f"Matched count: {len(matched_keys)}")
    print(f"\nOverlay keys with no matching station: {len(unmatched_overlay_keys)}")
    if unmatched_overlay_keys:
        print(f"  First 10: {unmatched_overlay_keys[:10]}")
    print(f"\nStations with no overlay entry: {len(stations_without_overlay)}")
    if stations_without_overlay:
        print(f"  First 10: {stations_without_overlay[:10]}")
    print("=" * 60 + "\n")


def load_metro_network(path: str) -> MetroNetwork:
    """
    Load metro network from JSON file with validation
    
    Args:
        path: Path to JSON file
        
    Returns:
        MetroNetwork object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If validation fails
        json.JSONDecodeError: If JSON is invalid
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Metro data file not found: {path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Validate top-level structure
    if "network" not in data:
        raise ValueError("JSON must contain 'network' field")
    if "lines" not in data:
        raise ValueError("JSON must contain 'lines' field")
    if not isinstance(data["lines"], list):
        raise ValueError("'lines' must be a list")
    
    tourist_data = {}
    tourist_path = file_path.parent / "tourist_ca.json"
    if tourist_path.exists():
        try:
            with open(tourist_path, 'r', encoding='utf-8') as tourist_file:
                tourist_payload = json.load(tourist_file)
            tourist_data = tourist_payload.get("stations", {}) if isinstance(tourist_payload, dict) else {}
        except (OSError, json.JSONDecodeError):
            tourist_data = {}

    # Create Line objects (validation happens in __post_init__)
    lines = []
    for line_data in data["lines"]:
        try:
            # Parse stations - support both old format (strings) and new format (dicts)
            stations_raw = line_data.get("stations", [])
            stations = []
            for station_data in stations_raw:
                if isinstance(station_data, str):
                    # Old format: just a string name
                    stations.append(Station(name=station_data))
                elif isinstance(station_data, dict):
                    # New format: dict with name, optional description, and optional zone
                    tourist_tip = station_data.get("tourist_tip_ca", station_data.get("tourist_info", ""))
                    stations.append(Station(
                        id=station_data.get("id", ""),
                        name=station_data.get("name", ""),
                        description=station_data.get("description", ""),
                        zone=station_data.get("zone", ""),
                        tourist_highlight=station_data.get("tourist_highlight", False),
                        tourist_priority=station_data.get("tourist_priority", 0),
                        tourist_tags=station_data.get("tourist_tags", []),
                        tourist_tip_ca=tourist_tip,
                        image_url=station_data.get("image_url", "")
                    ))
                else:
                    raise ValueError(f"Invalid station data type: {type(station_data)}")
            
            line = Line(
                id=line_data.get("id", ""),
                name=line_data.get("name", ""),
                color=line_data.get("color", "#000000"),
                endpoints=line_data.get("endpoints", {}),
                stations=stations
            )
            lines.append(line)
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error loading line {line_data.get('id', 'unknown')}: {e}")
    
    # Create and validate network
    network = MetroNetwork(
        network=data["network"],
        lines=lines
    )

    # Merge tourist overlay data
    if tourist_data:
        for line in network.lines:
            for station in line.stations:
                station_id = normalize_station_id(station.name)
                entry = tourist_data.get(station_id)
                if not entry:
                    continue
                if "zone" in entry:
                    station.zone = "" if entry.get("zone") is None else str(entry.get("zone", ""))
                if "one_liner_ca" in entry:
                    station.description = "" if entry.get("one_liner_ca") is None else str(entry.get("one_liner_ca", ""))
                if "highlight" in entry:
                    station.tourist_highlight = bool(entry.get("highlight", False))
                if "priority" in entry:
                    try:
                        station.tourist_priority = int(entry.get("priority") or 0)
                    except (TypeError, ValueError):
                        station.tourist_priority = 0
                if "tags" in entry:
                    tags = entry.get("tags")
                    if tags is None:
                        station.tourist_tags = []
                    elif isinstance(tags, list):
                        station.tourist_tags = tags
                    elif isinstance(tags, str):
                        station.tourist_tags = [tags]
                    else:
                        station.tourist_tags = []
                if "tip_ca" in entry:
                    station.tourist_tip_ca = "" if entry.get("tip_ca") is None else str(entry.get("tip_ca", ""))
                if "image_url" in entry:
                    station.image_url = "" if entry.get("image_url") is None else str(entry.get("image_url", ""))
    validate_overlay(network, tourist_data)
    
    return network


def normalize_station_id(name: str) -> str:
    """Normalize a station display name into a station_id key."""
    if not name:
        return ""
    text = name.upper()
    text = text.replace("·", "_").replace("-", "_")
    text = text.replace(" ", "_")
    text = text.replace("'", "").replace("’", "").replace(".", "")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def get_line(network: MetroNetwork, line_id: str) -> Optional[Line]:
    """
    Convenience function to get a line from network
    
    Args:
        network: MetroNetwork object
        line_id: Line identifier
        
    Returns:
        Line object or None
    """
    return network.get_line(line_id)


def get_station_index(network: MetroNetwork, line_id: str, station_name: str) -> Optional[int]:
    """
    Get the index of a station in a specific line
    
    Args:
        network: MetroNetwork object
        line_id: Line identifier
        station_name: Name of the station
        
    Returns:
        Index (0-based) or None if line or station not found
    """
    line = network.get_line(line_id)
    if line is None:
        return None
    return line.get_station_index(station_name)


if __name__ == "__main__":
    # Test normalize_station_id function
    print("=" * 60)
    print("TESTING normalize_station_id()")
    print("=" * 60)
    
    test_cases = [
        ("Passeig de Gràcia", "PASSEIG_DE_GRACIA"),
        ("Paral·lel", "PARAL_LEL"),
        ("Plaça d'Espanya", "PLACA_DESPANYA"),
        ("Sants Estació", "SANTS_ESTACIO"),
        ("Sagrada Família", "SAGRADA_FAMILIA"),
        ("Lesseps", "LESSEPS"),
        ("Arc de Triomf", "ARC_DE_TRIOMF"),
        ("Drassanes", "DRASSANES"),
        ("Jaume I", "JAUME_I"),
        ("Barceloneta", "BARCELONETA"),
    ]
    
    print("\nTest cases:")
    all_passed = True
    for input_name, expected in test_cases:
        result = normalize_station_id(input_name)
        passed = result == expected
        all_passed = all_passed and passed
        status = "✓" if passed else "✗"
        print(f"  {status} normalize_station_id('{input_name}')")
        print(f"     Expected: {expected}")
        print(f"     Got:      {result}")
        if not passed:
            print(f"     ⚠ MISMATCH!")
        print()
    
    if all_passed:
        print("✅ All normalize_station_id() tests passed!")
    else:
        print("❌ Some normalize_station_id() tests failed!")
    
    # Test manual loading
    print("\n" + "=" * 60)
    print("TESTING METRO NETWORK LOADER")
    print("=" * 60)
    
    # Load network
    data_path = Path(__file__).parent / "barcelona_metro_lines_stations.json"
    print(f"\n📂 Loading from: {data_path}")
    
    try:
        network = load_metro_network(str(data_path))
        print(f"✓ Network loaded: {network.network}")
        print(f"✓ Total lines: {len(network)}")
        print(f"✓ Total unique stations: {len(network.get_all_stations())}")
        
        # Test L3
        print("\n" + "=" * 60)
        print("TESTING LINE L3")
        print("=" * 60)
        
        l3 = get_line(network, "L3")
        if l3:
            print(f"\n🚇 Line: {l3.name} ({l3.id})")
            print(f"   Color: {l3.color}")
            print(f"   Endpoints: {l3.endpoints['from']} ↔ {l3.endpoints['to']}")
            print(f"   Number of stations: {len(l3)}")
            print(f"\n   Stations:")
            for i, station in enumerate(l3.stations):
                marker = "🔴" if station.name in [l3.endpoints['from'], l3.endpoints['to']] else "⚪"
                desc_text = f" - {station.description}" if station.description else ""
                print(f"   {marker} {i:2d}. {station.name}{desc_text}")
        else:
            print("❌ Line L3 not found")
        
        # Test station index
        print("\n" + "=" * 60)
        print("TESTING STATION INDEX - 'Liceu'")
        print("=" * 60)
        
        liceu_index = get_station_index(network, "L3", "Liceu")
        if liceu_index is not None:
            print(f"\n🎯 Station 'Liceu' found on L3 at index: {liceu_index}")
            print(f"   Position: {liceu_index + 1}/{len(l3)} stations")
            
            # Show context
            if liceu_index > 0:
                print(f"   Previous: {l3.stations[liceu_index - 1].name}")
            print(f"   ➜ Current: {l3.stations[liceu_index].name}")
            if liceu_index < len(l3) - 1:
                print(f"   Next: {l3.stations[liceu_index + 1].name}")
        else:
            print("❌ Station 'Liceu' not found on L3")
        
        # Additional tests
        print("\n" + "=" * 60)
        print("ADDITIONAL VALIDATION TESTS")
        print("=" * 60)
        
        # Test non-existent line
        non_existent = get_line(network, "L99")
        print(f"\n✓ Non-existent line L99: {non_existent}")
        
        # Test non-existent station
        non_existent_station = get_station_index(network, "L3", "Nonexistent Station")
        print(f"✓ Non-existent station index: {non_existent_station}")
        
        # Test all lines summary
        print("\n📊 All Lines Summary:")
        for line in network.lines:
            print(f"   {line.id}: {line.name} - {len(line)} stations")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
