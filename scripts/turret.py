import math
import random
import pygame

import scripts.pgtools as pt 


class Turret(pt.Entity):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size, 'turret')
        
        self.turret_handle_img = self.game.misc_images['turret_handle']
        self.rotated_turret_handle_img = self.turret_handle_img.copy()
        self.turret_handle_rot = 0
    
    @property
    def handle_tip(self):
        return (self.center[0] + math.cos(self.turret_handle_rot) * self.rotated_turret_handle_img.get_width() // 2, self.center[1] + math.sin(self.turret_handle_rot) * self.rotated_turret_handle_img.get_height() // 2 - 3)
    
    def update(self, dt):
        player = self.game.player
        
        player_angle = math.atan2(player.center[1] - self.center[1] + 2, player.center[0] - self.center[0])
        self.turret_handle_rot = player_angle
        
        if random.randint(1, 300) == 1:
            speed = 1 + random.random() * 0.7
            self.game.projectiles.append([list(self.handle_tip), self.turret_handle_rot, speed, 0])
            # turret gun sparks
            for angle in [40, -40, 0]:
                speed = 70 + random.random() * 30
                angle = player_angle + math.radians(angle)
                self.game.vfx.sparks.append(pt.Spark(self.handle_tip, angle, speed, decay_rate = 200 + random.random() * 40))
                
        if self.rect.colliderect(player.rect):
            player.die()
            
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        
        self.rotated_turret_handle_img = pygame.transform.rotate(self.turret_handle_img, -math.degrees(self.turret_handle_rot))
        turret_handle_loc = (self.center[0] - offset[0] - self.rotated_turret_handle_img.get_width() // 2, self.center[1] - offset[1] - 3 - self.rotated_turret_handle_img.get_height() // 2)        
        
        surf.blit(self.rotated_turret_handle_img, turret_handle_loc)


        