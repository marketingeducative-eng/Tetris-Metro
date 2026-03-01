"""
GameEngine - core game logic without UI dependencies.
"""
from pathlib import Path
import random
import json

from data.metro_loader import normalize_station_id
from core.badges import BADGE_DEFINITIONS
from core.modes import FreeMode, GoalMode, SurvivalMode


class GameEngine:
    """Pure game logic engine with event callbacks."""

    def __init__(self, metro_line, line_id="L3", practice_mode=False, direction_mode=False, first_day_mode=False, random_seed=None, mode=None):
        self.line = metro_line
        self.practice_mode = practice_mode
        self.direction_mode = direction_mode
        self.first_day_mode = first_day_mode

        self.current_index = 0
        self.next_index = 1
        self.score = 0
        self.streak = 0
        self.mistakes = 0
        self.high_score = 0
        self.game_over = False

        self.base_lives = 3
        self.bonus_lives = 0
        self.max_bonus_lives = 2
        self.lives_per_streak = 7

        self.is_waiting_for_answer = False
        self.has_attempted = False
        self.answered_correctly = False
        self.correct_station_id = None
        self.move_start_time = 0

        self.consecutive_correct = 0
        self.consecutive_mistakes = 0

        self.stations_completed = 0
        self.visited_stations = set()
        self.visited_stations.add(0)
        self.failed_station_index = None

        self.current_zone = metro_line.stations[0].zone if metro_line.stations else ""
        self.zone_changed = False
        self.new_zone = ""

        self.subtitles_enabled = True

        self.goal_mode = False
        self.goal_station_id = None
        self.goal_reached = False

        self.first_day_route = [
            "CATALUNYA",
            "LICEU",
            "JAUME_I",
            "BARCELONETA",
            "ESPANYA"
        ]
        self.first_day_progress = 0
        self.first_day_completed = False

        self.visited_tags = set()
        self.unlocked_badges = set()

        self.base_duration = 3.4
        self.min_duration = 2.2
        self.duration_step = 0.05
        self.streak_interval = 1

        self.base_radius = 50.0
        self.min_radius = 38.0
        self.radius_step = 1.0

        safe_line_id = line_id or "L3"
        mode_suffix = "_practice" if practice_mode else ""
        direction_suffix = "_direction" if direction_mode else ""
        filename = f"high_score_{safe_line_id}{mode_suffix}{direction_suffix}.json"
        self.high_score_file = Path(__file__).parent.parent / "data" / filename
        self._load_high_score()

        if random_seed is not None:
            random.seed(random_seed)

        self.on_round_start = None
        self.on_correct = None
        self.on_wrong = None
        self.on_game_over = None
        self.on_line_completed = None

        self.mode = None
        self.mode_name = "FREE"
        self.set_mode(mode or FreeMode())

    def set_callbacks(self, on_round_start=None, on_correct=None, on_wrong=None, on_game_over=None, on_line_completed=None):
        self.on_round_start = on_round_start
        self.on_correct = on_correct
        self.on_wrong = on_wrong
        self.on_game_over = on_game_over
        self.on_line_completed = on_line_completed

    def set_mode(self, mode):
        self.mode = mode or FreeMode()
        self.mode_name = getattr(self.mode, "name", "FREE")
        if isinstance(self.mode, GoalMode):
            self.goal_mode = True
            self.goal_station_id = self.mode.goal_station_id
        else:
            self.goal_mode = False
            self.goal_station_id = None
        self.goal_reached = False

    def get_recommendations(self):
        if self.mode and hasattr(self.mode, "get_recommendations"):
            return self.mode.get_recommendations(self)
        return list(self.line.stations)

    def get_direction_terminal(self):
        return self.line.endpoints.get('to', '')

    def get_distance_to_goal(self):
        if not self.goal_mode or self.goal_station_id is None:
            return None
        for idx, station in enumerate(self.line.stations):
            if normalize_station_id(station.name) == self.goal_station_id:
                return abs(idx - self.current_index)
        return None

    def get_goal_direction_indicator(self):
        if not self.goal_mode or self.goal_station_id is None:
            return None
        goal_idx = None
        for idx, station in enumerate(self.line.stations):
            if normalize_station_id(station.name) == self.goal_station_id:
                goal_idx = idx
                break
        if goal_idx is None:
            return None
        if goal_idx > self.current_index:
            return ("↑", "cap al nord")
        if goal_idx < self.current_index:
            return ("↓", "cap al sud")
        return None

    def get_current_first_day_goal(self):
        if not self.first_day_mode:
            return None
        if self.first_day_progress >= len(self.first_day_route):
            return None
        return self.first_day_route[self.first_day_progress]

    def advance_first_day_progress(self):
        if not self.first_day_mode:
            return False
        if self.first_day_progress < len(self.first_day_route):
            self.first_day_progress += 1
            if self.first_day_progress >= len(self.first_day_route):
                self.first_day_completed = True
                return True
            return True
        return False

    def get_first_day_progress_ratio(self):
        if not self.first_day_mode:
            return 0.0
        if len(self.first_day_route) == 0:
            return 1.0
        return self.first_day_progress / len(self.first_day_route)

    def check_badge_unlock(self, badge_id):
        if badge_id not in BADGE_DEFINITIONS:
            return False
        if badge_id in self.unlocked_badges:
            return False
        badge_def = BADGE_DEFINITIONS[badge_id]
        required_tags = badge_def["tags"]
        required_count = badge_def["required_count"]
        visited_count = sum(1 for tag in required_tags if tag in self.visited_tags)
        return visited_count >= required_count

    def check_all_badges(self):
        newly_unlocked = []
        for badge_id in BADGE_DEFINITIONS:
            if self.check_badge_unlock(badge_id):
                self.unlocked_badges.add(badge_id)
                newly_unlocked.append(badge_id)
        return newly_unlocked

    def add_visited_tags(self, tags):
        if tags:
            for tag in tags:
                self.visited_tags.add(tag)

    def calculate_travel_duration(self):
        duration = self.base_duration
        if self.consecutive_correct >= 3:
            reductions = self.consecutive_correct // 3
            duration = self.base_duration - (reductions * self.duration_step)
        if self.consecutive_mistakes >= 2:
            duration = self.base_duration
        return max(self.min_duration, min(duration, self.base_duration))

    def calculate_drop_radius(self):
        reductions = self.streak // self.streak_interval
        radius = self.base_radius - (reductions * self.radius_step)
        return max(self.min_radius, radius)

    def start_round(self, current_time):
        if self.game_over:
            return None
        self.current_index = self.next_index
        self.next_index = (self.current_index + 1) % len(self.line.stations)
        next_station = self.line.stations[self.next_index]
        self.zone_changed = False
        if next_station.zone and next_station.zone != self.current_zone:
            self.zone_changed = True
            self.new_zone = next_station.zone
            self.current_zone = next_station.zone
        self.is_waiting_for_answer = True
        self.has_attempted = False
        self.answered_correctly = False
        self.correct_station_id = self.line.stations[self.next_index].name
        self.move_start_time = current_time
        round_data = {
            'next_index': self.next_index,
            'correct_station_id': self.correct_station_id,
            'travel_duration': self.calculate_travel_duration(),
            'zone_changed': self.zone_changed,
            'zone_name': self.new_zone if self.zone_changed else None
        }
        if self.mode:
            self.mode.on_round_start(self, next_station)
        if callable(self.on_round_start):
            self.on_round_start(round_data)
        return round_data

    def generate_token_ids(self):
        correct_index = self.next_index
        correct_id = self.line.stations[correct_index].name
        num_stations = len(self.line.stations)
        used_indices = {correct_index}
        distractor_indices = []

        max_offset = min(num_stations // 2, 10)
        offsets = []
        for offset in range(1, max_offset + 1):
            offsets.extend([offset, -offset])
        random.shuffle(offsets)

        for offset in offsets:
            if len(distractor_indices) >= 2:
                break
            idx = correct_index + offset
            idx = max(0, min(idx, num_stations - 1))
            if idx not in used_indices:
                used_indices.add(idx)
                distractor_indices.append(idx)

        if len(distractor_indices) < 2:
            remaining = [i for i in range(num_stations) if i not in used_indices]
            random.shuffle(remaining)
            needed = 2 - len(distractor_indices)
            distractor_indices.extend(remaining[:needed])

        distractors = [self.line.stations[i].name for i in distractor_indices]
        all_station_ids = [correct_id] + distractors
        random.shuffle(all_station_ids)
        return all_station_ids

    def validate_drop(self, token_station_id, distance, elapsed_time):
        if not self.is_waiting_for_answer or self.has_attempted:
            return None
        travel_duration = self.calculate_travel_duration()
        if elapsed_time >= travel_duration:
            return 'timeout'
        acceptance_radius = self.calculate_drop_radius()
        if distance < acceptance_radius:
            return 'correct' if token_station_id == self.correct_station_id else 'wrong'
        return None

    def handle_correct_answer(self):
        self.has_attempted = True
        self.answered_correctly = True
        self.is_waiting_for_answer = False
        self.visited_stations.add(self.next_index)

        goal_reached = False
        if self.goal_mode and self.goal_station_id and not self.goal_reached:
            current_station = self.line.stations[self.next_index]
            current_station_id = normalize_station_id(current_station.name)
            if current_station_id == self.goal_station_id:
                self.goal_reached = True
                goal_reached = True

        first_day_step_reached = False
        first_day_completed_now = False
        if self.first_day_mode:
            current_goal = self.get_current_first_day_goal()
            if current_goal:
                current_station = self.line.stations[self.next_index]
                current_station_id = normalize_station_id(current_station.name)
                if current_station_id == current_goal:
                    first_day_step_reached = True
                    self.advance_first_day_progress()
                    if self.first_day_completed:
                        first_day_completed_now = True

        unlocked_badges = []
        current_station = self.line.stations[self.next_index]
        if hasattr(current_station, 'tourist_tags') and current_station.tourist_tags:
            self.add_visited_tags(current_station.tourist_tags)
            unlocked_badges = self.check_all_badges()

        self.stations_completed += 1
        is_milestone = (self.stations_completed % 5 == 0)

        self.consecutive_correct += 1
        self.consecutive_mistakes = 0

        bonus = 100 + self.streak * 10
        self.score += bonus
        self.streak += 1

        life_granted = False
        if (self.streak % self.lives_per_streak == 0 and
                self.bonus_lives < self.max_bonus_lives):
            self.bonus_lives += 1
            life_granted = True

        message = "Correcte. Continuem."
        if life_granted:
            message = "Correcte. Vida extra."

        line_completed_run = len(self.visited_stations) == len(self.line.stations)

        result = {
            'bonus': bonus,
            'message': message,
            'life_granted': life_granted,
            'is_milestone': is_milestone,
            'goal_reached': goal_reached,
            'stations_completed': self.stations_completed,
            'line_completed_run': line_completed_run,
            'first_day_step_reached': first_day_step_reached,
            'first_day_completed': first_day_completed_now,
            'unlocked_badges': unlocked_badges
        }
        if self.mode:
            self.mode.on_correct(self, current_station)
        if callable(self.on_correct):
            self.on_correct(result)
        if line_completed_run and callable(self.on_line_completed):
            self.on_line_completed()
        return result

    def handle_wrong_answer(self):
        self.has_attempted = True
        self.is_waiting_for_answer = False
        self.consecutive_mistakes += 1
        self.consecutive_correct = 0
        self.streak = self.streak // 2
        self.mistakes += 1
        self.failed_station_index = self.next_index

        message = "No és aquesta parada"
        total_lives = self.base_lives + self.bonus_lives
        game_over = (self.mistakes >= total_lives) and not self.practice_mode

        result = {'message': message, 'game_over': game_over, 'type': 'wrong'}
        current_station = self.line.stations[self.next_index]
        if self.mode:
            self.mode.on_wrong(self, current_station)
        if callable(self.on_wrong):
            self.on_wrong(result)
        if game_over:
            self._emit_game_over()
        return result

    def handle_timeout(self):
        self.has_attempted = True
        self.is_waiting_for_answer = False
        self.streak = self.streak // 2
        self.mistakes += 1
        self.failed_station_index = self.next_index

        message = f"Propera estació: {self.correct_station_id}"
        total_lives = self.base_lives + self.bonus_lives
        game_over = (self.mistakes >= total_lives) and not self.practice_mode

        result = {'message': message, 'game_over': game_over, 'type': 'timeout'}
        current_station = self.line.stations[self.next_index]
        if self.mode:
            self.mode.on_wrong(self, current_station)
        if callable(self.on_wrong):
            self.on_wrong(result)
        if game_over:
            self._emit_game_over()
        return result

    def _emit_game_over(self):
        data = self.check_game_over()
        if data:
            if self.mode:
                self.mode.on_game_over(self)
            if callable(self.on_game_over):
                self.on_game_over(data)

    def check_game_over(self):
        if self.practice_mode:
            return None
        total_lives = self.base_lives + self.bonus_lives
        if self.mistakes >= total_lives:
            self.game_over = True
            is_new_record = self.score > self.high_score
            if is_new_record:
                self.high_score = self.score
                self._save_high_score()
            return {'is_new_record': is_new_record}
        return None

    def _load_high_score(self):
        try:
            if self.high_score_file.exists():
                with open(self.high_score_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.high_score = data.get('high_score', 0)
            else:
                self.high_score = 0
        except Exception:
            self.high_score = 0

    def _save_high_score(self):
        try:
            self.high_score_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.high_score_file, 'w', encoding='utf-8') as f:
                json.dump({'high_score': self.high_score}, f, indent=2)
        except Exception:
            pass
