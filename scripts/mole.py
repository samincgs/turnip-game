import pygame
import random

import scripts.pgtools as pt

class Mole(pt.PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size, 'mole')
        self.direction = 1
        self.gravity = 0.05
        self.move_timer = 0
        self.terminal_velocity[1] = 1
        
    def update(self, dt):
        super().update(1/60)
        
        player = self.game.player
        
        self.move_timer = max(0, self.move_timer - 1)
        
        if not self.move_timer:
            if random.random() < 0.009:
                self.move_timer = random.randint(20, 100)
                for i in range(6):
                    self.game.particle_manager.particles.append(pt.Particle(self, self.rect.topright if self.direction == 1 else self.pos, (10 + random.random() * -20, random.random() * -2), 'particles', gravity=0.5, decay_rate=random.random() * 0.75, start_frame=5, custom_color=(51, 48, 63), physics=self.game.tilemap))
        if self.move_timer:
            self.frame_movement[0] += 0.3 * self.direction
            if not self.game.tilemap.tile_collide((self.center[0] + 3 if self.direction == 1 else self.center[0] - 3, self.rect.bottom + 14)):
                self.direction *= -1
        
        if self.rect.colliderect(player.rect):
            player.die()
        
        self.physics_update(1/60, self.game.tilemap)
    
        
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)