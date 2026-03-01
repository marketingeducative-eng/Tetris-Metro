"""
Example: Running a deterministic game with a fixed random seed.

This demonstrates how to use the random_seed parameter for:
1. Reproducible game sessions for testing
2. Recording and replaying game sequences
3. Debugging specific scenarios

Run this script to see the same token sequence every time.
"""
from game_propera_parada import ProximaParadaApp

if __name__ == '__main__':
    # Use a fixed seed for reproducible gameplay
    # The same seed will always produce the same token sequences
    FIXED_SEED = 42
    
    print("=" * 60)
    print("DETERMINISTIC GAME MODE")
    print("=" * 60)
    print(f"Running with random_seed={FIXED_SEED}")
    print()
    print("This game will have the same token sequences every time.")
    print("Perfect for:")
    print("  - Testing game mechanics")
    print("  - Recording speedruns")
    print("  - Debugging specific scenarios")
    print("  - Automated testing")
    print()
    print("Expected first few rounds:")
    print("  Round 1: Palau Reial, Paral·lel, Zona Universitària")
    print("  Round 2: Drassanes, Espanya, Maria Cristina")
    print("  Round 3: Les Corts, Plaça del Centre, Zona Universitària")
    print()
    print("Press Ctrl+C to exit or close the window")
    print("=" * 60)
    
    app = ProximaParadaApp(random_seed=FIXED_SEED)
    app.run()

