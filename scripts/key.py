import math
import random
import random

import scripts.pgtools as pt

class Key(pt.Entity):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size, 'key')
        self.collected = False
        
        self.display_icon_loc = (self.game.display.get_width() - self.size[0] - 10, 8)
        self.base_y = pos[1] + size[1] // 2 - 3
        
        self.random_shift = random.uniform(0, 5)
        
    def update(self, dt):
        
        if not self.collected:
            self.pos[1] = self.base_y + math.sin(self.random_shift + self.game.master_clock * 0.05) * 3 
        
        if not self.collected and self.game.player.rect.colliderect(self.rect):
            self.game.vfx.circles.append(pt.Circle(self.game, self.center, 3, 3, (47, 91, 128), 8, 0.2))
            self.game.vfx.circles.append(pt.Circle(self.game, self.center, 3.5, 1.5, (255, 255, 255), 6, 0.3))
            self.collected = True
            self.game.keys_collected += 1
            self.pos = [self.pos[0] - self.game.camera.pos[0], self.pos[1] - self.game.camera.pos[1]] # convert world pos to screen pos
            
        if self.collected:
            self.pos[0] += (self.display_icon_loc[0] - self.pos[0]) * 0.08
            self.pos[1] += (self.display_icon_loc[1] - self.pos[1]) * 0.08
        
    def render(self, surf, offset=(0, 0)):
        offset = offset if not self.collected else (0, 0)
        super().render(surf, offset)