"""
Particle System - Lightweight particle effects with object pooling
"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock
import random
import math


class Particle:
    """Single particle with position, velocity, lifetime"""
    
    def __init__(self):
        self.active = False
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.lifetime = 0
        self.max_lifetime = 1.0
        self.size = 4
        self.color = (1, 1, 1, 1)
        self.shape = None  # Canvas instruction
    
    def reset(self, x, y, vx, vy, lifetime, size, color):
        """Reset particle with new values"""
        self.active = True
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = 0
        self.max_lifetime = lifetime
        self.size = size
        self.color = color
    
    def update(self, dt):
        """Update particle physics"""
        if not self.active:
            return False
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Apply gravity
        self.vy -= 300 * dt
        
        # Update lifetime
        self.lifetime += dt
        
        if self.lifetime >= self.max_lifetime:
            self.active = False
            return False
        
        return True
    
    def get_alpha(self):
        """Get current alpha based on lifetime"""
        progress = self.lifetime / self.max_lifetime
        return max(0, 1.0 - progress)


class ParticleSystem(Widget):
    """Manages particle pool and rendering"""
    
    def __init__(self, max_particles=60, **kwargs):
        super().__init__(**kwargs)
        
        self.max_particles = max_particles
        self.particles = []
        self.particle_shapes = {}  # Map particle to canvas instruction
        
        # Create particle pool
        for _ in range(max_particles):
            self.particles.append(Particle())
        
        # Update loop
        Clock.schedule_interval(self.update, 1.0 / 60.0)
    
    def emit_line_clear(self, line_y, board_offset_x, board_offset_y, cell_size):
        """Emit particles for line clear effect"""
        # Emit 10-15 particles along the line
        count = random.randint(10, 15)
        
        for i in range(count):
            particle = self._get_inactive_particle()
            if not particle:
                break
            
            # Position along the line
            x = board_offset_x + random.uniform(0, 10 * cell_size)
            y = board_offset_y + line_y * cell_size + cell_size / 2
            
            # Random velocity
            angle = random.uniform(-math.pi/3, math.pi/3)
            speed = random.uniform(100, 250)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed + 150  # Upward bias
            
            # Random color (bright candy colors)
            colors = [
                (1.0, 0.3, 0.3),  # Red
                (0.3, 1.0, 0.3),  # Green
                (0.3, 0.3, 1.0),  # Blue
                (1.0, 1.0, 0.3),  # Yellow
                (1.0, 0.3, 1.0),  # Magenta
                (0.3, 1.0, 1.0),  # Cyan
            ]
            color = random.choice(colors) + (1.0,)
            
            # Size
            size = random.uniform(4, 8)
            
            # Lifetime
            lifetime = random.uniform(0.4, 0.7)
            
            particle.reset(x, y, vx, vy, lifetime, size, color)
            
            # Create or reuse canvas instruction
            if particle not in self.particle_shapes:
                with self.canvas:
                    Color(*color)
                    # Use star shape (4-point)
                    shape = self._create_star_shape(x, y, size)
                    self.particle_shapes[particle] = shape
    
    def emit_combo(self, x, y):
        """Emit particles for combo effect"""
        count = random.randint(5, 8)
        
        for i in range(count):
            particle = self._get_inactive_particle()
            if not particle:
                break
            
            # Radial burst
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(80, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            color = (1.0, 0.8, 0.0, 1.0)  # Gold
            size = random.uniform(3, 6)
            lifetime = random.uniform(0.3, 0.5)
            
            particle.reset(x, y, vx, vy, lifetime, size, color)
    
    def _get_inactive_particle(self):
        """Get an inactive particle from pool"""
        for particle in self.particles:
            if not particle.active:
                return particle
        return None
    
    def _create_star_shape(self, x, y, size):
        """Create star-shaped particle (simple diamond)"""
        # For performance, use Ellipse (can be upgraded to Triangle mesh later)
        return Ellipse(pos=(x - size/2, y - size/2), size=(size, size))
    
    def update(self, dt):
        """Update all active particles"""
        for particle in self.particles:
            if not particle.active:
                continue
            
            # Update physics
            still_alive = particle.update(dt)
            
            # Update rendering
            if particle in self.particle_shapes:
                shape = self.particle_shapes[particle]
                
                if still_alive:
                    # Update position
                    shape.pos = (particle.x - particle.size/2, particle.y - particle.size/2)
                    
                    # Update alpha (fade out)
                    alpha = particle.get_alpha()
                    # Note: Color instruction should be updated separately
                    # For now, we'll hide by moving offscreen when dead
                else:
                    # Hide dead particles offscreen
                    shape.pos = (-1000, -1000)
    
    def clear(self):
        """Clear all particles"""
        for particle in self.particles:
            particle.active = False
            if particle in self.particle_shapes:
                self.particle_shapes[particle].pos = (-1000, -1000)
