"""
Performance Monitor - FPS tracking and metrics
"""
from collections import deque
import time


class PerformanceMonitor:
    """Tracks FPS and performance metrics"""
    
    def __init__(self, window_size=5.0):
        """
        Args:
            window_size: Time window in seconds for averaging
        """
        self.window_size = window_size
        self.frame_times = deque()
        self.last_frame_time = time.time()
        self.enabled = False
    
    def enable(self):
        """Enable FPS tracking"""
        self.enabled = True
    
    def disable(self):
        """Disable FPS tracking"""
        self.enabled = False
    
    def frame_tick(self):
        """Call once per frame"""
        if not self.enabled:
            return
        
        current_time = time.time()
        
        # Remove old frames outside window
        cutoff_time = current_time - self.window_size
        while self.frame_times and self.frame_times[0] < cutoff_time:
            self.frame_times.popleft()
        
        # Add current frame
        self.frame_times.append(current_time)
        self.last_frame_time = current_time
    
    def get_fps(self):
        """Get average FPS over window"""
        if not self.enabled or len(self.frame_times) < 2:
            return 0.0
        
        time_span = self.frame_times[-1] - self.frame_times[0]
        if time_span <= 0:
            return 0.0
        
        return (len(self.frame_times) - 1) / time_span
    
    def get_frame_time_ms(self):
        """Get average frame time in milliseconds"""
        fps = self.get_fps()
        if fps <= 0:
            return 0.0
        return 1000.0 / fps
    
    def reset(self):
        """Clear all metrics"""
        self.frame_times.clear()
        self.last_frame_time = time.time()
