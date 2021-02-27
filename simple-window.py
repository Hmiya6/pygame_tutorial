import pygame, sys

clock = pygame.time.Clock()

# pylint: disable=unused-wildcard-import
from pygame.locals import *

# pylint: disable=no-name-in-module
from pygame.constants import (
    QUIT, KEYDOWN, K_a, K_d, KEYUP
)
from pygame import display, event, key, time

# pylint: disable=no-member
pygame.init() # initiates pygame

# window configurations
WINDOW_SIZE = (600, 400)
pygame.display.set_caption('2D Action Game v0.0.1')
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
# render on `display` and scale up
DISPLAY_SIZE = (WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2)
display = pygame.Surface(DISPLAY_SIZE)
true_scroll = [0.0, 0.0]
scroll = [0, 0]

# player
global animation_frames
animation_frames = {}
def load_animation(path, frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((0, 0, 0))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame

animation_database = {}
animation_database['run'] = load_animation('assets/player_animations/run', [8, 8, 8])
animation_database['idle'] = load_animation('assets/player_animations/idle', [16, 40])

player_action = 'idle'
player_frame = 0
player_flip = False

# player_image = pygame.image.load('assets/player.png')
# player_image.set_colorkey((255, 255, 255))
player_location = [50, 50]
player_y_momentum = 0.0
air_timer = 0.0
jump_counter = 2
moving_right = False
moving_left = False
player_rect = pygame.Rect(
    50, 50, animation_frames[animation_database['idle'][0]].get_width(), animation_frames[animation_database['idle'][0]].get_height()
)

# test_rect = pygame.Rect(100, 100, 200, 200)


# terrian
def load_map(path):
    with open(path, 'r') as f:
        data = f.read()
        f.close()
        data = data.split('\n')
        game_map = []
        for row in data:
            game_map.append(list(row))
    return game_map

game_map = load_map('map.txt')
stone_block = pygame.image.load('assets/rock.png').convert()
grass_block = pygame.image.load('assets/grass_rock.png').convert()
grass = pygame.image.load('assets/grass.png').convert()
grass.set_colorkey((0, 0, 0))
TILE_SIZE = stone_block.get_width()

# background
ruins = pygame.image.load('assets/ruins.png').convert()
ruins.set_colorkey((0, 0, 0))
RUINS_SIZE = ruins.get_width() # == ruins.get_height()
ruins = pygame.transform.scale(ruins, (RUINS_SIZE*4, RUINS_SIZE*4))
RUINS_SIZE = ruins.get_width() # == ruins.get_height()
background_objects = [[0.25, [0, 10]],
                     # [0.25, [280, 10]],
                     # [0.25, [280, 10]],
                     # [0.25, [280, 10]]
                    ]
# collision
def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types



while True:
    # display.fill((255, 255, 255))
    # display.fill((120, 240, 240))
    display.fill((90, 40, 90))

    true_scroll[0] += (player_rect.x - scroll[0] - DISPLAY_SIZE[0]/2)/10 
    true_scroll[1] += (player_rect.y - scroll[1] - DISPLAY_SIZE[1]/2)/10
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
    
    # map rendering
    for background_object in background_objects:
        display.blit(ruins, ((background_object[1][0] - scroll[0])*background_object[0], (background_object[1][1] - scroll[1])*background_object[0]))

    tile_rects = []
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '1':
                display.blit(stone_block, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
            if tile == '2':
                display.blit(grass_block, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
            if tile == '3':
                display.blit(grass, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
            if tile != '0' and tile != '3':
                tile_rects.append(pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1
        y += 1

    
    # display.blit(player_image, player_location)
    
    """
    if player_location[1] > WINDOW_SIZE[1]-player_image.get_height():
        player_y_momentum = -player_y_momentum
    else:
        player_y_momentum += 0.2
    player_location[1] += player_y_momentum
    """


    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2 # type: ignore
    player_movement[1] += player_y_momentum # type: ignore
    player_y_momentum += 0.2
    if player_y_momentum > 3:
        player_y_momentum = 3
    
    
    

    
    player_rect, collisions = move(player_rect, player_movement, tile_rects)
    # player_rect.x -= scroll[0]
    # player_rect.y -= scroll[1]
    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_image = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_image, player_flip, False), (player_rect.x-scroll[0], player_rect.y-scroll[1]))

    """
    # pyright error
    if moving_right == True:
        player_location[0] += 4 # type: ignore
    if moving_left == True:
        player_location[0] -= 4 # type: ignore
    """
    """
    player_rect.update(player_location[0], player_location[1], player_rect.w, player_rect.h) # type: ignore
    # player_rect.x = player_location[0]
    # player_rect.y = player_location[1]
    """
    """
    if player_rect.colliderect(test_rect):
        pygame.draw.rect(screen, (255, 0, 0), test_rect)
    else:
        pygame.draw.rect(screen, (0, 0, 0), test_rect)
    """


    if player_movement[0] > 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        player_flip = False
    if player_movement[0] == 0:
        player_action, player_frame = change_action(player_action, player_frame, 'idle')
    if player_movement[0] < 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        player_flip = True
    if air_timer > 8:
        player_action, player_frame = change_action(player_action, player_frame, 'idle')


    if collisions['bottom']:
        player_y_momentum = 0
        air_timer = 0.0
        jump_counter = 2
    else:
        air_timer += 1
    if collisions['top']:
        player_y_momentum = 0

    for event in pygame.event.get():
        if event.type == QUIT:
            # print('I don\'t want to close')
            pygame.quit()
            sys.exit()
        
        if event.type == KEYDOWN:
            if event.key == K_a:
                moving_left = True
            if event.key == K_d:
                moving_right = True
            if event.key == K_SPACE or event.key == K_w:
                if air_timer < 8 or jump_counter > 0:
                    player_y_momentum = -5
                    jump_counter -= 1
        if event.type == KEYUP:
            if event.key == K_a:
                moving_left = False
            if event.key == K_d:
                moving_right = False

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()
    clock.tick(60) # FPS

    

