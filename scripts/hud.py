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

                