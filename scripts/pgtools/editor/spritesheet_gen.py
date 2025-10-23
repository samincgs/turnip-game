import pygame
import sys
import os
import tkinter as tk
from tkinter import filedialog

RENDER_SCALE = 3
COLORKEY = (0, 0, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)

NEIGHBOURS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

pygame.init()
root = tk.Tk()
root.withdraw()

screen = pygame.display.set_mode((500, 500))
display = pygame.Surface((300, 300))
clock = pygame.time.Clock()

img_file = None
selected_crops = []

mpos = None
clicked = False
tile_offset = False

img_file_path = filedialog.askopenfilename(title='Choose a sketch image', filetypes=[('Image Files', '*.png;*.jpg;*.jpeg;*.gif')], defaultextension='.png', initialdir=os.getcwd())

if not img_file_path:
    pygame.quit()
    sys.exit()
    
img_file = pygame.image.load(img_file_path).convert()

img_dimensions = (img_file.get_width() * RENDER_SCALE, img_file.get_height() * RENDER_SCALE)

screen = pygame.display.set_mode(img_dimensions, pygame.SCALED + pygame.RESIZABLE)
display = img_file.copy()

def clip(surf, loc, size):
    main_surf = surf.copy()
    clipped_rect = pygame.Rect(loc[0], loc[1], size[0], size[1])
    main_surf.set_clip(clipped_rect)
    img = main_surf.subsurface(main_surf.get_clip())
    return img.copy()

def floodfill(start_pos):
    queue = [start_pos]
    visited = set()
    min_pos = start_pos
    max_pos = start_pos
    
    while queue:
        
        curr_point = queue.pop()
        
        if curr_point in visited:
            continue
        
        if img_file.get_at(curr_point)[:3] == COLORKEY:
            continue
        
        
        visited.add(curr_point)
        
        min_pos = (min(min_pos[0], curr_point[0]), min(min_pos[1], curr_point[1]))
        max_pos = (max(max_pos[0], curr_point[0]), max(max_pos[1], curr_point[1]))
        
        for dx, dy in NEIGHBOURS:
            queue.append((curr_point[0] + dx, curr_point[1] + dy))
    
    return min_pos, max_pos


def create_spritesheet(tile_config):
    spritesheet_width = 0
    spritesheet_height = 0
    spritesheet_list = []
    for min_pos, max_pos in selected_crops:
        size = (max_pos[0] - min_pos[0] + 1, max_pos[1] - min_pos[1] + 2)
        img = clip(img_file, (min_pos[0], min_pos[1]), size)
        spritesheet_width = max(spritesheet_width, size[0] + 2)
        spritesheet_height += size[1] + 1
        spritesheet_list.append(img)
        
    spritesheet_surf = pygame.Surface((spritesheet_width, spritesheet_height))
    
    y_pos = 1
    for i, img in enumerate(spritesheet_list):
        spritesheet_surf.blit(img, (1, y_pos))
        pygame.draw.rect(spritesheet_surf, CYAN if tile_config else MAGENTA, pygame.Rect(0, y_pos - 1, img.get_width() + 2, img.get_height() + 1), 1)   
        y_pos += img.get_height() + 1

    export_path = filedialog.asksaveasfilename(title='Save the spritesheet', filetypes=[('Image Files', '*.png;*.jpg;*.jpeg;*.gif')], defaultextension='.png')
    if export_path:
        pygame.image.save(spritesheet_surf, export_path)
        print(f"Spritesheet saved as {export_path.split('/')[-1]}")
        

while True:
    
    display.fill((0, 0, 0))
    display.blit(img_file, (0, 0))
    
    mpos = pygame.mouse.get_pos()
    mpos = (mpos[0] // RENDER_SCALE, mpos[1] // RENDER_SCALE)
    
    if clicked:
        min_pos, max_pos = floodfill(mpos)
        points = [min_pos, max_pos]
        if points not in selected_crops:
            selected_crops.append([min_pos, max_pos])
        
    for min_pos, max_pos in selected_crops:
        size = (max_pos[0] - min_pos[0], max_pos[1] - min_pos[1])
        img_crop_rect = pygame.Rect(min_pos[0] - 1, min_pos[1] - 1, size[0] + 3, size[1] + 3)
        c = CYAN if tile_offset else MAGENTA
        pygame.draw.rect(display, c,  img_crop_rect, 1)
     
    clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_s:
                # add save
                create_spritesheet(tile_config=tile_offset)
                selected_crops = []
            if event.key == pygame.K_r:
                selected_crops = []
            if event.key == pygame.K_t:
                tile_offset = not tile_offset
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if img_file.get_at(mpos)[:3] != COLORKEY:
                    clicked = True
            if event.button == 3:
                selected_crops.pop()
        
        
            
            
    pygame.display.flip()
    screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
    clock.tick(60)