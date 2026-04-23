import scripts.pgtools as pt

INSTRUCTION_TEXT = ['Use a and d to move and space to jump', 'Collect keys and escape']

class HUD:
    def __init__(self, game):
        self.game = game
        self.main_font = pt.Font(font_color=(255, 255, 255))
        
        self.instruction_index = 0
        self.instruction_removal_timer = 0
        self.instruction_len = len(INSTRUCTION_TEXT)
        self.level_text_loc = -100
        self.display_key_loc = [319, 2]
        
        self.input_check = {'right': False, 'left': False, 'jump': False}
        
        self.start_time = None
    
    def reset(self):
        self.level_text_loc = -100
        self.display_key_loc = [319, 2]
        self.start_time = None
    
    def render(self, surf, offset=(0, 0)):
        
        if (self.instruction_index == 1) and (not self.instruction_removal_timer):
            self.instruction_removal_timer = 100
            
        if self.instruction_removal_timer:            
            self.instruction_removal_timer = max(1, self.instruction_removal_timer - 1)
        
        level_text = self.game.level + 1
        
        self.level_text_loc += int(2 - self.level_text_loc) / 10
        self.display_key_loc[0] += int(219 - self.display_key_loc[0]) / 10
        
        self.main_font.render(surf, 'Level: ' + str(level_text), (int(self.level_text_loc), 2))
        
        instruction_text = INSTRUCTION_TEXT[self.instruction_index] if self.instruction_index < len(INSTRUCTION_TEXT) else None
        if instruction_text and self.instruction_removal_timer != 1:
            self.main_font.outline_text(surf, instruction_text, (surf.get_width() // 2 - self.main_font.get_width(instruction_text) // 2, surf.get_height() // 2 - self.main_font.get_height() // 2), outline_color=(47, 91, 128))
        
        if self.instruction_index == 0:
            if all(self.input_check.values()):
                self.instruction_index += 1
        elif self.instruction_index == 1:
            if self.game.input.pressing_any_key():
                self.instruction_index += 1
                
        img = self.game.tilemap.get_spritesheet_imgs(('spawners', (1,)))
        surf.blit(img, (int(self.display_key_loc[0]), int(self.display_key_loc[1])))
        self.main_font.render(surf, str(self.game.keys_collected) + '/' + str(len(self.game.keys)), (int(self.display_key_loc[0]) + 8, self.display_key_loc[1] + 1))
        
        if not self.start_time:
            self.start_time = round(self.game.timer)
            
        timer = round(self.game.timer)

        minutes = timer // 60
        seconds = timer % 60

        timer_format = f"{minutes}:{seconds:02}"
        
        self.main_font.render(surf, 'Timer:', (int(self.level_text_loc), 11))
        
        # TODO: tweak the colors
        self.main_font.render(surf, timer_format, (int(self.level_text_loc) + self.main_font.get_width('Timer:') + 2, 11), color=(139, 232, 47))


                