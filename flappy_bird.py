import sys
import random
import pygame
from pygame.locals import *
from itertools import cycle

# Constant
CAPTION = 'Flappy Bird'
FPS = 30
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
PIPE_GAP = 100  # Gap between upper and lower part of pipe
BASE_WIDTH = SCREEN_HEIGHT * 0.79

LIST_BACKGROUND = ('assets/img/bg_day.png', 'assets/img/bg_night.png')
LIST_PIPE = ('assets/img/ic_pipe_green.png', 'assets/img/ic_pipe_red.png')
LIST_BIRD = (
    (
        'assets/img/ic_red_bird_up_flap.png',
        'assets/img/ic_red_bird_mid_flap.png',
        'assets/img/ic_red_bird_down_flap.png',
    ),
    (
        'assets/img/ic_blue_bird_up_flap.png',
        'assets/img/ic_blue_bird_mid_flap.png',
        'assets/img/ic_blue_bird-down_flap.png',
    ),
    (
        'assets/img/ic_yellow_bird_up_flap.png',
        'assets/img/ic_yellow_bird_mid_flap.png',
        'assets/img/ic_yellow_bird_down_flap.png',
    ),
)

# Variable
pipe_color, bird_color = 0, 0
images, sounds, hit_mask = {}, {}, {}


def start_game():
    # Initialize game
    init_game()

    while True:
        # Start game
        movement_info = show_welcome_screen()
        collide_info = game_configuration(movement_info)
        show_game_over_screen(collide_info)


def init_game():
    global CAPTION, screen, fps_clock

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Initialize a window or screen for display
    fps_clock = pygame.time.Clock()  # Create an object to help track time
    pygame.display.set_caption(CAPTION)  # Get the current window caption

    # Initialize images source, Change the pixel format of an image including per pixel alphas
    images['background'] = pygame.image.load(LIST_BACKGROUND[0]).convert()
    images['base'] = pygame.image.load('assets/img/bg_base.png').convert_alpha()
    images['title'] = pygame.image.load('assets/img/ic_title.png').convert_alpha()
    images['numbers'] = (
        pygame.image.load('assets/img/ic_0.png').convert_alpha(),
        pygame.image.load('assets/img/ic_1.png').convert_alpha(),
        pygame.image.load('assets/img/ic_2.png').convert_alpha(),
        pygame.image.load('assets/img/ic_3.png').convert_alpha(),
        pygame.image.load('assets/img/ic_4.png').convert_alpha(),
        pygame.image.load('assets/img/ic_5.png').convert_alpha(),
        pygame.image.load('assets/img/ic_6.png').convert_alpha(),
        pygame.image.load('assets/img/ic_7.png').convert_alpha(),
        pygame.image.load('assets/img/ic_8.png').convert_alpha(),
        pygame.image.load('assets/img/ic_9.png').convert_alpha()
    )
    images['bird'] = (
        pygame.image.load(LIST_BIRD[0][0]).convert_alpha(),
        pygame.image.load(LIST_BIRD[0][1]).convert_alpha(),
        pygame.image.load(LIST_BIRD[0][2]).convert_alpha()
    )
    images['bird_blue'] = (
        pygame.image.load(LIST_BIRD[1][0]).convert_alpha(),
        pygame.image.load(LIST_BIRD[1][1]).convert_alpha(),
        pygame.image.load(LIST_BIRD[1][2]).convert_alpha()
    )
    images['bird_yellow'] = (
        pygame.image.load(LIST_BIRD[2][0]).convert_alpha(),
        pygame.image.load(LIST_BIRD[2][1]).convert_alpha(),
        pygame.image.load(LIST_BIRD[2][2]).convert_alpha()
    )
    images['pipe'] = (
        pygame.transform.flip(pygame.image.load(LIST_PIPE[0]).convert_alpha(), False, True),
        pygame.image.load(LIST_PIPE[0]).convert_alpha()
    )
    images['pipe_red'] = (
        pygame.transform.flip(pygame.image.load(LIST_PIPE[1]).convert_alpha(), False, True),
        pygame.image.load(LIST_PIPE[1]).convert_alpha()
    )
    images['game_over'] = pygame.image.load('assets/img/ic_game_over.png').convert_alpha()

    # Initialize hit mask
    hit_mask['pipe'] = (
        get_hit_mask(images['pipe'][0]),
        get_hit_mask(images['pipe'][1]),
    )
    hit_mask['bird'] = (
        get_hit_mask(images['bird'][0]),
        get_hit_mask(images['bird'][1]),
        get_hit_mask(images['bird'][2]),
    )

    # Initialize sounds source, Create a new Sound object from a file or buffer object
    if 'win' in sys.platform:  # According to OS choosing filename extension
        sound_extension = '.wav'
    else:
        sound_extension = '.ogg'
    sounds['die'] = pygame.mixer.Sound('assets/audio/die' + sound_extension)
    sounds['hit'] = pygame.mixer.Sound('assets/audio/hit' + sound_extension)
    sounds['point'] = pygame.mixer.Sound('assets/audio/point' + sound_extension)
    sounds['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + sound_extension)
    sounds['wing'] = pygame.mixer.Sound('assets/audio/wing' + sound_extension)


# Returns a hit mask using an image's alpha
def get_hit_mask(image):
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))

    return mask


def show_welcome_screen():
    # Variable
    bird_index = 0  # Index of bird for blit(draw to cover the entire window) on screen
    bird_index_generator = cycle([0, 1, 2, 1])
    loop_iter = 0  # Iterator used to change bird_index after every 5th iteration
    base_x = 0
    bird_x = int(SCREEN_WIDTH * 0.2)
    bird_y = int((SCREEN_HEIGHT - images['bird'][0].get_height()) / 2)
    title_x = int((SCREEN_WIDTH - images['title'].get_width()) / 2)
    title_y = int(SCREEN_HEIGHT * 0.12)
    base_offset = images['base'].get_width() - images['background'].get_width()
    bird_s_h_m = {'val': 0, 'dir': 1}  # Bird SHM(Simple Harmonic Motion) for up-down motion on welcome screen

    while True:
        for event in pygame.event.get():
            # Quit game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # Make first flap sound and return values for game
                sounds['wing'].play()

                return {
                    'base_x': base_x,
                    'bird_y': bird_y + bird_s_h_m['val'],
                    'bird_index_generator': bird_index_generator,
                }

        # Adjust base_x, bird_y, bird_index
        if (loop_iter + 1) % 5 == 0:
            bird_index = next(bird_index_generator)

        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 4) % base_offset)
        s_h_m_configuration(bird_s_h_m)

        # Draw to cover the entire window
        screen.blit(images['background'], (0, 0))
        screen.blit(images['bird'][bird_index],
                    (bird_x, bird_y + bird_s_h_m['val']))
        screen.blit(images['title'], (title_x, title_y))
        screen.blit(images['base'], (base_x, BASE_WIDTH))

        fps_clock.tick(FPS)  # Update the clock
        pygame.display.update()  # Update portions of the screen for software displays


# Oscillates the value of bird_s_h_m['val'] between 8 and -8
def s_h_m_configuration(bird_s_h_m):
    if abs(bird_s_h_m['val']) == 8:
        bird_s_h_m['dir'] *= -1

    if bird_s_h_m['dir'] == 1:
        bird_s_h_m['val'] += 1
    else:
        bird_s_h_m['val'] -= 1


def game_configuration(movement_info):
    global pipe_color, bird_color

    # Variable
    score = bird_index = loop_iter = 0
    bird_index_generator = movement_info['bird_index_generator']
    bird_x, bird_y = int(SCREEN_WIDTH * 0.2), movement_info['bird_y']
    base_x = movement_info['base_x']
    base_shift = images['base'].get_width() - images['background'].get_width()

    pipe_velocity_x = -4  # Pipe's velocity along x
    bird_velocity_y = -9  # Bird's velocity along Y
    bird_max_velocity_y = 10  # Bird's max velocity along Y
    bird_acceleration_y = 1  # Downward acceleration
    bird_rotation = 45
    bird_rotate_velocity = 3
    bird_rotation_threshold = 20
    bird_flap_acceleration = -9  # Bird's flapping speed
    is_bird_flapped = False

    # Get 2 new pipes adding to upper_pipes lower_pipes list
    pipe_one = get_random_pipe()
    pipe_two = get_random_pipe()
    upper_pipes = [
        {'x': SCREEN_WIDTH + 200, 'y': pipe_one[0]['y']},
        {'x': SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': pipe_two[0]['y']},
    ]
    lower_pipes = [
        {'x': SCREEN_WIDTH + 200, 'y': pipe_one[1]['y']},
        {'x': SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': pipe_two[1]['y']},
    ]

    while True:
        for event in pygame.event.get():
            # Quit game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if bird_y > -2 * images['bird'][0].get_height():
                    bird_velocity_y = bird_flap_acceleration
                    is_bird_flapped = True
                    sounds['wing'].play()

        # Check is collided
        is_collided = check_collide({'x': bird_x, 'y': bird_y, 'index': bird_index}, upper_pipes, lower_pipes)
        if is_collided[0]:
            return {
                'y': bird_y,
                'is_collided': is_collided[1],
                'base_x': base_x,
                'upper_pipes': upper_pipes,
                'lower_pipes': lower_pipes,
                'score': score,
                'bird_velocity_y': bird_velocity_y,
                'bird_rotation': bird_rotation
            }

        # Check score
        bird_mid_position = bird_x + images['bird'][0].get_width() / 2
        for pipe in upper_pipes:
            pipe_mid_position = pipe['x'] + images['pipe'][0].get_width() / 2
            if pipe_mid_position <= bird_mid_position < pipe_mid_position + 4:
                score += 1
                sounds['point'].play()

        # Update bird_index base_x
        if (loop_iter + 1) % 3 == 0:
            bird_index = next(bird_index_generator)
        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 100) % base_shift)

        # Rotate the bird
        if bird_rotation > -90:
            bird_rotation -= bird_rotate_velocity

        # Bird's movement
        if bird_velocity_y < bird_max_velocity_y and not is_bird_flapped:
            bird_velocity_y += bird_acceleration_y
        if is_bird_flapped:
            is_bird_flapped = False
            bird_rotation = 45  # More rotation to cover the threshold (calculated in visible rotation)
        bird_y += min(bird_velocity_y, BASE_WIDTH - bird_y - images['bird'][bird_index].get_height())

        # Pipe's movement
        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            upper_pipe['x'] += pipe_velocity_x
            lower_pipe['x'] += pipe_velocity_x

        # Add new pipe when front pipe is appearing in left of screen
        if len(upper_pipes) > 0 and 0 < upper_pipes[0]['x'] < 5:
            new_pipe = get_random_pipe()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        # Remove front pipe when it is out of the screen
        if len(upper_pipes) > 0 and upper_pipes[0]['x'] < -images['pipe'][0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        # Draw to cover the entire window
        screen.blit(images['background'], (0, 0))

        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            if score >= 5:
                pipe_color = 1
                screen.blit(images['pipe_red'][0], (upper_pipe['x'], upper_pipe['y']))
                screen.blit(images['pipe_red'][1], (lower_pipe['x'], lower_pipe['y']))
            else:
                pipe_color = 0
                screen.blit(images['pipe'][0], (upper_pipe['x'], upper_pipe['y']))
                screen.blit(images['pipe'][1], (lower_pipe['x'], lower_pipe['y']))

        screen.blit(images['base'], (base_x, BASE_WIDTH))

        # Print score
        show_score(score)

        # Bird rotation has a threshold
        rotation_visibility = bird_rotation_threshold
        if bird_rotation <= bird_rotation_threshold:
            rotation_visibility = bird_rotation

        if 3 <= score < 6:
            bird_color = 1
            bird_surface = pygame.transform.rotate(images['bird_blue'][bird_index], rotation_visibility)
        elif score >= 6:
            bird_color = 2
            bird_surface = pygame.transform.rotate(images['bird_yellow'][bird_index], rotation_visibility)
        else:
            bird_color = 0
            bird_surface = pygame.transform.rotate(images['bird'][bird_index], rotation_visibility)
        screen.blit(bird_surface, (bird_x, bird_y))

        fps_clock.tick(FPS)
        pygame.display.update()


# Returns a random size of pipe
def get_random_pipe():
    # gap between upper and lower pipe
    gap_y = random.randrange(0, int(BASE_WIDTH * 0.6 - PIPE_GAP)) + int(BASE_WIDTH * 0.2)
    pipe_height = images['pipe'][0].get_height()
    pipe_x = SCREEN_WIDTH + 10

    return [
        {'x': pipe_x, 'y': gap_y - pipe_height},  # upper pipe
        {'x': pipe_x, 'y': gap_y + PIPE_GAP},  # lower pipe
    ]


# Returns True if bird collide with base or pipes.
def check_collide(bird, upper_pipes, lower_pipes):
    bird_index = bird['index']
    bird['w'] = images['bird'][0].get_width()
    bird['h'] = images['bird'][0].get_height()

    # If bird collide with base
    if bird['y'] + bird['h'] >= BASE_WIDTH - 1:
        return [True, True]
    else:
        bird_rect = pygame.Rect(bird['x'], bird['y'], bird['w'], bird['h'])
        pipe_width = images['pipe'][0].get_width()
        pipe_height = images['pipe'][0].get_height()

        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            # Upper and lower pipe rects
            upper_pipe_rect = pygame.Rect(upper_pipe['x'], upper_pipe['y'], pipe_width, pipe_height)
            lower_pipe_rect = pygame.Rect(lower_pipe['x'], lower_pipe['y'], pipe_width, pipe_height)

            # Set bird and upper & lower pipe hit mask
            bird_hit_mask = hit_mask['bird'][bird_index]
            upper_pipe_hit_mask = hit_mask['pipe'][0]
            lower_pipe_hit_mask = hit_mask['pipe'][1]

            # if bird collided with upper_pipe or lower_pipe
            upper_collide = pixel_collision(bird_rect, upper_pipe_rect, bird_hit_mask, upper_pipe_hit_mask)
            lower_collide = pixel_collision(bird_rect, lower_pipe_rect, bird_hit_mask, lower_pipe_hit_mask)

            if upper_collide or lower_collide:
                return [True, False]
    return [False, False]


# Checks if two objects collide not just their rects
def pixel_collision(bird_rect, pipe_rect, bird_hit_mask, pipe_hit_mask):
    rect = bird_rect.clip(pipe_rect)  # Crops a rectangle inside another

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - bird_rect.x, rect.y - bird_rect.y
    x2, y2 = rect.x - pipe_rect.x, rect.y - pipe_rect.y

    for x in range(rect.width):
        for y in range(rect.height):
            if bird_hit_mask[x1 + x][y1 + y] and pipe_hit_mask[x2 + x][y2 + y]:
                return True
    return False


# Display score in center of screen
def show_score(score):
    scores = [int(x) for x in list(str(score))]
    total_width = 0

    offset = (SCREEN_WIDTH - total_width) / 2

    for score in scores:
        total_width += images['numbers'][score].get_width()
        screen.blit(images['numbers'][score], (offset, SCREEN_HEIGHT * 0.1))
        offset += images['numbers'][score].get_width()


# Bird collide and showing game over image
def show_game_over_screen(collide_info):
    # Variable
    score = collide_info['score']
    base_x = collide_info['base_x']
    bird_x = SCREEN_WIDTH * 0.2
    bird_y = collide_info['y']
    bird_height = images['bird'][0].get_height()
    bird_velocity_y = collide_info['bird_velocity_y']
    bird_acceleration_y = 2
    bird_rotation = collide_info['bird_rotation']
    bird_rotate_velocity = 7
    upper_pipes = collide_info['upper_pipes']
    lower_pipes = collide_info['lower_pipes']

    # Play hit and die sounds
    sounds['hit'].play()
    if not collide_info['is_collided']:
        sounds['die'].play()

    while True:
        for event in pygame.event.get():
            # Quit game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if bird_y + bird_height >= BASE_WIDTH - 1:
                    return

        # Bird y offset
        if bird_y + bird_height < BASE_WIDTH - 1:
            bird_y += min(bird_velocity_y, BASE_WIDTH - bird_y - bird_height)

        # Update bird velocity
        if bird_velocity_y < 15:
            bird_velocity_y += bird_acceleration_y

        # Rotate only when colliding with pipe
        if not collide_info['is_collided']:
            if bird_rotation > -90:
                bird_rotation -= bird_rotate_velocity

        # Draw to cover the entire window
        screen.blit(images['background'], (0, 0))

        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            if pipe_color == 1:
                screen.blit(images['pipe_red'][0], (upper_pipe['x'], upper_pipe['y']))
                screen.blit(images['pipe_red'][1], (lower_pipe['x'], lower_pipe['y']))
            else:
                screen.blit(images['pipe'][0], (upper_pipe['x'], upper_pipe['y']))
                screen.blit(images['pipe'][1], (lower_pipe['x'], lower_pipe['y']))

        screen.blit(images['base'], (base_x, BASE_WIDTH))
        show_score(score)

        if bird_color == 1:
            bird_surface = pygame.transform.rotate(images['bird_blue'][1], bird_rotation)
            screen.blit(bird_surface, (bird_x, bird_y))
        elif bird_color == 2:
            bird_surface = pygame.transform.rotate(images['bird_yellow'][1], bird_rotation)
            screen.blit(bird_surface, (bird_x, bird_y))
        else:
            bird_surface = pygame.transform.rotate(images['bird'][1], bird_rotation)
            screen.blit(bird_surface, (bird_x, bird_y))

        screen.blit(images['game_over'], (50, 180))

        fps_clock.tick(FPS)
        pygame.display.update()


if __name__ == '__main__':
    start_game()
