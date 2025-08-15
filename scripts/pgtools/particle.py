from .utils import palette_swap, glow_blit
from .entities import Entity

class ParticleManager:
    def __init__(self):
        self.particles = []
        
    def update(self, dt):
        for particle in self.particles.copy():
            kill = particle.update(dt)
            if kill:
                self.particles.remove(particle)
                
    def render(self, surf, offset=(0, 0)):
        for particle in self.particles:
            particle.render(surf, offset=offset)

class Particle(Entity):
    def __init__(self, game, pos, velocity, p_type, decay_rate=0.1, start_frame=0, custom_color=None, physics=None, fall=None, glow=None, glow_radius=None):
        super().__init__(game, pos, (1, 1), p_type)
        self.velocity = velocity
        self.decay_rate = decay_rate
        self.frame = start_frame
        self.custom_color = custom_color
        self.physics = physics
        self.fall = fall
        self.glow = glow # color
        self.glow_radius = glow_radius
        
        self.despawn = False
        
    
    @property
    def img(self):
        return self.active_animation.images[int(self.frame)]
    
    def update(self, dt):
        self.pos[0] += self.velocity[0] * dt
        self.pos[1] += self.velocity[1] * dt
        if self.fall:
            self.velocity[1] += self.fall
        
        self.frame += self.decay_rate * dt
        self.frame = min(self.frame, len(self.active_animation.images) - 1)
        if self.frame >= len(self.active_animation.images) - 1:
            self.despawn = True
                    
        return self.despawn
    
    def render(self, surf, offset=(0, 0)):
        img = self.img
        if self.custom_color:
            img = palette_swap(img, (255, 255, 255), self.custom_color)
            img.set_colorkey((0, 0, 0))
        
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))
        
        if self.glow:
            glow_blit(surf, (self.pos[0] - offset[0] - self.glow_radius, self.pos[1] - offset[1] - self.glow_radius), self.glow_radius, self.glow)
        
        
            