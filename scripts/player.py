import random

import scripts.pgtools as pt

class Player(pt.PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size, 'player')
        self.air_timer = 0
        self.speed = 1.2
        self.max_jumps = 2
        self.jumps = self.max_jumps
        
    def update(self):
        super().update(1/60)
        
        self.velocity[1] = min(2, self.velocity[1] + 0.1)
        
        self.air_timer += 1
    
        self.frame_movement[0] = (self.game.input.holding('right') - self.game.input.holding('left')) * self.speed 
        if self.game.input.pressed('jump'):
            if not self.game.hud.tutorial['space']:
                self.game.hud.tutorial['space'] = True
            if self.jumps:
                self.game.vfx.add_anim((self.pos[0] - 3, self.pos[1] - 4), 'jump_anim')
                self.velocity[1] = -2
                self.air_timer = 5
                self.jumps -= 1
        
        self.frame_movement[1] += self.velocity[1]
        
        if self.frame_movement[0] > 0:
            self.flip[0] = False
            if not self.game.hud.tutorial['d']:
                self.game.hud.tutorial['d'] = True
        if self.frame_movement[0] < 0:
            self.flip[0] = True
            if not self.game.hud.tutorial['a']:
                self.game.hud.tutorial['a'] = True
            
        if self.air_timer >= 5:
            self.set_action('jump')
        else:
            if self.frame_movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        
        self.physics_movement(self.game.tilemap, self.frame_movement)
        if self.collision_directions['down']:
            self.velocity[1] = 0
            self.air_timer = 0
            self.jumps = self.max_jumps
        
        self.frame_movement = [0, 0]