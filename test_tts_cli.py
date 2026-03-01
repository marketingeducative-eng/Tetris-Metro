"""
Simple CLI test for TTS service
"""
from core.tts import get_tts, speak, announce_station, announce_line
from data.metro_loader import load_metro_network
from pathlib import Path
import time


def main():
    print("=" * 60)
    print("TTS SERVICE - SIMPLE TEST")
    print("=" * 60)
    
    # Initialize TTS
    print("\n1. Initializing TTS service...")
    tts = get_tts()
    
    print(f"   Platform: {'Android' if tts.tts else 'Desktop'}")
    print(f"   Initialized: {tts.is_initialized}")
    print(f"   Available: {tts.is_available}")
    print(f"   Language: {tts.language}_{tts.country}")
    
    if not tts.is_available:
        print("\n   ℹ️  Running in MOCK mode (desktop)")
        print("   On Android, this would use real TTS")
    
    # Load metro data
    print("\n2. Loading metro data...")
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    network = load_metro_network(str(data_path))
    l3 = network.get_line("L3")
    print(f"   ✓ Loaded {l3.name} with {len(l3)} stations")
    
    # Test basic speech
    print("\n3. Testing basic speech...")
    print("   📢 Speaking: 'Hola, benvingut al metro de Barcelona'")
    speak("Hola, benvingut al metro de Barcelona")
    time.sleep(0.5)
    
    # Test line announcement
    print("\n4. Testing line announcement...")
    print(f"   📢 Announcing: {l3.name}")
    announce_line(l3.name)
    time.sleep(0.5)
    
    # Test station announcements
    print("\n5. Testing station announcements...")
    test_stations = ["Liceu", "Catalunya", "Passeig de Gràcia"]
    for station in test_stations:
        print(f"   📢 Announcing station: {station}")
        announce_station(station, interrupt=False)
        time.sleep(0.3)
    
    # Test sequence
    print("\n6. Testing sequence announcement...")
    print(f"   📢 Announcing: Liceu + {l3.name}")
    tts.announce_sequence("Liceu", l3.name)
    time.sleep(0.5)
    
    # Test speech parameters
    print("\n7. Testing speech parameters...")
    print("   ⚙️  Setting speech rate to 1.2x")
    tts.set_speech_rate(1.2)
    
    print("   ⚙️  Setting pitch to 1.0")
    tts.set_pitch(1.0)
    
    print("   📢 Speaking with new parameters")
    speak("Aquesta és una prova amb velocitat augmentada")
    time.sleep(0.5)
    
    # Test interruption
    print("\n8. Testing interruption...")
    print("   📢 Speaking long text...")
    speak("Aquest és un text molt llarg que serà interromput", interrupt=False)
    time.sleep(0.2)
    print("   ⏸️  Interrupting with new speech...")
    speak("Interrupció", interrupt=True)
    
    # Test stop
    print("\n9. Testing stop...")
    speak("Aquest text serà aturat", interrupt=False)
    time.sleep(0.1)
    print("   ⏹️  Stopping speech...")
    tts.stop()
    
    print("\n10. Cleanup...")
    tts.shutdown()
    print("   ✓ TTS service shutdown complete")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETED")
    print("=" * 60)
    print("\nNotes:")
    print("- On desktop: TTS runs in mock mode (check logs)")
    print("- On Android: Real TTS with Catalan voice")
    print("- Check Kivy logs for detailed TTS output")
    print()


if __name__ == "__main__":
    main()
