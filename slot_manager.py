"""
SlotManager - Core game logic for station placement
Pure Python, no Kivy dependencies
"""
from typing import Dict, List, Set, Optional


class SlotManager:
    """
    Manages the slot-based station placement game logic
    
    Rules:
    - Players must place stations in order at the correct slot (next_index)
    - Can place "ahead" within a window, but must still place the next one correctly
    - Failed placements go to parking; game over when parking is full
    """
    
    def __init__(self, 
                 ordered_station_ids: List[str],
                 window_size: int = 3,
                 parking_capacity: int = 3):
        """
        Initialize slot manager
        
        Args:
            ordered_station_ids: List of station IDs in correct order
            window_size: How many stations ahead can be placed (default: 3)
            parking_capacity: Max failed tokens before game over (default: 3)
        """
        self.ordered_station_ids = ordered_station_ids
        self.window_size = window_size
        self.parking_capacity = parking_capacity
        
        # Game state
        self.next_index = 0
        self.placed: Set[int] = set()  # Set of placed slot indices
        self.parking_count = 0
        self.streak = 0
        self.total_score = 0
        
        # Stats
        self.perfect_count = 0
        self.ahead_count = 0
        self.total_attempts = 0
    
    def attempt_place(self, station_id: str, slot_index: int) -> Dict:
        """
        Attempt to place a station at a specific slot
        
        Args:
            station_id: ID of the station being placed
            slot_index: Target slot index (0-based)
            
        Returns:
            Dict with keys:
                - accepted: bool - Was placement accepted?
                - perfect: bool - Was it the exact next station?
                - next_index: int - Updated next_index
                - streak: int - Current streak
                - feedback: str - Feedback message in Catalan
                - game_over: bool - Is game over?
                - points: int - Points earned
                - parking_count: int - Current parking count
        """
        self.total_attempts += 1
        
        # Default result
        result = {
            "accepted": False,
            "perfect": False,
            "next_index": self.next_index,
            "streak": self.streak,
            "feedback": "",
            "game_over": False,
            "points": 0,
            "parking_count": self.parking_count
        }
        
        # Check if game is already over
        if self.is_game_over():
            result["game_over"] = True
            result["feedback"] = "Joc acabat!"
            return result
        
        # Rule 1: Must place at next_index slot
        if slot_index != self.next_index:
            result["accepted"] = False
            result["feedback"] = "Col·loca-la al següent punt"
            # Token is lost - goes to parking
            self.parking_count += 1
            result["parking_count"] = self.parking_count
            
            if self.parking_count >= self.parking_capacity:
                result["game_over"] = True
                result["feedback"] = "Aparcament ple! Joc acabat"
            
            # Streak is broken on wrong slot
            self.streak = 0
            result["streak"] = self.streak
            
            return result
        
        # Rule 2: Check if station is within the valid window
        window_end = min(self.next_index + self.window_size, len(self.ordered_station_ids))
        valid_window = self.ordered_station_ids[self.next_index:window_end]
        
        if station_id not in valid_window:
            # Station not in valid window - rejected
            result["accepted"] = False
            result["feedback"] = f"Aquesta estació no correspon aquí"
            
            # Token goes to parking
            self.parking_count += 1
            result["parking_count"] = self.parking_count
            
            if self.parking_count >= self.parking_capacity:
                result["game_over"] = True
                result["feedback"] = "Aparcament ple! Joc acabat"
            
            # Streak is broken
            self.streak = 0
            result["streak"] = self.streak
            
            return result
        
        # Station is in valid window - accepted!
        result["accepted"] = True
        self.placed.add(slot_index)
        
        # Check if it's the perfect next station
        expected_station = self.ordered_station_ids[self.next_index]
        
        if station_id == expected_station:
            # Perfect placement!
            result["perfect"] = True
            result["feedback"] = f"Perfecte! {station_id}"
            
            # Increment streak
            self.streak += 1
            result["streak"] = self.streak
            
            # Calculate points
            points = self.points_for(perfect=True, streak=self.streak)
            result["points"] = points
            self.total_score += points
            
            # Move to next index
            self.next_index += 1
            result["next_index"] = self.next_index
            
            # Check if we've completed all stations
            if self.next_index >= len(self.ordered_station_ids):
                result["game_over"] = True
                result["feedback"] = "Enhorabona! Has completat totes les estacions!"
            
            self.perfect_count += 1
            
        else:
            # Placed ahead (valid but not perfect)
            result["perfect"] = False
            result["feedback"] = f"Estació acceptada però fora d'ordre"
            
            # Don't increment streak (but don't break it either)
            # Don't increment next_index - must place the correct next one
            
            # Calculate points (lower for non-perfect)
            points = self.points_for(perfect=False, streak=self.streak)
            result["points"] = points
            self.total_score += points
            
            self.ahead_count += 1
        
        return result
    
    def points_for(self, perfect: bool, streak: int) -> int:
        """
        Calculate points for a placement
        
        Args:
            perfect: Is this a perfect (in-order) placement?
            streak: Current streak value
            
        Returns:
            Points earned
        """
        if perfect:
            # Perfect placement: base 100 + streak bonus
            base_points = 100
            streak_bonus = streak * 10
            return base_points + streak_bonus
        else:
            # Ahead placement: fixed 50 points (no streak bonus)
            return 50
    
    def is_game_over(self) -> bool:
        """Check if game is over"""
        # Game over if parking is full
        if self.parking_count >= self.parking_capacity:
            return True
        
        # Game over if all stations placed
        if self.next_index >= len(self.ordered_station_ids):
            return True
        
        return False
    
    def get_progress(self) -> float:
        """Get completion progress (0.0 to 1.0)"""
        if not self.ordered_station_ids:
            return 0.0
        return self.next_index / len(self.ordered_station_ids)
    
    def get_stats(self) -> Dict:
        """Get game statistics"""
        return {
            "next_index": self.next_index,
            "placed_count": len(self.placed),
            "parking_count": self.parking_count,
            "streak": self.streak,
            "total_score": self.total_score,
            "perfect_count": self.perfect_count,
            "ahead_count": self.ahead_count,
            "total_attempts": self.total_attempts,
            "progress": self.get_progress(),
            "game_over": self.is_game_over()
        }
    
    def reset(self):
        """Reset game state"""
        self.next_index = 0
        self.placed.clear()
        self.parking_count = 0
        self.streak = 0
        self.total_score = 0
        self.perfect_count = 0
        self.ahead_count = 0
        self.total_attempts = 0


# ============================================================================
# UNIT TESTS
# ============================================================================

def test_perfect_placement():
    """Test Case 1: Perfect in-order placement"""
    print("=" * 60)
    print("TEST 1: Perfect In-Order Placement")
    print("=" * 60)
    
    stations = ["Liceu", "Catalunya", "Passeig de Gràcia", "Diagonal"]
    manager = SlotManager(stations, window_size=3, parking_capacity=3)
    
    # Place first station perfectly
    result = manager.attempt_place("Liceu", 0)
    
    assert result["accepted"] == True, "Should accept correct station at correct slot"
    assert result["perfect"] == True, "Should be perfect placement"
    assert result["next_index"] == 1, "Should advance to next slot"
    assert result["streak"] == 1, "Streak should be 1"
    assert result["points"] == 110, f"Points should be 110 (100 + 1*10), got {result['points']}"
    assert result["game_over"] == False, "Game should not be over"
    
    print(f"✓ Placed 'Liceu' at slot 0:")
    print(f"  - Accepted: {result['accepted']}")
    print(f"  - Perfect: {result['perfect']}")
    print(f"  - Next index: {result['next_index']}")
    print(f"  - Streak: {result['streak']}")
    print(f"  - Points: {result['points']}")
    print(f"  - Feedback: {result['feedback']}")
    
    # Place second station perfectly (streak continues)
    result = manager.attempt_place("Catalunya", 1)
    
    assert result["accepted"] == True
    assert result["perfect"] == True
    assert result["next_index"] == 2
    assert result["streak"] == 2, "Streak should increment to 2"
    assert result["points"] == 120, f"Points should be 120 (100 + 2*10), got {result['points']}"
    
    print(f"\n✓ Placed 'Catalunya' at slot 1:")
    print(f"  - Streak: {result['streak']}")
    print(f"  - Points: {result['points']}")
    
    print("\n✅ TEST 1 PASSED\n")


def test_ahead_placement():
    """Test Case 2: Placing ahead within window (non-perfect)"""
    print("=" * 60)
    print("TEST 2: Ahead Placement (Within Window)")
    print("=" * 60)
    
    stations = ["Liceu", "Catalunya", "Passeig de Gràcia", "Diagonal"]
    manager = SlotManager(stations, window_size=3, parking_capacity=3)
    
    # Try to place second station at first slot (ahead)
    result = manager.attempt_place("Catalunya", 0)
    
    assert result["accepted"] == True, "Should accept station within window"
    assert result["perfect"] == False, "Should NOT be perfect (out of order)"
    assert result["next_index"] == 0, "Should NOT advance next_index"
    assert result["streak"] == 0, "Streak should stay at 0"
    assert result["points"] == 50, f"Points should be 50 (ahead bonus), got {result['points']}"
    
    print(f"✓ Placed 'Catalunya' ahead at slot 0:")
    print(f"  - Accepted: {result['accepted']}")
    print(f"  - Perfect: {result['perfect']}")
    print(f"  - Next index: {result['next_index']} (should NOT advance)")
    print(f"  - Streak: {result['streak']}")
    print(f"  - Points: {result['points']}")
    print(f"  - Feedback: {result['feedback']}")
    
    # Now place the correct next station
    result = manager.attempt_place("Liceu", 0)
    
    assert result["accepted"] == True
    assert result["perfect"] == True, "Should be perfect now"
    assert result["next_index"] == 1, "Should advance after placing correct station"
    assert result["streak"] == 1, "Streak should start"
    
    print(f"\n✓ Placed 'Liceu' (correct next) at slot 0:")
    print(f"  - Perfect: {result['perfect']}")
    print(f"  - Next index: {result['next_index']} (advanced!)")
    print(f"  - Streak: {result['streak']}")
    
    print("\n✅ TEST 2 PASSED\n")


def test_wrong_placement_and_game_over():
    """Test Case 3: Wrong placements leading to game over"""
    print("=" * 60)
    print("TEST 3: Wrong Placements and Game Over")
    print("=" * 60)
    
    stations = ["Liceu", "Catalunya", "Passeig de Gràcia", "Diagonal"]
    manager = SlotManager(stations, window_size=2, parking_capacity=2)
    
    # Try to place at wrong slot
    result = manager.attempt_place("Liceu", 1)
    
    assert result["accepted"] == False, "Should reject wrong slot"
    assert result["parking_count"] == 1, "Should increment parking"
    assert result["feedback"] == "Col·loca-la al següent punt"
    
    print(f"✓ Attempted 'Liceu' at wrong slot 1:")
    print(f"  - Accepted: {result['accepted']}")
    print(f"  - Parking: {result['parking_count']}/2")
    print(f"  - Feedback: {result['feedback']}")
    
    # Try to place out-of-window station
    result = manager.attempt_place("Diagonal", 0)
    
    assert result["accepted"] == False, "Should reject out-of-window station"
    assert result["parking_count"] == 2, "Should increment parking again"
    assert result["game_over"] == True, "Should trigger game over (parking full)"
    
    print(f"\n✓ Attempted 'Diagonal' (out of window) at slot 0:")
    print(f"  - Accepted: {result['accepted']}")
    print(f"  - Parking: {result['parking_count']}/2 (FULL!)")
    print(f"  - Game Over: {result['game_over']}")
    print(f"  - Feedback: {result['feedback']}")
    
    # Try to place after game over
    result = manager.attempt_place("Liceu", 0)
    assert result["game_over"] == True, "Should stay game over"
    
    print(f"\n✓ Attempted placement after game over:")
    print(f"  - Game Over: {result['game_over']}")
    
    print("\n✅ TEST 3 PASSED\n")


def test_complete_game():
    """Bonus Test: Complete game winning scenario"""
    print("=" * 60)
    print("BONUS TEST: Complete Winning Game")
    print("=" * 60)
    
    stations = ["A", "B", "C"]
    manager = SlotManager(stations, window_size=3, parking_capacity=3)
    
    # Place all stations perfectly
    results = []
    for i, station in enumerate(stations):
        result = manager.attempt_place(station, i)
        results.append(result)
        print(f"Placed '{station}' at slot {i}: streak={result['streak']}, points={result['points']}")
    
    # Last placement should trigger win
    assert results[-1]["game_over"] == True, "Should be game over (win)"
    assert results[-1]["accepted"] == True, "Last placement accepted"
    assert "completat" in results[-1]["feedback"].lower(), "Should show completion message"
    
    stats = manager.get_stats()
    print(f"\n✓ Final Stats:")
    print(f"  - Total Score: {stats['total_score']}")
    print(f"  - Perfect Count: {stats['perfect_count']}")
    print(f"  - Progress: {stats['progress'] * 100:.0f}%")
    print(f"  - Game Over: {stats['game_over']}")
    
    assert stats["progress"] == 1.0, "Should be 100% complete"
    
    print("\n✅ BONUS TEST PASSED\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SLOT MANAGER - UNIT TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_perfect_placement()
        test_ahead_placement()
        test_wrong_placement_and_game_over()
        test_complete_game()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
