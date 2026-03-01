"""
Text-to-Speech Service
Handles voice announcements for metro stations in Catalan
"""
from kivy.utils import platform
from kivy.logger import Logger
from typing import Optional, Callable


class TTSService:
    """Text-to-Speech manager for metro station announcements"""
    
    def __init__(self, language: str = "ca", country: str = "ES"):
        """
        Initialize TTS service
        
        Args:
            language: Language code (default: "ca" for Catalan)
            country: Country code (default: "ES" for Spain)
        """
        self.language = language
        self.country = country
        self.tts = None
        self.is_initialized = False
        self.is_available = False
        
        # Queue management
        self.current_utterance_id = 0
        
        self._initialize()
    
    def _initialize(self):
        """Initialize TTS based on platform"""
        if platform == 'android':
            self._initialize_android()
        else:
            self._initialize_desktop()
    
    def _initialize_android(self):
        """Initialize Android TTS"""
        try:
            from jnius import autoclass, PythonJavaClass, java_method  # type: ignore
            
            # Import Android classes
            TextToSpeech = autoclass('android.speech.tts.TextToSpeech')  # type: ignore
            Locale = autoclass('java.util.Locale')  # type: ignore
            PythonActivity = autoclass('org.kivy.android.PythonActivity')  # type: ignore
            
            # Create listener for initialization
            class TTSInitListener(PythonJavaClass):
                __javainterfaces__ = ['android/speech/tts/TextToSpeech$OnInitListener']
                
                def __init__(self, callback):
                    super().__init__()
                    self.callback = callback
                
                @java_method('(I)V')
                def onInit(self, status):
                    self.callback(status)
            
            def on_tts_init(status):
                """Callback when TTS is initialized"""
                SUCCESS = 0  # TextToSpeech.SUCCESS
                if status == SUCCESS:
                    try:
                        # Set Catalan locale
                        locale = Locale(self.language, self.country)
                        result = self.tts.setLanguage(locale)
                        
                        # Check if language is available
                        LANG_AVAILABLE = 0  # TextToSpeech.LANG_AVAILABLE
                        LANG_COUNTRY_AVAILABLE = 1
                        LANG_COUNTRY_VAR_AVAILABLE = 2
                        
                        if result in [LANG_AVAILABLE, LANG_COUNTRY_AVAILABLE, LANG_COUNTRY_VAR_AVAILABLE]:
                            self.is_available = True
                            self.is_initialized = True
                            Logger.info(f"TTS: Initialized with {self.language}_{self.country}")
                        else:
                            Logger.warning(f"TTS: Language {self.language}_{self.country} not fully available")
                            self.is_available = True  # Still usable
                            self.is_initialized = True
                    except Exception as e:
                        Logger.error(f"TTS: Error setting language: {e}")
                else:
                    Logger.error("TTS: Initialization failed")
            
            # Create TTS instance
            activity = PythonActivity.mActivity
            listener = TTSInitListener(on_tts_init)
            self.tts = TextToSpeech(activity, listener)
            
            Logger.info("TTS: Android TTS initialization started")
            
        except Exception as e:
            Logger.error(f"TTS: Failed to initialize Android TTS: {e}")
            self.is_available = False
    
    def _initialize_desktop(self):
        """Initialize desktop TTS (fallback/mock)"""
        Logger.info("TTS: Desktop mode - using mock TTS")
        self.is_available = False
        self.is_initialized = True
    
    def speak(self, text: str, interrupt: bool = True) -> bool:
        """
        Speak text using TTS
        
        Args:
            text: Text to speak
            interrupt: If True, interrupts current speech (QUEUE_FLUSH)
                      If False, queues after current speech (QUEUE_ADD)
        
        Returns:
            True if speech was queued successfully
        """
        if not self.is_initialized or not self.is_available:
            Logger.debug(f"TTS: Not available - would speak: '{text}'")
            return False
        
        if platform == 'android':
            return self._speak_android(text, interrupt)
        else:
            Logger.info(f"TTS: [Mock] {text}")
            return True
    
    def _speak_android(self, text: str, interrupt: bool) -> bool:
        """Speak using Android TTS"""
        try:
            from jnius import autoclass  # type: ignore
            TextToSpeech = autoclass('android.speech.tts.TextToSpeech')  # type: ignore
            
            # Queue mode
            queue_mode = TextToSpeech.QUEUE_FLUSH if interrupt else TextToSpeech.QUEUE_ADD
            
            # Generate utterance ID
            self.current_utterance_id += 1
            utterance_id = f"utterance_{self.current_utterance_id}"
            
            # Speak
            result = self.tts.speak(text, queue_mode, None, utterance_id)
            
            SUCCESS = 0  # TextToSpeech.SUCCESS
            if result == SUCCESS:
                Logger.info(f"TTS: Speaking '{text}' (id: {utterance_id})")
                return True
            else:
                Logger.warning(f"TTS: Failed to queue speech: {result}")
                return False
                
        except Exception as e:
            Logger.error(f"TTS: Error speaking: {e}")
            return False
    
    def stop(self):
        """Stop current speech"""
        if not self.is_initialized or not self.is_available:
            return
        
        if platform == 'android':
            try:
                self.tts.stop()
                Logger.debug("TTS: Stopped")
            except Exception as e:
                Logger.error(f"TTS: Error stopping: {e}")
    
    def announce_station(self, station_name: str, interrupt: bool = True):
        """
        Announce a metro station name
        
        Args:
            station_name: Name of the station
            interrupt: Whether to interrupt current announcement
        """
        # Format announcement
        text = f"Estació: {station_name}"
        self.speak(text, interrupt)
    
    def announce_line(self, line_name: str, interrupt: bool = True):
        """
        Announce a metro line
        
        Args:
            line_name: Name of the line (e.g., "Línia 3")
            interrupt: Whether to interrupt current announcement
        """
        text = f"Línia: {line_name}"
        self.speak(text, interrupt)
    
    def announce_sequence(self, station_name: str, line_name: str, interrupt: bool = True):
        """
        Announce station and line together
        
        Args:
            station_name: Name of the station
            line_name: Name of the line
            interrupt: Whether to interrupt current announcement
        """
        text = f"{station_name}, {line_name}"
        self.speak(text, interrupt)
    
    def set_speech_rate(self, rate: float):
        """
        Set speech rate
        
        Args:
            rate: Speech rate multiplier (1.0 = normal, 0.5 = slow, 2.0 = fast)
        """
        if not self.is_initialized or not self.is_available:
            return
        
        if platform == 'android':
            try:
                result = self.tts.setSpeechRate(rate)
                SUCCESS = 0
                if result == SUCCESS:
                    Logger.info(f"TTS: Speech rate set to {rate}")
                else:
                    Logger.warning(f"TTS: Failed to set speech rate")
            except Exception as e:
                Logger.error(f"TTS: Error setting speech rate: {e}")
    
    def set_pitch(self, pitch: float):
        """
        Set speech pitch
        
        Args:
            pitch: Speech pitch multiplier (1.0 = normal, 0.5 = low, 2.0 = high)
        """
        if not self.is_initialized or not self.is_available:
            return
        
        if platform == 'android':
            try:
                result = self.tts.setPitch(pitch)
                SUCCESS = 0
                if result == SUCCESS:
                    Logger.info(f"TTS: Pitch set to {pitch}")
                else:
                    Logger.warning(f"TTS: Failed to set pitch")
            except Exception as e:
                Logger.error(f"TTS: Error setting pitch: {e}")
    
    def shutdown(self):
        """Shutdown TTS engine"""
        if not self.is_initialized:
            return
        
        if platform == 'android' and self.tts:
            try:
                self.tts.shutdown()
                Logger.info("TTS: Shutdown complete")
            except Exception as e:
                Logger.error(f"TTS: Error during shutdown: {e}")
        
        self.is_initialized = False
        self.is_available = False


# Global TTS instance (singleton pattern)
_tts_instance: Optional[TTSService] = None


def get_tts() -> TTSService:
    """
    Get global TTS service instance
    
    Returns:
        TTSService singleton instance
    """
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSService()
    return _tts_instance


def shutdown_tts():
    """Shutdown global TTS instance"""
    global _tts_instance
    if _tts_instance:
        _tts_instance.shutdown()
        _tts_instance = None


# Convenience functions
def speak(text: str, interrupt: bool = True) -> bool:
    """Speak text using global TTS instance"""
    return get_tts().speak(text, interrupt)


def announce_station(station_name: str, interrupt: bool = True):
    """Announce station using global TTS instance"""
    get_tts().announce_station(station_name, interrupt)


def announce_line(line_name: str, interrupt: bool = True):
    """Announce line using global TTS instance"""
    get_tts().announce_line(line_name, interrupt)
