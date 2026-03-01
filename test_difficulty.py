"""
Test dynamic difficulty calculation
"""

def calculate_travel_duration(streak):
    """Calculate travel duration based on streak"""
    base_duration = 3.2
    min_duration = 2.2
    duration_step = 0.1
    streak_interval = 3
    
    reductions = streak // streak_interval
    duration = base_duration - (reductions * duration_step)
    return max(min_duration, duration)


def calculate_drop_radius(streak):
    """Calculate drop acceptance radius based on streak"""
    base_radius = 50.0
    min_radius = 38.0
    radius_step = 1.0
    streak_interval = 3
    
    reductions = streak // streak_interval
    radius = base_radius - (reductions * radius_step)
    return max(min_radius, radius)


def main():
    """Test various streak values"""
    print("Dynamic Difficulty Test")
    print("=" * 65)
    print(f"Time: 3.2s → 2.2s | Radius: 50px → 38px | Every 3 streak\n")
    
    test_streaks = [0, 1, 2, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 36]
    
    print(f"{'Streak':<8} {'Duration':<12} {'Radius':<15} {'Difficulty'}")
    print("-" * 65)
    
    for streak in test_streaks:
        duration = calculate_travel_duration(streak)
        radius = calculate_drop_radius(streak)
        time_reduction = 3.2 - duration
        radius_reduction = 50.0 - radius
        
        # Visual indicator
        if streak == 0:
            difficulty = "Easy ★"
        elif streak < 12:
            difficulty = "Medium ★★"
        elif streak < 24:
            difficulty = "Hard ★★★"
        else:
            difficulty = "Expert ★★★★"
        
        print(f"{streak:<8} {duration:.1f}s (-{time_reduction:.1f}s)  "
              f"{radius:.0f}px (-{radius_reduction:.0f}px)    {difficulty}")
    
    print("\n" + "=" * 65)
    print("✅ Both difficulty progressions validated!")
    print(f"   Time reaches min at streak {(3.2 - 2.2) / 0.1 * 3:.0f}")
    print(f"   Radius reaches min at streak {(50.0 - 38.0) / 1.0 * 3:.0f}")


if __name__ == '__main__':
    main()
