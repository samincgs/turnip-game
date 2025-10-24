import random
import math

import scripts.pgtools as pt

class Player(pt.PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size, 'player')
        self.air_timer = 0
        self.speed = 1.4
        self.max_jumps = 2
        self.acceleration = [0, 0]
        self.jumps = self.max_jumps
        self.dead = False
        self.target_rot = 0
        
    def die(self):
        self.dead = True
        self.game.transition = 1
        if self.flip[0]:
            self.velocity[0] = 2
            self.target_rot = -360
        else:
            self.velocity[0] = -2
            self.target_rot = 360
        self.velocity[1] = -6
        for i in range(60):
            self.game.vfx.sparks.append(pt.Spark(self.center, random.random() * math.pi * 2, 120 + random.random() * 60, 100 + random.random() * 50))
            self.game.particle_manager.particles.append(pt.Particle(self.game, self.center, (150 + random.random() * -300, 150 + random.random() * -300), 'particles', 2 + random.random() * 2, random.randint(1, 3), custom_color=random.choice([(245, 240, 201), (245, 240, 201), (245, 240, 201), (139, 232, 47), (38, 191, 30)])))
                 
    def update(self):
        super().update(1/60)
                
        if not self.dead:
            self.velocity[1] = min(3, self.velocity[1] + 0.1)
        else:
            self.velocity[1] = min(4, self.velocity[1] + 0.25)
            
        self.velocity[0] = pt.utils.normalize(self.velocity[0], 0.009)
        self.air_timer += 1
        
        self.rotation = pt.utils.normalize(self.rotation, 5, self.target_rot)
        if not self.dead and not self.game.door_entered:
            self.frame_movement[0] = (self.game.input.holding('right') - self.game.input.holding('left')) * self.speed 
            if self.game.input.pressing('jump'):
                if self.jumps:
                    self.game.vfx.add_anim((self.pos[0] - 3, self.pos[1] - 4), 'jump_anim')
                    self.velocity[1] = -1.85
                    self.air_timer = 5
                    self.jumps -= 1
        
        self.frame_movement[0] += self.velocity[0]
        self.frame_movement[1] += self.velocity[1]
                
        if not self.dead:
            if self.frame_movement[0] > 0:
                self.flip[0] = False
            if self.frame_movement[0] < 0:
                self.flip[0] = True
            
        if self.air_timer >= 5:
            self.set_action('jump')
        else:
            if self.frame_movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        
        
        self.physics_movement(self.game.tilemap if not self.dead else None, self.frame_movement)
        print(self.pos[0])
        if self.collision_directions['down'] or self.collision_directions['up']:
            self.velocity[1] = 0
        if self.collision_directions['down']:
            self.air_timer = 0
            self.jumps = self.max_jumps
            
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        
        
    