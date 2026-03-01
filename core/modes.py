"""
Game modes for the core engine.
"""
import random


class BaseMode:
    """Base mode with hooks for game lifecycle."""

    name = "FREE"

    def on_round_start(self, engine, station):
        pass

    def on_correct(self, engine, station):
        pass

    def on_wrong(self, engine, station):
        pass

    def on_game_over(self, engine):
        pass

    def get_recommendations(self, engine):
        return list(engine.line.stations)


class FreeMode(BaseMode):
    """Default mode with no special behavior."""

    name = "FREE"


class GoalMode(BaseMode):
    """Goal mode driven by a target station."""

    name = "GOAL"

    def __init__(self, goal_station_id=None):
        self.goal_station_id = goal_station_id


class SurvivalMode(BaseMode):
    """
    Barcelona Survival Mode - Learn practical Catalan for metro navigation.
    
    Real-life scenarios for Erasmus students and expats:
    - Buying TMB tickets
    - Asking for directions
    - Understanding signage
    - Ordering near stations
    - Reading metro directions
    
    Emotional framing: "Arriving in Barcelona for the first time"
    No English during gameplay (optional help button available)
    """
    
    name = "SURVIVAL"
    
    def __init__(self, scenarios_data=None):
        """
        Initialize Survival Mode with scenarios.
        
        Args:
            scenarios_data (list): List of scenario dicts. If None, loads default scenarios.
        """
        self.scenarios = scenarios_data or self._load_default_scenarios()
        self.current_scenario_index = 0
        self.completed_scenarios = set()
        self.scenario_attempts = {}
        
    def _load_default_scenarios(self):
        """Load default survival scenarios"""
        from pathlib import Path
        import json
        
        try:
            scenarios_path = Path(__file__).parent.parent / "data" / "survival_scenarios_ca.json"
            with open(scenarios_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('scenarios', [])
        except Exception as e:
            print(f"Could not load survival scenarios: {e}")
            return []
    
    def get_current_scenario(self):
        """Get the current scenario"""
        if not self.scenarios or self.current_scenario_index >= len(self.scenarios):
            return None
        return self.scenarios[self.current_scenario_index]
    
    def get_scenario_progress(self):
        """Get completion progress (completed / total)"""
        return (len(self.completed_scenarios), len(self.scenarios))
    
    def is_complete(self):
        """Check if all scenarios are completed"""
        return len(self.completed_scenarios) >= len(self.scenarios)
    
    def on_round_start(self, engine, station):
        """Start a new scenario round"""
        scenario = self.get_current_scenario()
        if scenario:
            scenario_id = scenario.get('id', f'scenario_{self.current_scenario_index}')
            if scenario_id not in self.scenario_attempts:
                self.scenario_attempts[scenario_id] = 0
    
    def on_correct(self, engine, station):
        """Mark scenario as completed and advance"""
        scenario = self.get_current_scenario()
        if scenario:
            scenario_id = scenario.get('id', f'scenario_{self.current_scenario_index}')
            self.completed_scenarios.add(scenario_id)
            
            # Advance to next scenario
            self.current_scenario_index += 1
            
            # Check if all scenarios completed
            if self.is_complete():
                # Unlock survival badge
                engine.unlocked_badges.add("survival_barcelona_1")
    
    def on_wrong(self, engine, station):
        """Track failed attempts"""
        scenario = self.get_current_scenario()
        if scenario:
            scenario_id = scenario.get('id', f'scenario_{self.current_scenario_index}')
            self.scenario_attempts[scenario_id] = self.scenario_attempts.get(scenario_id, 0) + 1
    
    def get_recommendations(self, engine):
        """
        Return station options based on current scenario.
        
        In survival mode, we present scenario-specific choices
        instead of all line stations.
        """
        scenario = self.get_current_scenario()
        if not scenario:
            return list(engine.line.stations)
        
        # Get scenario choices
        choices = scenario.get('choices', [])
        
        # Map choices to stations
        # For now, return random subset of line stations
        # In full implementation, this would map scenario choices to specific stations
        stations = list(engine.line.stations)
        random.shuffle(stations)
        return stations[:len(choices)] if choices else stations[:3]
