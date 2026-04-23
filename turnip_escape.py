import random
import math
import os

import pygame

import scripts.pgtools as pt
from scripts.player import Player
from scripts.key import Key
from scripts.hud import HUD
from scripts.turret import Turret
from scripts.mole import Mole

RESOLUTION = (240, 160)
RENDER_SCALE = 3
TILE_SIZE = 8

LEVEL_TIMERS = [30, 40]

class Game:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((RESOLUTION[0] * RENDER_SCALE, RESOLUTION[1] * RENDER_SCALE))
        self.display = pygame.Surface((RESOLUTION[0], RESOLUTION[1]))
        self.ui_display = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        pygame.display.set_caption('turnip escape')
        self.clock = pygame.time.Clock()
        
        self.animations = pt.AnimationManager()
        self.tilemap = pt.Tilemap(self, tile_size=TILE_SIZE)            
        self.input = pt.Input(RENDER_SCALE) 
        
        self.vfx = pt.VFX(self)
        self.particle_manager = pt.ParticleManager()
        self.camera = pt.Camera(self.display.get_size(), tile_size=TILE_SIZE, lag=20)
        self.hud = HUD(self)
        
        self.misc_images = pt.utils.load_imgs_dict('data/images/misc')
        self.fallen_rock_imgs = pt.utils.load_imgs('data/images/falling_rocks')

        self.master_clock = 0
        self.dt = 0
        self.level = 0
        
        self.load_level(self.level)
        
    def load_level(self, level):
        self.tilemap.load_map(f'data/maps/map_{level}.json')
        
        self.transition = -60
        self.keys_collected = 0
        self.reset_timer = 15
        self.timer = LEVEL_TIMERS[self.level]

        self.door_entered = False

        self.player = Player(self, self.tilemap.extract(('spawners', (0, )), False, False)[0]['pos'], (4, 8))
        self.camera.set_target(self.player)
        
        self.falling_rocks = self.tilemap.extract(('decor', (0, 1)), True)
        self.door = self.tilemap.extract(('spawners', (2,)), keep=False)[0]
        
        self.keys = self.tilemap.load_entity(Key, ('spawners', {1}), (5, 9))
        self.turrets = self.tilemap.load_entity(Turret, ('spawners', {3}), (12, 6))
        self.enemies = self.tilemap.load_entity(Mole, ('spawners', {4}), (6, 5), False)
        
        self.rocks = []
        self.bg_particles = []
        self.projectiles = []
        self.vfx.reset()
        self.hud.reset()
        self.particle_manager.reset()
        
        self.hud.level_text_loc = -100
        self.zoom = 0
        self.torch_radius = [15, 27]
        self.collided_torch = None

    def run(self):
        while True:
            
            self.display.fill((6, 5, 15))
            self.ui_display.fill((0, 0, 0, 0))
            
            self.master_clock += 1

            if (self.hud.instruction_index >= self.hud.instruction_len):
                self.timer = max(self.timer - self.dt, 0)
            
            if (self.timer <= 0) and (not self.player.dead) and (not self.door_entered):
                self.player.hit = True

            if self.transition != 0:
                self.transition =  min(self.transition + 1, 60)
                if self.transition >= 60:
                    self.reset_timer = max(self.reset_timer - 1, 0)
                    if not self.reset_timer:
                        if self.door_entered:
                            self.level = min(self.level + 1, len(os.listdir('data/maps')))
                        self.load_level(self.level)
                        
            edges = self.tilemap.get_map_edges()
            clamped = [False, False]
            if self.camera.scroll[0] < edges[0]:
                self.camera.scroll[0] = edges[0]
                clamped[0] = True
            if self.camera.scroll[0] > edges[1] - self.display.get_width():
                self.camera.scroll[0] = edges[1] - self.display.get_width()
                clamped[0] = True
            if self.camera.scroll[1] < edges[2]:
                self.camera.scroll[1] = edges[2]
                clamped[1] = True
            if self.camera.scroll[1] > edges[3] - self.display.get_height():
                self.camera.scroll[1] = edges[3] - self.display.get_height()
                clamped[1] = True

            self.bg_particles[-300:]
            
                
            door = self.door
            door_img = self.tilemap.tiles[door['type']][door['variant']]
            door_rect = pygame.Rect(door['pos'][0], door['pos'][1], 7, 11)
            if (self.player.rect.collidepoint(door_rect.center)) and not self.transition and (self.keys_collected == len(self.keys)):
                self.transition = max(self.transition, 1)
                self.door_entered = True  
            if self.master_clock // 20 % 4 > 0 and (self.keys_collected == len(self.keys)):
                pt.utils.outline(self.display, door_img, (int(door['pos'][0] - self.camera.pos[0]), int(door['pos'][1] - self.camera.pos[1])))
            self.display.blit(door_img, (int(door['pos'][0] - self.camera.pos[0]), int(door['pos'][1] - self.camera.pos[1])))
            
            self.tilemap.render_visible(self.display, visible_range=self.camera.get_visible_screen, offset=self.camera.pos)
            
            for rock in self.rocks.copy(): # pos, speed, img
                rock[0][1] += rock[1]
                if self.tilemap.tile_collide((rock[0][0] + rock[2].get_width() // 2, rock[0][1] + rock[2].get_height() // 2)):
                    for i in range(4):
                        angle = math.radians(random.uniform(15, 165)) - math.pi
                        speed = 60 + random.random() * 30
                        decay_rate = 300 + random.random() * 40
                        self.vfx.sparks.append(pt.Spark(rock[0],  angle, speed, decay_rate))
                    self.rocks.remove(rock)
                    break
                
                if self.player.rect.collidepoint(rock[0]) and not self.player.hit:
                    self.rocks.remove(rock)
                    self.player.hit = True

                render_pos = (rock[0][0] - self.camera.pos[0], rock[0][1] - self.camera.pos[1])
                pt.utils.outline(self.display, rock[2], render_pos)
                self.display.blit(rock[2], render_pos)

            for key in self.keys:
                key.update(self.dt) 
                key.render(self.display, offset=self.camera.pos)
                
            for turret in self.turrets:
                turret.update(self.dt) 
                turret.render(self.display, offset=self.camera.pos)

            for torch in self.tilemap.extract(('torches', (0, 1)), True):
                if torch != self.collided_torch:
                    pt.utils.glow_blit(self.display, loc=(torch['pos'][0] - self.camera.pos[0] - 15 + 4, torch['pos'][1] - self.camera.pos[1] - 15), radius=15, glow_color=(3, 7, 23))
                    pt.utils.glow_blit(self.display, loc=(torch['pos'][0] - self.camera.pos[0] - 27 + 4, torch['pos'][1] - self.camera.pos[1] - 27), radius=27, glow_color=(3, 7, 23))
                else:
                    pt.utils.glow_blit(self.display, loc=(torch['pos'][0] - self.camera.pos[0] - self.torch_radius[0] + 4, torch['pos'][1] - self.camera.pos[1] - self.torch_radius[0]), radius=self.torch_radius[0], glow_color=(3, 7, 23))
                    pt.utils.glow_blit(self.display, loc=(torch['pos'][0] - self.camera.pos[0] - self.torch_radius[1] + 4, torch['pos'][1] - self.camera.pos[1] - self.torch_radius[1]), radius=self.torch_radius[1], glow_color=(3, 7, 23))
                
                collided = False
                torch_rect = pygame.Rect(torch['pos'][0], torch['pos'][1], 7, 10)
                if self.player.rect.colliderect(torch_rect):
                    self.collided_torch = torch
                    collided = True
                
                if not collided:
                    self.particle_manager.particles.append(pt.Particle(self, (torch['pos'][0] + 4, torch['pos'][1] + 3), (4 + random.random() * -8, -4 + random.random() * -8), 'particles', decay_rate=1.7 + random.random(), start_frame=2 + random.random() * 3, glow=(3, 3 + random.randint(1, 3), 8 + random.randint(1, 6)), glow_radius=3 + random.random() * 6))

            if self.collided_torch:
                torch_rect = pygame.Rect(self.collided_torch['pos'][0], self.collided_torch['pos'][1], 7, 10)
                if self.player.rect.colliderect(torch_rect):
                    self.torch_radius[0] = self.torch_radius[0] // 2
                    self.torch_radius[1] = self.torch_radius[1] // 2
                if not self.player.rect.colliderect(torch_rect):
                    self.torch_radius[0] = min(self.torch_radius[0] + self.dt * 15, 15)
                    self.torch_radius[1] = min(self.torch_radius[1] + self.dt * 30, 27)
                    if self.torch_radius[0] == 15 and self.torch_radius[1] == 27:
                        self.collided_torch = None
            
            for mole in self.enemies:
                mole.update(self.dt)
                mole.render(self.display, offset=self.camera.pos)
            
            self.vfx.update(self.dt)
            self.vfx.render(self.display, offset=self.camera.pos)
            
            self.particle_manager.update(self.dt)
            self.particle_manager.render(self.display, self.camera.pos)
            
            self.player.update()
            self.player.render(self.display, offset=(self.camera.float_pos[0] + clamped[0], self.camera.float_pos[1] + clamped[1]))
            
            # pos, angle, speed, timer, 
            for proj in self.projectiles.copy():
                proj[0][0] += math.cos(proj[1]) * proj[2]
                proj[0][1] += math.sin(proj[1]) * proj[2]
                
                proj[3] += 1
                
                orig_img = self.misc_images['projectile']
                sin_radius = 7 + math.sin(self.master_clock / 12) * 0.5 
                img = pygame.transform.rotate(orig_img, -math.degrees(proj[1]))
                loc = (proj[0][0] - self.camera.pos[0] - img.get_width() // 2, proj[0][1] - self.camera.pos[1] - img.get_height() // 2)
                pt.utils.outline(self.display, img, loc)
                self.display.blit(img, loc)
                pt.utils.glow_blit(self.display, (loc[0] + img.get_width() // 2 + 1 - sin_radius, loc[1] + img.get_height() // 2 + 1 - sin_radius), sin_radius, (61, 15, 37))
                
                if proj[3] >= 600:
                    self.projectiles.remove(proj)
                if self.player.rect.collidepoint(proj[0]) and not self.player.hit:
                    self.projectiles.remove(proj)
                    self.player.hit = True
            
            self.hud.render(self.ui_display, offset=self.camera.pos)
            
            self.camera.update()
            self.input.update()
                        
            for rock in self.falling_rocks:
                img_size = self.tilemap.tiles[rock['type']][rock['variant']].get_size()
                rock_collide_check = (rock['pos'][0] + random.random() * img_size[0], rock['pos'][1] + img_size[1] - 2)
                if not self.tilemap.tile_collide(rock_collide_check):
                    if random.randint(1, 200) == 1:
                        speed = 0.5 + random.random()
                        img = random.choice(self.fallen_rock_imgs)
                        self.rocks.append([list(rock_collide_check), speed, img])
                        
            
            if self.transition:
                black_surf = pygame.Surface(self.display.get_size())
                black_surf.set_alpha(abs(self.transition) / 60 * 255)
                self.display.blit(black_surf, (0, 0))
            
            
            self.display.blit(self.ui_display, (0, 0))
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.dt = self.clock.tick(60) / 1000
            
if __name__ == '__main__':
    Game().run()