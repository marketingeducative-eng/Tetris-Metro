"""
DirectionMission - Mini-challenge for direction selection
Triggered every N correct placements in ORDER TRACK mode
"""
import random


class DirectionMission:
    """
    Mini-challenge mode: Player must choose correct direction/terminus
    
    Triggered periodically during ORDER TRACK gameplay. Shows a brief
    scenario in Catalan asking which direction to take, with 2 options.
    """
    
    def __init__(self, content_manager):
        """
        Initialize Direction Mission
        
        Args:
            content_manager: MetroContentManager instance
        """
        self.content = content_manager
        
        # Mission state
        self.active = False
        self.current_mission = None
        self.cooldown = 0
        
        # Trigger config
        self.trigger_interval = 5  # Every N correct answers
        
        # Feedback
        self.last_result = None
        self.feedback_timer = 0
    
    def should_trigger(self, correct_count):
        """
        Check if mission should trigger based on correct count
        
        Args:
            correct_count: Number of correct answers in ORDER TRACK
            
        Returns:
            True if should trigger
        """
        if self.active or self.cooldown > 0:
            return False
        
        return (correct_count > 0 and correct_count % self.trigger_interval == 0)
    
    def generate_mission(self, current_line_id, metro_lines_data):
        """
        Generate a new direction mission
        
        Args:
            current_line_id: Current metro line being played (e.g., 'L1')
            metro_lines_data: Dict of metro line data from JSON
            
        Returns:
            dict with mission data or None if cannot generate
        """
        if current_line_id not in metro_lines_data:
            return None
        
        line_data = metro_lines_data[current_line_id]
        stations = line_data.get('stations', [])
        
        if len(stations) < 4:
            return None  # Not enough stations
        
        # Pick random source and destination (not adjacent, not same)
        attempts = 0
        while attempts < 10:
            src_idx = random.randint(0, len(stations) - 1)
            dest_idx = random.randint(0, len(stations) - 1)
            
            # Must be at least 2 stations apart
            if abs(dest_idx - src_idx) >= 2:
                break
            attempts += 1
        
        if abs(dest_idx - src_idx) < 2:
            return None  # Couldn't find good pair
        
        src_station = stations[src_idx]
        dest_station = stations[dest_idx]
        
        # Determine correct direction (terminus)
        # For circular lines, use intermediate distinctive stations
        if stations[0] == stations[-1]:
            # Circular line - use quarter points as direction markers
            quarter = len(stations) // 4
            three_quarters = (len(stations) * 3) // 4
            
            if dest_idx > src_idx:
                # Going "up" - use station at 3/4 point as direction
                correct_terminus = stations[three_quarters]
                wrong_terminus = stations[quarter]
            else:
                # Going "down" - use station at 1/4 point as direction
                correct_terminus = stations[quarter]
                wrong_terminus = stations[three_quarters]
        else:
            # Linear line - use actual terminus
            if dest_idx > src_idx:
                correct_terminus = stations[-1]
                wrong_terminus = stations[0]
            else:
                correct_terminus = stations[0]
                wrong_terminus = stations[-1]
        
        # Create mission text in Catalan
        mission_text = f"Vull anar a {dest_station} des de {src_station}. Quina direcció?"
        
        # Randomize option order
        if random.random() < 0.5:
            options = [
                {'label': f"Direcció {correct_terminus}", 'correct': True},
                {'label': f"Direcció {wrong_terminus}", 'correct': False}
            ]
        else:
            options = [
                {'label': f"Direcció {wrong_terminus}", 'correct': False},
                {'label': f"Direcció {correct_terminus}", 'correct': True}
            ]
        
        mission = {
            'text': mission_text,
            'options': options,
            'correct_terminus': correct_terminus,
            'line_id': current_line_id,
            'src_station': src_station,
            'dest_station': dest_station
        }
        
        return mission
    
    def start_mission(self, current_line_id, metro_lines_data):
        """
        Start a new direction mission
        
        Args:
            current_line_id: Current line being played
            metro_lines_data: Metro line data from JSON
            
        Returns:
            True if mission started successfully
        """
        mission = self.generate_mission(current_line_id, metro_lines_data)
        
        if not mission:
            return False
        
        self.current_mission = mission
        self.active = True
        self.last_result = None
        
        print(f"Direction mission started: {mission['text']}")
        return True
    
    def submit_answer(self, option_index):
        """
        Submit answer to current mission
        
        Args:
            option_index: 0 for option A, 1 for option B
            
        Returns:
            dict with result:
            {
                'correct': bool,
                'feedback': str,
                'bonus_score': int
            }
        """
        if not self.active or not self.current_mission:
            return None
        
        options = self.current_mission['options']
        
        if option_index < 0 or option_index >= len(options):
            return None
        
        selected_option = options[option_index]
        correct = selected_option['correct']
        
        result = {
            'correct': correct,
            'feedback': '',
            'bonus_score': 0
        }
        
        if correct:
            result['feedback'] = "Direcció correcta!"
            result['bonus_score'] = 300
        else:
            # Find correct terminus
            correct_terminus = self.current_mission['correct_terminus']
            result['feedback'] = f"Direcció: {correct_terminus}"
            result['bonus_score'] = 0
        
        self.last_result = result
        self.feedback_timer = 2.5
        self.active = False
        self.cooldown = 3.0  # Cooldown before next mission
        
        return result
    
    def cancel_mission(self):
        """Cancel active mission (timeout or skip)"""
        if self.active:
            self.active = False
            self.current_mission = None
            self.cooldown = 2.0
    
    def update(self, dt):
        """Update per frame"""
        # Update cooldown
        if self.cooldown > 0:
            self.cooldown -= dt
            if self.cooldown < 0:
                self.cooldown = 0
        
        # Update feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.last_result = None
    
    def get_current_mission(self):
        """Get current active mission data"""
        if not self.active or not self.current_mission:
            return None
        
        return {
            'text': self.current_mission['text'],
            'options': [opt['label'] for opt in self.current_mission['options']],
            'line_id': self.current_mission['line_id']
        }
    
    def is_active(self):
        """Check if a mission is currently active"""
        return self.active
    
    def get_feedback(self):
        """Get current feedback if any"""
        if self.last_result and self.feedback_timer > 0:
            return {
                'text': self.last_result['feedback'],
                'correct': self.last_result['correct']
            }
        return None
