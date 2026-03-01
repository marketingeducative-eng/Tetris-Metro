"""
Audio Service - Simple sound effects for game events
"""
from kivy.core.audio import SoundLoader
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.animation import Animation
from pathlib import Path
from typing import Optional
import time
from enum import Enum
import random
import io


class AudioEvent(str, Enum):
    UI_CLICK = "ui_click"
    UI_PICK = "ui_pick"
    UI_DROP = "ui_drop"
    UI_HOVER_TARGET = "ui_hover_target"
    SFX_CORRECT = "sfx_correct"
    SFX_WRONG = "sfx_wrong"
    SFX_INVALID_DROP = "sfx_invalid_drop"
    SFX_TIMEOUT = "sfx_timeout"
    SFX_ARRIVAL_BRAKE = "sfx_arrival_brake"
    SFX_DOOR_OPEN = "sfx_door_open"
    SFX_DOOR_CLOSE = "sfx_door_close"
    AMB_TUNNEL = "amb_tunnel"
    AMB_STATION = "amb_station"
    SFX_GOAL_ANTICIPATION = "sfx_goal_anticipation"
    SFX_GOAL_CELEBRATION = "sfx_goal_celebration"
    SFX_LINE_COMPLETED = "sfx_line_completed"


AUDIO_EVENT_FILES = {
    AudioEvent.UI_CLICK: ["ui_click.wav", "ui_click_02.wav"],
    AudioEvent.UI_PICK: ["ui_pick.wav"],
    AudioEvent.UI_DROP: ["ui_drop.wav"],
    AudioEvent.UI_HOVER_TARGET: ["ui_hover_target.wav"],
    AudioEvent.SFX_CORRECT: ["sfx_correct.wav"],
    AudioEvent.SFX_WRONG: ["sfx_wrong.wav"],
    AudioEvent.SFX_INVALID_DROP: ["sfx_invalid_drop.wav"],
    AudioEvent.SFX_TIMEOUT: ["sfx_timeout.wav"],
    AudioEvent.SFX_ARRIVAL_BRAKE: ["sfx_arrival_brake.wav"],
    AudioEvent.SFX_DOOR_OPEN: ["sfx_door_open.wav"],
    AudioEvent.SFX_DOOR_CLOSE: ["sfx_door_close.wav"],
    AudioEvent.AMB_TUNNEL: ["amb_tunnel.wav"],
    AudioEvent.AMB_STATION: ["amb_station.wav"],
    AudioEvent.SFX_GOAL_ANTICIPATION: ["sfx_goal_anticipation.wav"],
    AudioEvent.SFX_GOAL_CELEBRATION: ["sfx_goal_celebration.wav"],
    AudioEvent.SFX_LINE_COMPLETED: ["sfx_line_completed.wav"],
}


class AudioService:
    """Manages simple sound effects for game events"""
    
    def __init__(self):
        self.sounds = {}
        self.event_sounds = {}
        self.enabled = True
        self._cooldowns = {}
        self._active_sound = None
        self._active_priority = -1
        self._active_event = None
        self._ambience_mode = "none"
        self._ambience_sound = None
        self._ambience_volume = 0.22
        self._ambience_fade_duration = 0.6
        self._ambience_fade_in = None
        self._ambience_fade_out = None
        self.tunnel_sound = None
        self.tunnel_sound_active = False
        self.tunnel_fade_animation = None
        self.bonus_life_sound = None
        self.direction_mode_sound = None
        self.milestone_sound = None
        self._initialize_sounds()
        self._generate_tunnel_sound()
        self._generate_bonus_life_sound()
        self._generate_direction_mode_sound()
        self._generate_milestone_sound()
        self._register_event_fallbacks()
    
    def _initialize_sounds(self):
        """Initialize sound effects"""
        # Try to load station announcement chime
        # If no file exists, we'll generate a simple beep programmatically
        sound_dir = Path(__file__).parent.parent / "sounds"
        
        # Look for station chime sound file
        chime_path = sound_dir / "station_chime.wav"
        
        if chime_path.exists():
            try:
                self.sounds['station_chime'] = SoundLoader.load(str(chime_path))
                Logger.info(f"Audio: Loaded station_chime from {chime_path}")
            except Exception as e:
                Logger.warning(f"Audio: Could not load station_chime: {e}")
                self._generate_station_chime()
        else:
            Logger.info("Audio: No station_chime.wav found, using generated sound")
            self._generate_station_chime()

        self._load_event_registry(sound_dir)

    def _load_event_registry(self, sound_dir: Path):
        """Load event sound variants from disk."""
        for event, filenames in AUDIO_EVENT_FILES.items():
            loaded = []
            for filename in filenames:
                path = sound_dir / filename
                if not path.exists():
                    continue
                try:
                    sound = SoundLoader.load(str(path))
                    if sound:
                        loaded.append(sound)
                except Exception as e:
                    Logger.warning(f"Audio: Could not load {event.value} from {path}: {e}")
            self.event_sounds[event] = loaded

    def _register_event_fallbacks(self):
        """Wire generated sounds into the event registry when files are missing."""
        if self.event_sounds.get(AudioEvent.AMB_TUNNEL):
            self.tunnel_sound = self.event_sounds[AudioEvent.AMB_TUNNEL][0]
        elif self.tunnel_sound:
            self.event_sounds[AudioEvent.AMB_TUNNEL] = [self.tunnel_sound]
        if not self.event_sounds.get(AudioEvent.SFX_GOAL_ANTICIPATION) and self.milestone_sound:
            self.event_sounds[AudioEvent.SFX_GOAL_ANTICIPATION] = [self.milestone_sound]
        if not self.event_sounds.get(AudioEvent.SFX_GOAL_CELEBRATION):
            fallback = []
            if self.direction_mode_sound:
                fallback.append(self.direction_mode_sound)
            if self.milestone_sound:
                fallback.append(self.milestone_sound)
            if fallback:
                self.event_sounds[AudioEvent.SFX_GOAL_CELEBRATION] = fallback
    
    def _generate_station_chime(self):
        """Generate a simple two-tone chime using wave synthesis"""
        try:
            import wave
            import struct
            import math
            import tempfile
            
            # Generate a pleasant two-tone chime (E5 and C5)
            sample_rate = 22050
            duration = 0.15  # 150ms per tone
            
            # Create temporary WAV file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp_file.name
            temp_file.close()
            
            with wave.open(temp_path, 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                
                # First tone: E5 (659.25 Hz)
                freq1 = 659.25
                samples1 = []
                for i in range(int(sample_rate * duration)):
                    # Apply envelope (fade in/out)
                    t = i / sample_rate
                    envelope = math.sin(math.pi * t / duration)
                    value = int(32767 * 0.3 * envelope * math.sin(2 * math.pi * freq1 * t))
                    samples1.append(struct.pack('h', value))
                
                # Second tone: C6 (1046.50 Hz) - higher pitch
                freq2 = 1046.50
                samples2 = []
                for i in range(int(sample_rate * duration)):
                    t = i / sample_rate
                    envelope = math.sin(math.pi * t / duration)
                    value = int(32767 * 0.3 * envelope * math.sin(2 * math.pi * freq2 * t))
                    samples2.append(struct.pack('h', value))
                
                # Write both tones
                wav_file.writeframes(b''.join(samples1 + samples2))
            
            # Load the generated sound
            self.sounds['station_chime'] = SoundLoader.load(temp_path)
            
            if self.sounds['station_chime']:
                Logger.info("Audio: Generated station_chime successfully")
            else:
                Logger.warning("Audio: Failed to load generated station_chime")
                
        except Exception as e:
            Logger.error(f"Audio: Could not generate station_chime: {e}")
            self.sounds['station_chime'] = None
    
    def play_station_announcement(self):
        """Play station announcement chime"""
        if not self.enabled:
            return
        
        chime = self.sounds.get('station_chime')
        if chime:
            try:
                # Reset to beginning and play
                chime.seek(0)
                chime.volume = 0.4  # 40% volume
                chime.play()
            except Exception as e:
                Logger.warning(f"Audio: Could not play station_chime: {e}")

    def _resolve_event(self, event_name):
        if isinstance(event_name, AudioEvent):
            return event_name
        if not isinstance(event_name, str):
            return None
        try:
            return AudioEvent(event_name)
        except ValueError:
            return None

    def _is_sound_playing(self, sound):
        if not sound:
            return False
        state = getattr(sound, "state", None)
        if state is None:
            return False
        return state == "play"

    def _refresh_active(self):
        if self._active_sound and not self._is_sound_playing(self._active_sound):
            self._active_sound = None
            self._active_priority = -1
            self._active_event = None

    def _play_from_event(self, event_name, volume=1.0, allow_overlap=False, cooldown_ms=0, priority=0, loop=False):
        if not self.enabled:
            return None

        event = self._resolve_event(event_name)
        if not event:
            return None

        variants = self.event_sounds.get(event, [])
        if not variants:
            return None

        now = time.monotonic()
        last_played = self._cooldowns.get(event.value)
        if cooldown_ms and last_played is not None:
            elapsed_ms = (now - last_played) * 1000.0
            if elapsed_ms < cooldown_ms:
                return None

        self._refresh_active()
        if not allow_overlap and self._active_sound and self._is_sound_playing(self._active_sound):
            if priority > self._active_priority:
                try:
                    self._active_sound.stop()
                except Exception:
                    pass
            else:
                return None

        sound = random.choice(variants)
        if not sound:
            return None

        try:
            sound.seek(0)
            sound.volume = max(0.0, min(1.0, volume))
            sound.loop = bool(loop)
            sound.play()
        except Exception as e:
            Logger.warning(f"Audio: Could not play event {event.value}: {e}")
            return None

        self._cooldowns[event.value] = now
        if not allow_overlap:
            self._active_sound = sound
            self._active_priority = priority
            self._active_event = event.value
        return sound

    def play(self, event_name: str, volume=1.0, allow_overlap=False, cooldown_ms=0, priority=0):
        """Play an audio event by name with cooldown, priority, and overlap controls."""
        return self._play_from_event(
            event_name,
            volume=volume,
            allow_overlap=allow_overlap,
            cooldown_ms=cooldown_ms,
            priority=priority,
            loop=False,
        )

    def play_event(self, event: AudioEvent, volume: Optional[float] = None, loop: bool = False):
        """Play an audio event with optional volume and loop settings."""
        if volume is None:
            volume = 1.0
        return self._play_from_event(
            event,
            volume=volume,
            allow_overlap=True,
            cooldown_ms=0,
            priority=0,
            loop=loop,
        )

    def play_correct_feedback(self, volume=0.5, streak_rise=False):
        """Play success feedback; optionally add a subtle pitch rise for streaks."""
        sound = self._play_from_event(
            AudioEvent.SFX_CORRECT,
            volume=volume,
            allow_overlap=True,
            cooldown_ms=120,
            priority=2,
            loop=False,
        )
        if sound and hasattr(sound, 'pitch'):
            try:
                sound.pitch = 1.06
            except Exception:
                pass
        if not streak_rise:
            return sound

        def play_rise(dt):
            rise = self._get_event_sound(AudioEvent.SFX_CORRECT)
            if not rise:
                return
            try:
                if hasattr(rise, 'pitch'):
                    rise.pitch = 1.15
                rise.seek(0)
                rise.volume = max(0.0, min(1.0, volume * 0.8))
                rise.loop = False
                rise.play()
            except Exception:
                return

            def reset_pitch(reset_dt):
                try:
                    if hasattr(rise, 'pitch'):
                        rise.pitch = 1.0
                except Exception:
                    pass

            Clock.schedule_once(reset_pitch, 0.25)

        def reset_main_pitch(dt):
            if sound and hasattr(sound, 'pitch'):
                try:
                    sound.pitch = 1.0
                except Exception:
                    pass

        Clock.schedule_once(reset_main_pitch, 0.25)

        Clock.schedule_once(play_rise, 0.06)
        return sound

    def play_wrong_feedback(self, volume=0.3):
        """Play a muted fail feedback sound."""
        sound = self._get_event_sound(AudioEvent.SFX_WRONG)
        if not sound:
            return None
        try:
            if hasattr(sound, 'pitch'):
                sound.pitch = 0.9
            sound.seek(0)
            sound.volume = max(0.0, min(1.0, volume))
            sound.loop = False
            sound.play()
        except Exception as e:
            Logger.warning(f"Audio: Could not play fail feedback: {e}")
            return None

        def reset_pitch(dt):
            if hasattr(sound, 'pitch'):
                try:
                    sound.pitch = 1.0
                except Exception:
                    pass

        Clock.schedule_once(reset_pitch, 0.25)
        return sound

    def _get_event_sound(self, event: AudioEvent):
        variants = self.event_sounds.get(event, [])
        if not variants:
            return None
        return random.choice(variants)

    def _cancel_ambience_fades(self, sound=None):
        if sound is None:
            if self._ambience_fade_in and self._ambience_sound:
                self._ambience_fade_in.cancel(self._ambience_sound)
            if self._ambience_fade_out and self._ambience_sound:
                self._ambience_fade_out.cancel(self._ambience_sound)
            self._ambience_fade_in = None
            self._ambience_fade_out = None
            return
        if self._ambience_fade_in:
            self._ambience_fade_in.cancel(sound)
        if self._ambience_fade_out:
            self._ambience_fade_out.cancel(sound)

    def _fade_in_ambience(self, sound, duration):
        if not sound:
            return
        try:
            sound.loop = True
            sound.volume = 0.0
            sound.play()
            self._ambience_fade_in = Animation(
                volume=self._ambience_volume,
                duration=duration,
                transition="in_out_quad",
            )
            self._ambience_fade_in.start(sound)
        except Exception as e:
            Logger.warning(f"Audio: Could not fade in ambience: {e}")

    def _fade_out_ambience(self, sound, duration):
        if not sound:
            return
        try:
            self._ambience_fade_out = Animation(
                volume=0.0,
                duration=duration,
                transition="in_out_quad",
            )

            def stop_after(anim, widget):
                try:
                    widget.stop()
                    widget.volume = self._ambience_volume
                except Exception:
                    pass

            self._ambience_fade_out.bind(on_complete=stop_after)
            self._ambience_fade_out.start(sound)
        except Exception as e:
            Logger.warning(f"Audio: Could not fade out ambience: {e}")

    def set_ambience(self, mode: str):
        """Set ambience loop: tunnel, station, or none."""
        if mode not in ("tunnel", "station", "none"):
            return
        if not self.enabled:
            mode = "none"

        self._refresh_active()

        if (
            mode == self._ambience_mode
            and self._ambience_sound
            and self._is_sound_playing(self._ambience_sound)
        ):
            return

        target_sound = None
        if mode == "tunnel":
            target_sound = self._get_event_sound(AudioEvent.AMB_TUNNEL) or self.tunnel_sound
        elif mode == "station":
            target_sound = self._get_event_sound(AudioEvent.AMB_STATION)

        duration = self._ambience_fade_duration
        current_sound = self._ambience_sound

        if mode == "none" or not target_sound:
            if current_sound and self._is_sound_playing(current_sound):
                self._cancel_ambience_fades(current_sound)
                self._fade_out_ambience(current_sound, duration)
            self._ambience_mode = "none"
            self._ambience_sound = None
            self.tunnel_sound_active = False
            return

        if target_sound == current_sound and self._is_sound_playing(target_sound):
            self._ambience_mode = mode
            self.tunnel_sound_active = mode == "tunnel"
            return

        if current_sound and current_sound != target_sound:
            self._cancel_ambience_fades(current_sound)
            self._fade_out_ambience(current_sound, duration)

        self._ambience_sound = target_sound
        self._ambience_mode = mode
        self.tunnel_sound_active = mode == "tunnel"

        if target_sound:
            self._cancel_ambience_fades(target_sound)
            self._fade_in_ambience(target_sound, duration)
    
    def _generate_tunnel_sound(self):
        """Generate a subtle looping tunnel sound (low-frequency whoosh)"""
        try:
            import wave
            import struct
            import math
            import tempfile
            
            # Generate a subtle tunnel sound using low-frequency modulation
            sample_rate = 22050
            duration = 2.0  # 2 seconds for smooth looping
            
            # Create temporary WAV file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp_file.name
            temp_file.close()
            
            with wave.open(temp_path, 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                
                samples = []
                buffer = [0.0] * int(sample_rate * duration)
                delay_samples = int(sample_rate * 0.055)  # 55ms slapback for subtle reverb
                decay = 0.22
                for i in range(int(sample_rate * duration)):
                    t = i / sample_rate

                    # Create a subtle modulated low frequency sound
                    # Uses two frequencies: 60Hz base + 30Hz modulation
                    base_freq = 60  # Very low frequency for tunnel effect
                    mod_freq = 30   # Modulation frequency for motion effect

                    # Base tone
                    base_wave = math.sin(2 * math.pi * base_freq * t)

                    # Modulation (creates a whooshing effect)
                    modulation = 0.5 + 0.5 * math.sin(2 * math.pi * mod_freq * t)

                    # Combine and add subtle higher harmonics for realism
                    combined = base_wave * modulation
                    harmonic = 0.2 * math.sin(2 * math.pi * base_freq * 2 * t) * modulation

                    # Apply soft envelope at start and end for smooth looping
                    envelope = 1.0
                    fade_in_duration = 0.2
                    fade_out_duration = 0.3

                    if t < fade_in_duration:
                        envelope = t / fade_in_duration
                    elif t > duration - fade_out_duration:
                        envelope = (duration - t) / fade_out_duration

                    # Subtle reverb by mixing a quiet, delayed copy
                    dry = 0.12 * envelope * (combined + harmonic)
                    wet = dry
                    if i >= delay_samples:
                        wet += buffer[i - delay_samples] * decay
                    buffer[i] = wet

                    value = int(32767 * max(-1.0, min(1.0, wet)))
                    samples.append(struct.pack('h', value))
                
                wav_file.writeframes(b''.join(samples))
            
            # Load the generated sound
            self.tunnel_sound = SoundLoader.load(temp_path)
            
            if self.tunnel_sound:
                Logger.info("Audio: Generated tunnel looping sound successfully")
            else:
                Logger.warning("Audio: Failed to load generated tunnel sound")
                
        except Exception as e:
            Logger.error(f"Audio: Could not generate tunnel sound: {e}")
            self.tunnel_sound = None
    
    def _generate_bonus_life_sound(self):
        """Generate a positive bonus life jingle (rising tones)"""
        try:
            import wave
            import struct
            import math
            import tempfile
            
            # Generate a cheerful rising 3-note jingle
            sample_rate = 22050
            total_duration = 0.6  # Total 600ms
            tone_duration = total_duration / 3  # 200ms per tone
            
            # Create temporary WAV file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp_file.name
            temp_file.close()
            
            with wave.open(temp_path, 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                
                # Three ascending tones for positive feedback
                # G4 (392 Hz), then C5 (523.25 Hz), then G5 (783.99 Hz)
                frequencies = [392, 523.25, 783.99]
                samples = []
                
                for freq in frequencies:
                    for i in range(int(sample_rate * tone_duration)):
                        t = i / sample_rate
                        
                        # Apply envelope (smooth fade in/out for each tone)
                        if i < sample_rate * 0.05:  # Fade in
                            envelope = (t / 0.05)
                        elif i > sample_rate * (tone_duration - 0.05):  # Fade out
                            envelope = (tone_duration - t) / 0.05
                        else:
                            envelope = 1.0
                        
                        # Generate tone
                        value = int(32767 * 0.4 * envelope * math.sin(2 * math.pi * freq * t))
                        samples.append(struct.pack('h', value))
                
                wav_file.writeframes(b''.join(samples))
            
            # Load the generated sound
            self.bonus_life_sound = SoundLoader.load(temp_path)
            
            if self.bonus_life_sound:
                Logger.info("Audio: Generated bonus life sound successfully")
            else:
                Logger.warning("Audio: Failed to load generated bonus life sound")
                
        except Exception as e:
            Logger.error(f"Audio: Could not generate bonus life sound: {e}")
            self.bonus_life_sound = None
    
    def _generate_direction_mode_sound(self):
        """Generate a distinct direction mode startup cue (descending tones)"""
        try:
            import wave
            import struct
            import math
            import tempfile
            
            # Generate a descending 3-note pattern for direction mode
            sample_rate = 22050
            total_duration = 0.5  # Total 500ms (slightly quicker)
            tone_duration = total_duration / 3  # ~167ms per tone
            
            # Create temporary WAV file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp_file.name
            temp_file.close()
            
            with wave.open(temp_path, 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                
                # Three descending tones for direction mode
                # G5 (783.99 Hz), then E5 (329.63 Hz), then C5 (261.63 Hz)
                # Descending = opposite direction
                frequencies = [783.99, 329.63, 261.63]
                samples = []
                
                for freq in frequencies:
                    for i in range(int(sample_rate * tone_duration)):
                        t = i / sample_rate
                        
                        # Apply envelope (quick fade in/out)
                        if i < sample_rate * 0.04:  # Fade in
                            envelope = (t / 0.04)
                        elif i > sample_rate * (tone_duration - 0.04):  # Fade out
                            envelope = (tone_duration - t) / 0.04
                        else:
                            envelope = 1.0
                        
                        # Generate tone with slight buzz/pulse
                        base_tone = math.sin(2 * math.pi * freq * t)
                        # Add subtle harmonic for richness
                        harmonic = 0.15 * math.sin(2 * math.pi * freq * 1.5 * t)
                        
                        # Combine
                        value = int(32767 * 0.35 * envelope * (base_tone + harmonic))
                        samples.append(struct.pack('h', value))
                
                wav_file.writeframes(b''.join(samples))
            
            # Load the generated sound
            self.direction_mode_sound = SoundLoader.load(temp_path)
            
            if self.direction_mode_sound:
                Logger.info("Audio: Generated direction mode startup sound successfully")
            else:
                Logger.warning("Audio: Failed to load generated direction mode sound")
                
        except Exception as e:
            Logger.error(f"Audio: Could not generate direction mode sound: {e}")
            self.direction_mode_sound = None
    
    def _generate_milestone_sound(self):
        """Generate soft celebratory milestone sound (5-tone pentatonic chime)"""
        try:
            import wave
            import struct
            import math
            import tempfile
            
            # Generate a soft, celebratory 5-tone pentatonic pattern
            sample_rate = 22050
            total_duration = 0.4  # Total 400ms (quick and snappy)
            tone_duration = total_duration / 5  # 80ms per tone
            
            # Create temporary WAV file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp_file.name
            temp_file.close()
            
            with wave.open(temp_path, 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                
                # Pentatonic scale progression (C-E-G-C-E for celebratory mood)
                # These frequencies create an uplifting, triumphant feel
                frequencies = [
                    261.63,  # C5
                    329.63,  # E5
                    392.00,  # G5
                    523.25,  # C6 (octave higher)
                    659.25   # E6 (octave higher)
                ]
                samples = []
                
                for freq in frequencies:
                    for i in range(int(sample_rate * tone_duration)):
                        t = i / sample_rate
                        
                        # Apply envelope with quick fade in/out
                        fade_time = 0.02  # 20ms fade
                        if i < sample_rate * fade_time:  # Fade in
                            envelope = (t / fade_time)
                        elif i > sample_rate * (tone_duration - fade_time):  # Fade out
                            envelope = (tone_duration - t) / fade_time
                        else:
                            envelope = 1.0
                        
                        # Generate tone with subtle bell-like quality
                        base_tone = math.sin(2 * math.pi * freq * t)
                        # Add very subtle harmonic for richness (1.5x frequency)
                        harmonic = 0.1 * math.sin(2 * math.pi * freq * 1.5 * t)
                        
                        # Combine
                        value = int(32767 * 0.25 * envelope * (base_tone + harmonic))
                        samples.append(struct.pack('h', value))
                
                wav_file.writeframes(b''.join(samples))
            
            # Load the generated sound
            self.milestone_sound = SoundLoader.load(temp_path)
            
            if self.milestone_sound:
                Logger.info("Audio: Generated milestone sound successfully")
            else:
                Logger.warning("Audio: Failed to load generated milestone sound")
                
        except Exception as e:
            Logger.error(f"Audio: Could not generate milestone sound: {e}")
            self.milestone_sound = None
    
    def play_tunnel_loop(self):
        """Start playing tunnel sound in a loop during train movement"""
        if not self.enabled:
            return
        self.set_ambience("tunnel")
    
    def stop_tunnel_sound(self, fade_duration=0.5):
        """Stop tunnel sound with fade-out effect"""
        if self._ambience_mode == "tunnel" and self._ambience_sound:
            self._cancel_ambience_fades(self._ambience_sound)
            self._fade_out_ambience(self._ambience_sound, fade_duration)
            self._ambience_mode = "none"
            self._ambience_sound = None
            self.tunnel_sound_active = False
            return
        if not self.tunnel_sound or not self.tunnel_sound_active:
            return

        try:
            # Cancel any existing fade animation
            if self.tunnel_fade_animation:
                self.tunnel_fade_animation.cancel(self.tunnel_sound)

            # Create fade-out animation
            self.tunnel_fade_animation = Animation(
                volume=0,
                duration=fade_duration,
                transition='in_quad'
            )

            # Stop sound after fade completes
            self.tunnel_fade_animation.bind(on_complete=self._stop_tunnel_callback)
            self.tunnel_fade_animation.start(self.tunnel_sound)

            Logger.info(f"Audio: Tunnel sound fading out over {fade_duration}s")
        except Exception as e:
            Logger.warning(f"Audio: Could not fade out tunnel sound: {e}")
            self._stop_tunnel_callback()
    
    def _stop_tunnel_callback(self, *args):
        """Stop tunnel sound playback"""
        try:
            if self.tunnel_sound:
                self.tunnel_sound.stop()
                self.tunnel_sound.volume = 0.3  # Reset volume for next playback
            self.tunnel_sound_active = False
            Logger.info("Audio: Tunnel sound stopped")
        except Exception as e:
            Logger.warning(f"Audio: Could not stop tunnel sound: {e}")
            self.tunnel_sound_active = False
    
    def play_bonus_life_sound(self):
        """Play positive bonus life jingle"""
        if not self.enabled or not self.bonus_life_sound:
            return
        
        try:
            # Reset to beginning and play
            self.bonus_life_sound.seek(0)
            self.bonus_life_sound.volume = 0.6  # Prominent volume
            self.bonus_life_sound.play()
            Logger.info("Audio: Bonus life sound played")
        except Exception as e:
            Logger.warning(f"Audio: Could not play bonus life sound: {e}")
    
    def play_direction_mode_cue(self):
        """Play direction mode startup cue"""
        if not self.enabled or not self.direction_mode_sound:
            return
        
        try:
            # Reset to beginning and play
            self.direction_mode_sound.seek(0)
            self.direction_mode_sound.volume = 0.5  # Moderate volume
            self.direction_mode_sound.play()
            Logger.info("Audio: Direction mode startup cue played")
        except Exception as e:
            Logger.warning(f"Audio: Could not play direction mode cue: {e}")
    
    def play_milestone_cue(self):
        """Play soft celebratory milestone sound (every 5 stations)"""
        if not self.enabled or not self.milestone_sound:
            return
        
        try:
            # Reset to beginning and play
            self.milestone_sound.seek(0)
            self.milestone_sound.volume = 0.4  # Soft but audible volume
            self.milestone_sound.play()
            Logger.info("Audio: Milestone cue played")
        except Exception as e:
            Logger.warning(f"Audio: Could not play milestone cue: {e}")
    
    def play_goal_anticipation_sound(self):
        """Play subtle anticipation sound when 1 station away from goal"""
        if not self.enabled:
            return
        if self.play_event(AudioEvent.SFX_GOAL_ANTICIPATION, volume=0.3):
            return

        # Use a softer version of the milestone sound
        if self.milestone_sound:
            try:
                self.milestone_sound.seek(0)
                self.milestone_sound.volume = 0.3
                self.milestone_sound.play()
                # Reset volume after playing
                Clock.schedule_once(lambda dt: setattr(self.milestone_sound, 'volume', 0.4), 0.5)
                Logger.info("Audio: Goal anticipation sound played")
            except Exception as e:
                Logger.warning(f"Audio: Could not play goal anticipation: {e}")
    
    def play_goal_celebration_sound(self):
        """Play celebratory sound when goal is reached (different from milestone)"""
        if not self.enabled:
            return

        if self.play_event(AudioEvent.SFX_GOAL_CELEBRATION, volume=0.6):
            return
        
        try:
            # Play a combination: direction mode sound + milestone
            if self.direction_mode_sound:
                self.direction_mode_sound.seek(0)
                self.direction_mode_sound.volume = 0.5
                self.direction_mode_sound.play()
            
            # Follow with milestone sound at higher volume
            if self.milestone_sound:
                def play_delayed(dt):
                    self.milestone_sound.seek(0)
                    self.milestone_sound.volume = 0.6
                    self.milestone_sound.play()
                    # Reset volume
                    Clock.schedule_once(lambda dt: setattr(self.milestone_sound, 'volume', 0.4), 0.8)
                
                Clock.schedule_once(play_delayed, 0.3)
            Logger.info("Audio: Goal celebration sound played")
        except Exception as e:
            Logger.warning(f"Audio: Could not play goal celebration: {e}")

    def play_line_completed(self):
        """Play sound when a line is completed."""
        if self.play_event(AudioEvent.SFX_LINE_COMPLETED, volume=0.6):
            return
        self.play_milestone_cue()
    
    def enable(self):
        """Enable sound effects"""
        self.enabled = True
    
    def disable(self):
        """Disable sound effects"""
        self.enabled = False
    
    def set_volume(self, volume: float):
        """Set volume for all sounds (0.0 to 1.0)"""
        for sound in self.sounds.values():
            if sound:
                sound.volume = max(0.0, min(1.0, volume))
