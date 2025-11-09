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
        self.turret_handle_tip = (0, 0)
                
    def update(self, dt):
        player = self.game.player
        
        self.turret_handle_tip = (self.center[0] + math.cos(self.turret_handle_rot) * self.rotated_turret_handle_img.get_width() // 2, self.center[1] + math.sin(self.turret_handle_rot) * self.rotated_turret_handle_img.get_height() // 2 - 3)
        player_angle = math.atan2(player.center[1] - self.center[1] + 2, player.center[0] - self.center[0])
        self.turret_handle_rot = player_angle
        
        
        
        if random.randint(1, 200) == 1:
            speed = 0.75 + random.random() * 0.5
            self.game.projectiles.append([[self.turret_handle_tip[0], self.turret_handle_tip[1]], self.turret_handle_rot, speed, 0])
            # turret gun sparks
            for angle in [40, -40, 0]:
                speed = 60 + random.random() * 30
                angle = player_angle + math.radians(angle)
                self.game.vfx.sparks.append(pt.Spark(self.turret_handle_tip, angle, speed, decay_rate = 200 + random.random() * 40))
                
        # if self.rect.colliderect(player.rect):
        #     player.die()
            
            
        
        
    
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        
        self.rotated_turret_handle_img = pygame.transform.rotate(self.turret_handle_img, -math.degrees(self.turret_handle_rot))
        turret_handle_loc = (self.center[0] - offset[0] - self.rotated_turret_handle_img.get_width() // 2, self.center[1] - offset[1] - 3 - self.rotated_turret_handle_img.get_height() // 2)        
        
        surf.blit(self.rotated_turret_handle_img, turret_handle_loc)
        
        # pygame.draw.circle(surf, (255, 0, 0), self.turret_handle_tip, 1, 1)
        # pygame.draw.rect(surf, (255, 0, 0), pygame.Rect(*turret_handle_loc, img.get_width(), img.get_height()), width=1)
        

        