import math
import pygame

from .entities import Entity

class VFX:
    def __init__(self, game):
        self.game = game
        
        self.sparks = []
        self.circles = []
        self.action_animations = []
    
    def add_spark(self, pos, angle, speed, decay_rate=2):
        self.sparks.append(Spark(pos, angle, speed, decay_rate))
        
    def add_anim(self, pos, a_type, size=(1, 1)):
        self.action_animations.append(ActionAnimation(self.game, pos, size, a_type))
        
    def update(self, dt):
        for spark in self.sparks.copy():
            kill = spark.update(dt)
            if kill:
                self.sparks.remove(spark)
                
        for anim in self.action_animations:
            kill = anim.update(dt)
            if kill:
                self.action_animations.remove(anim)
                
    def render(self, surf, offset=(0, 0)):
        for spark in self.sparks:
            spark.render(surf, offset=offset)
        for anim in self.action_animations:
            anim.render(surf, offset=offset)
        
            

class Spark:
    def __init__(self, pos, angle, speed, decay_rate=2):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
        self.decay_rate = decay_rate
            
    def update(self, dt):
        
        self.pos[0] += math.cos(self.angle) * self.speed 
        self.pos[1] += math.sin(self.angle) * self.speed
        
        self.speed -= self.decay_rate
        if self.speed <= 0:
            return True 
        

    def render(self, surf, offset=(0, 0)):
        render_pos = (self.pos[0] - offset[0], self.pos[1] - offset[1])
        
        points = [
            (render_pos[0] + math.cos(self.angle) * self.speed * 3, render_pos[1] + math.sin(self.angle) * self.speed * 3),
            (render_pos[0] + math.cos(self.angle + math.pi / 2) * self.speed * 0.5, render_pos[1] + math.sin(self.angle + math.pi / 2) * self.speed * 0.5),
            (render_pos[0] + math.cos(self.angle + math.pi) * self.speed * 3, render_pos[1] + math.sin(self.angle + math.pi) * self.speed * 3),
            (render_pos[0] + math.cos(self.angle - math.pi / 2) * self.speed * 0.5, render_pos[1] + math.sin(self.angle - math.pi / 2) * self.speed * 0.5),
        ]
        
        pygame.draw.polygon(surf, (255, 255, 255), points=points)
        
        
class Circle:
    pass


class ActionAnimation(Entity):
    def __init__(self, game, pos, size, e_type):
        super().__init__(game, pos, size, e_type)
        
    def update(self, dt):
        super().update(1/ 60)
        
        if self.active_animation.finished:
            return True
        
    def render(self, surf, offset=(0, 0)):
        surf.blit(self.img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))