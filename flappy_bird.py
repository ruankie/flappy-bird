# inspired by youtube tutorial: https://www.youtube.com/watch?v=UZg49z76cLw
# assets, sound, and font from: https://github.com/clear-code-projects/FlappyBird_Python


######################
### import modules ###
######################
import pygame
import sys
import random


#################
### constants ###
#################
SCR_WIDTH = 576
SCR_HEIGHT = 1024
TEXT_SIZE = 40
MAX_FPS = 120
FLY_SPEED = 4
GRAVITY = 0.25
FLOOR_HEIGHT = 900
BG_COLOUR = 'day' # 'day' or 'night'
BIRD_COLOUR = 'yellow' # 'yellow' or 'blue' or 'red'
PIPE_COLOUR = 'green' # 'green' or 'red'
BIRD_X_POS = 100
SCORE_Y_POS = 100
HIGH_SCORE_Y_POS = FLOOR_HEIGHT - 50
FLAP_SPEED = 8 # speed that bird moves upwards with after flap
PIPE_SPAWN_TIME = 1400 # time between spawning pipes (milliseconds)
FLAP_CYCLE_TIME = 200 # time between cycling bird surfaces (milliseconds)
PIPE_HEIGHTS = [400,600,800] # possible pipe heights
PIPE_GAPS = [250,300,350] # possible pipe gaps
SOUND = True # sound on or off
GAME_ACTIVE = False # used for setting game mode


########################
### helper functions ###
########################
def draw_floor(floor_x_pos):
    '''
    draw two floors side by side that extends past screen edge for scrolling left
    '''
    screen.blit(floor_surface, (floor_x_pos, FLOOR_HEIGHT))
    screen.blit(floor_surface, (floor_x_pos+SCR_WIDTH, FLOOR_HEIGHT))
 
 
def create_pipe_set():
    '''
    creates a new pipe set - one on the bottom and one on top
    the pipe height and gap will be radomly sampled from PIPE_HEIGHTSand PIPE_GAPS
    returns the rect of the new pipes
    '''
    lower_pipe_height = random.choice(PIPE_HEIGHTS)
    pipe_gap = random.choice(PIPE_GAPS)
    lower_pipe = pipe_surface.get_rect(midtop=(700,lower_pipe_height))
    upper_pipe = pipe_surface.get_rect(midbottom=(700,lower_pipe_height-pipe_gap))
    return lower_pipe, upper_pipe


def move_pipes(pipes):
    '''
    moves all the rects in the given list of pipes to the left by FLY_SPEED
    then returns moved pipes (rects)
    '''
    for pipe in pipes:
        pipe.centerx -= FLY_SPEED
    return pipes


def draw_pipes(pipes):
    '''
    cycles throug given list of pipes and draws them on screen
    pipes that extend off the bottom will be drawn upright
    pipes that extend above the top of the screen, will be flipped then drawn
    '''
    for pipe in pipes:
        if pipe.bottom >= SCR_HEIGHT:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)


def check_collisions(pipes, bird_rect, death_sound):
    '''
    check for pipe and edge collisions
    return False if collicions are present
    '''
    # pipe collisions
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            if SOUND:
                death_sound.play()
            return False
    # edge collisions (top and floor)
    if (bird_rect.top <= 0) or (bird_rect.bottom >= FLOOR_HEIGHT):
        if SOUND:
            death_sound.play()
        return False
    return True


def reset_bird_and_pipes(pipes, bird_rect):
    '''
    clear the pipes list and reset the bird position
    used at start of new game
    '''
    pipes.clear()
    bird_rect.center = (BIRD_X_POS, SCR_HEIGHT/2)


def rotate_bird(bird_surface):
    '''
    return rotated bird surface - rotation will be proportional to y speed (bird_y_movement)
    '''
    return pygame.transform.rotozoom(bird_surface, -3*bird_y_movement, 1)


def bird_animation():
    '''
    gets correct frame from bird surfaces and draws new rect around it
    then returns updated frame and rect
    '''
    new_bird = bird_surface_frames[bird_frame_idx]
    new_bird_rect = new_bird.get_rect(center=(BIRD_X_POS,bird_rect.centery))
    return new_bird, new_bird_rect


def score_display(game_active):
    '''
    display score and high score depending on game state
    '''
    if game_active:
        score_surface = game_font.render(str(int(score)), True, (255,255,255))
        score_rect = score_surface.get_rect(center=(SCR_WIDTH/2,SCORE_Y_POS))
        screen.blit(score_surface, score_rect)
    else:
        score_surface = game_font.render(f'Score: {int(score)}', True, (255,255,255))
        score_rect = score_surface.get_rect(center=(SCR_WIDTH/2,SCORE_Y_POS))
        screen.blit(score_surface, score_rect)
        high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255,255,255))
        high_score_rect = high_score_surface.get_rect(center=(SCR_WIDTH/2,HIGH_SCORE_Y_POS))
        screen.blit(high_score_surface, high_score_rect)


#############
### setup ###
#############
pygame.init()
screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
clock = pygame.time.Clock()
floor_x_pos = 0
bird_y_movement = 0
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, PIPE_SPAWN_TIME)
BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, FLAP_CYCLE_TIME)
score = 0
high_score = 0


#############################
### assets, sounds, fonts ###
#############################
# background
bg_surface = pygame.transform.scale2x(pygame.image.load(f'assets/background-{BG_COLOUR}.png').convert())

# floor
floor_surface = pygame.transform.scale2x(pygame.image.load('assets/base.png').convert())

# pipes
pipe_surface = pygame.transform.scale2x(pygame.image.load(f'assets/pipe-{PIPE_COLOUR}.png').convert())
pipe_rect_list = []

# bird
bird_surface_down = pygame.transform.scale2x(pygame.image.load(f'assets/{BIRD_COLOUR}bird-downflap.png').convert_alpha())
bird_surface_mid = pygame.transform.scale2x(pygame.image.load(f'assets/{BIRD_COLOUR}bird-midflap.png').convert_alpha())
bird_surface_up = pygame.transform.scale2x(pygame.image.load(f'assets/{BIRD_COLOUR}bird-upflap.png').convert_alpha())
bird_surface_frames = [bird_surface_down, bird_surface_mid, bird_surface_up]
bird_frame_idx = 0
bird_surface = bird_surface_frames[bird_frame_idx]
bird_rect = bird_surface.get_rect(center=(BIRD_X_POS,SCR_HEIGHT/2))

# font
game_font = pygame.font.Font('04B_19.TTF', TEXT_SIZE)

# game over
game_over_surface = pygame.transform.scale2x(pygame.image.load(f'assets/message.png').convert_alpha())
game_over_rect = game_over_surface.get_rect(center=(SCR_WIDTH/2,SCR_HEIGHT/2))

# sounds
flap_soud = pygame.mixer.Sound('sound/sfx_wing.wav')
death_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
score_sound = pygame.mixer.Sound('sound/sfx_point.wav')


#################
### game loop ###
#################
while True:
    # check events
    for event in pygame.event.get():
        # to quit game
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # check if spacebar is pressed
        if event.type == pygame.KEYDOWN:
            # space to flap if game is active
            if event.key == pygame.K_SPACE and GAME_ACTIVE:
                bird_y_movement = 0
                bird_y_movement -= FLAP_SPEED
                if SOUND:
                    flap_soud.play()
            # space to start game if game is inactive
            if event.key == pygame.K_SPACE and not GAME_ACTIVE:
                reset_bird_and_pipes(pipe_rect_list, bird_rect)
                bird_y_movement = 0
                bird_y_movement -= FLAP_SPEED
                GAME_ACTIVE = True
                score = 0

        # spawn next pipe
        if (event.type == SPAWNPIPE) and GAME_ACTIVE:
            pipe_rect_list.extend(create_pipe_set())
            score += 1
            if SOUND:
                score_sound.play()

        # flap bird wings
        if event.type == BIRDFLAP:
            if bird_frame_idx < 2:
                bird_frame_idx += 1
            else:
                bird_frame_idx = 0
            bird_surface, bird_rect = bird_animation()

    # background
    screen.blit(bg_surface, (0,0))

    if GAME_ACTIVE:
        # bird
        bird_y_movement += GRAVITY
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_y_movement
        screen.blit(rotated_bird, bird_rect)

        # pipes
        pipe_rect_list = move_pipes(pipe_rect_list)
        draw_pipes(pipe_rect_list)

        # move floor
        floor_x_pos -= FLY_SPEED
        draw_floor(floor_x_pos)

        # check collisions
        GAME_ACTIVE = check_collisions(pipe_rect_list, bird_rect, death_sound)

    else:
        # display game over screen
        screen.blit(game_over_surface, game_over_rect)

    # draw floor
    draw_floor(floor_x_pos)
    if floor_x_pos <= -SCR_WIDTH:
        floor_x_pos = 0        

    # display score(s)
    high_score = max(score, high_score)
    score_display(GAME_ACTIVE)

    # update display
    pygame.display.update()
    clock.tick(MAX_FPS)