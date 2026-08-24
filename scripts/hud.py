import math

import pygame

import scripts.pgtools as pt

INSTRUCTION_TEXT = ['Use a and d to move and space to jump', 'Collect keys and escape']

class HUD:
    def __init__(self, game):
        self.game = game
        self.main_font = pt.Font(font_color=(255, 255, 255))
        self.black_font = pt.Font(font_color=(0, 0, 1))
        
        self.instruction_index = 0
        self.instruction_len = len(INSTRUCTION_TEXT)
        self.level_text_loc = -100
        self.display_key_loc = [319, 2]
        
        self.input_check = {'right': False, 'left': False, 'jump': False}
        self.current_text_loc = [0, 0]
        self.scroll_down = False
        
        self.start_time = None
    
    def reset(self):
        self.level_text_loc = -100
        self.display_key_loc = [319, 2]
        self.start_time = None        
        if self.game.level == 0:
            self.current_text_loc = [0, 0]
            self.instruction_index = 0
            self.scroll_down = False
            self.input_check = {'right': False, 'left': False, 'jump': False}
    
    def render(self, surf):
        
        level_text = self.game.level + 1
        self.level_text_loc += int(2 - self.level_text_loc) / 10
        self.display_key_loc[0] += int(219 - self.display_key_loc[0]) / 10
        
        self.black_font.render(surf, 'Level: ' + str(level_text), (int(self.level_text_loc) + 1, 3))
        self.main_font.render(surf, 'Level: ' + str(level_text), (int(self.level_text_loc), 2))
        
        if self.game.level == 0:
            instruction_text = INSTRUCTION_TEXT[self.instruction_index] if self.instruction_index < len(INSTRUCTION_TEXT) else ''
            text_loc = (0, 0)
            if not self.scroll_down:
                text_loc = (surf.get_width() // 2 - self.main_font.get_width(instruction_text) // 2, surf.get_height() // 2 - self.main_font.get_height() // 2)
            else:
                text_loc = (surf.get_width() // 2 - self.main_font.get_width(instruction_text) // 2, surf.get_height() + self.main_font.get_height())
                
            self.current_text_loc[0] = text_loc[0]
            self.current_text_loc[1] += (text_loc[1] - self.current_text_loc[1]) / 10
            
            if instruction_text:
                self.black_font.render(surf, instruction_text, (self.current_text_loc[0] + 1, self.current_text_loc[1] + 2))
                self.main_font.outline_text(surf, instruction_text, self.current_text_loc, outline_color=(47, 91, 128), spacing=(0, 1))
            
            if self.instruction_index == 0:
                if all(self.input_check.values()):
                    self.scroll_down = True
            elif self.instruction_index == 1:
                if self.game.input.pressing_any_key():
                    self.scroll_down = True
                    
            if self.current_text_loc[1] > surf.get_height():
                self.scroll_down = False
                self.current_text_loc = [0, 0]
                self.instruction_index += 1
                
            if self.game.show_door[0]:
                door_instruction = 'You must exit through this door'
                door_instruction_loc = self.game.display.get_width() // 2 - self.black_font.get_width(door_instruction) // 2
                self.black_font.render(surf, door_instruction, (door_instruction_loc, 60))
                self.main_font.outline_text(surf, door_instruction, (door_instruction_loc, 60), outline_color=(47, 91, 128), spacing=(0, 1))
                
                bob = math.sin(self.game.master_clock / 8) * 3
                arrow_start_pos = (self.game.door['pos'][0], self.game.door['pos'][1] + bob)
                
                arrow_points = [(arrow_start_pos[0],     arrow_start_pos[1] - 12), (arrow_start_pos[0] + 6, arrow_start_pos[1] - 12), (arrow_start_pos[0] + 3, arrow_start_pos[1] - 9)]
                arrow_points = [(p[0] - self.game.camera.pos[0], p[1] - self.game.camera.pos[1]) for p in arrow_points]
                
                for offset in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                    outline_points = [(p[0] + offset[0], p[1] + offset[1]) for p in arrow_points]
                    pygame.draw.polygon(surf, (15, 42, 63), outline_points)
                
                pygame.draw.polygon(surf, (255, 255, 255),arrow_points)
                
                
        img = self.game.tilemap.get_spritesheet_imgs(('spawners', (1,)))
        surf.blit(img, (int(self.display_key_loc[0]), int(self.display_key_loc[1])))
        
        keys_text = str(self.game.keys_collected) + '/' + str(len(self.game.keys))
        key_ui_pos = (int(self.display_key_loc[0]) + 8, self.display_key_loc[1] + 1)
        self.black_font.render(surf, keys_text, (key_ui_pos[0] + 1, key_ui_pos[1] + 2))
        self.main_font.outline_text(surf, keys_text, key_ui_pos, outline_color=(47, 91, 128), spacing=(0, 1))
        
        if not self.start_time:
            self.start_time = round(self.game.timer)
            
        timer = round(self.game.timer)

        minutes = timer // 60
        seconds = timer % 60

        timer_format = f"{minutes}:{seconds:02}"
        time_segment = self.start_time // 3
        
        self.black_font.render(surf, 'Timer:', (int(self.level_text_loc) + 1, 11 + 2))
        self.main_font.outline_text(surf, 'Timer:', (int(self.level_text_loc), 11), outline_color=(47, 91, 128), spacing=(0, 1))
        self.main_font.render(surf, 'Timer:', (int(self.level_text_loc), 11))
        
        color = (139, 232, 47) 
        if seconds <= time_segment:
            color = (202, 21, 57)
        elif seconds <= self.start_time - time_segment:
            color = (228, 214, 105)
        else:
            color = (139, 232, 47) 
        
        self.black_font.render(surf, timer_format, (int(self.level_text_loc) + self.main_font.get_width('Timer:') + 3, 11 + 1))
        self.main_font.render(surf, timer_format, (int(self.level_text_loc) + self.main_font.get_width('Timer:') + 2, 11), color=color)


                