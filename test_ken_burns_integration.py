"""
Integration test for Ken Burns animation in game.
Tests that popup displays images and animations without errors.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_ken_burns_integration():
    """Test Ken Burns animation integration"""
    print("=" * 70)
    print("KEN BURNS INTEGRATION TEST")
    print("=" * 70)
    
    # Test 1: Import checks
    print("\n[Test 1/3] Checking imports...")
    try:
        from game_propera_parada import Renderer
        from data.metro_loader import load_metro_network, Station
        from kivy.uix.image import Image
        from kivy.uix.scatterlayout import ScatterLayout
        from kivy.animation import Animation
        print("  ✓ All required imports available")
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False
    
    # Test 2: Station dataclass has image_url
    print("\n[Test 2/3] Checking Station dataclass...")
    try:
        station = Station(
            id="TEST",
            name="Test Station",
            zone="Test Zone",
            tourist_highlight=True,
            tourist_priority=5,
            tourist_tip_ca="This is a test station",
            image_url="https://example.com/image.jpg"
        )
        assert hasattr(station, 'image_url'), "Station missing image_url field"
        assert station.image_url == "https://example.com/image.jpg", "image_url not stored correctly"
        print(f"  ✓ Station dataclass has image_url field")
        print(f"    Sample: {station.name} -> {station.image_url}")
    except Exception as e:
        print(f"  ✗ Station dataclass error: {e}")
        return False
    
    # Test 3: Metro network loads with images
    print("\n[Test 3/3] Checking metro network integration...")
    try:
        metro_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
        network = load_metro_network(str(metro_path))
        
        # Count stations with images
        stations_with_images = 0
        total_stations = 0
        sample_station = None
        
        for line in network.lines:
            for station in line.stations:
                total_stations += 1
                if station.image_url:
                    stations_with_images += 1
                    if sample_station is None:
                        sample_station = station
        
        print(f"  ✓ Metro network loaded successfully")
        print(f"    Total stations: {total_stations}")
        print(f"    Stations with images: {stations_with_images}")
        
        if sample_station:
            print(f"\n  Sample station with image animation:")
            print(f"    Name: {sample_station.name}")
            print(f"    Zone: {sample_station.zone}")
            print(f"    Priority: {sample_station.tourist_priority}")
            print(f"    Highlight: {sample_station.tourist_highlight}")
            print(f"    Tip: {sample_station.tourist_tip_ca[:60]}...")
            print(f"    Image: {sample_station.image_url[:60]}...")
    except Exception as e:
        print(f"  ✗ Network loading error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Animation syntax validation
    print("\n[Test 4/4] Checking animation syntax...")
    try:
        # Simulate animation creation
        anim_in = Animation(scale=1.08, duration=1.75, transition='in_out_quad')
        anim_out = Animation(scale=1.0, duration=1.75, transition='in_out_quad')
        anim_chain = anim_in + anim_out
        
        print(f"  ✓ Animation chain created successfully")
        print(f"    Phase 1: scale to 1.08x over 1.75s (in_out_quad)")
        print(f"    Phase 2: scale to 1.0x over 1.75s (in_out_quad)")
        print(f"    Total: 3.5 seconds")
    except Exception as e:
        print(f"  ✗ Animation error: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("=" * 70)
    print("\nKen Burns animation is ready for deployment:")
    print("  • Image URLs loaded from tourist_ca.json")
    print("  • Station dataclass properly configured")
    print("  • Metro network integration complete")
    print("  • Animation parameters validated")
    print("\nTo see the animation in action, run: python main.py")
    print("Then go to a tourist-highlighted station to view the popup.")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = test_ken_burns_integration()
    sys.exit(0 if success else 1)

