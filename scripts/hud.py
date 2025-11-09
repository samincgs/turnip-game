import pygame
import math

import scripts.pgtools as pt

INSTRUCTION_TEXT = ['Use a and d to move and space to jump', 'Collect keys and escape']

class HUD:
    def __init__(self, game):
        self.game = game
        self.main_font = pt.Font(font_color=(255, 255, 255))
        
        self.instruction_index = 0
        self.level_text_loc = -100
            
    def render(self, surf, offset=(0, 0)):
        level_text = self.game.level + 1
        
        self.level_text_loc += (2 - self.level_text_loc) / 10
        
        self.main_font.render(surf, 'Level: ' + str(level_text), (int(self.level_text_loc), 2))
        
        instruction_text = INSTRUCTION_TEXT[self.instruction_index] if self.instruction_index < len(INSTRUCTION_TEXT) else None
        if instruction_text:
            self.main_font.outline_text(surf, instruction_text, (surf.get_width() // 2 - self.main_font.get_width(instruction_text) // 2, surf.get_height() // 2 - self.main_font.get_height() // 2), outline_color=(8, 20, 30))
        
        if self.instruction_index == 0:
            if self.game.input.pressing('right') or self.game.input.pressing('left'):
                self.instruction_index += 1
        elif self.instruction_index == 1:
            if self.game.input.pressing_any_key():
                self.instruction_index += 1
        
        door_rect = pygame.Rect(self.game.door['pos'][0], self.game.door['pos'][1], 7, 11)
        if (self.game.keys_collected == len(self.game.keys)) and not self.game.camera.rect.colliderect(door_rect):
            angle_to_door = math.atan2(self.game.door['pos'][1] - self.game.player.pos[1], self.game.door['pos'][0] - self.game.player.pos[0])
            start_pos = (self.game.player.center[0] + 20, self.game.player.center[1] - 15)
            points = [
                [start_pos[0] + math.cos(angle_to_door) * 6, start_pos[1] + math.sin(angle_to_door) * 6],
                [start_pos[0] + math.cos(angle_to_door + math.pi / 2) * 3, start_pos[1] + math.sin(angle_to_door  + math.pi / 2) * 3],
                [start_pos[0] + math.cos(angle_to_door - math.pi / 2) * 3, start_pos[1] + math.sin(angle_to_door - math.pi / 2) * 3],
            ]        
            points = [[p[0] - offset[0], p[1] - offset[1]] for p in points]
                
            pygame.draw.polygon(surf, (255, 255, 255), points=points)

                