# Import libaries
import pygame as pg
import sys
import time
from pygame.locals import *
from pyfirmata import Arduino, util, INPUT, OUTPUT, PWM
import tictactoe as ttt

# Constants
ARDUINO_PORT = 'COM6'
LED_PINS = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10}
NAV_BUTTON_PIN = 11
SELECT_BUTTON_PIN = 12
CHANCES_TO_PLAY = 3

# variables
last_nav_button_state = False
last_select_button_state = False

try:
    # Connect to the Arduino board
    board = Arduino(ARDUINO_PORT)

    # Start an iterator thread so that serial buffer doesn't overflow
    it = util.Iterator(board)
    it.start()
except Exception as e:
    print('Error while connecting to the Arduino board: {}'.format(e))
    exit(1)

try:
    # Create a list of LED objects
    leds = [ttt.Led(pin, board) for pin in LED_PINS.values()]
except Exception as e:
    print('Error while creating the LED objects: {}'.format(e))
    exit(1)

try:
    # Create the Game object
    game = ttt.Game(leds, CHANCES_TO_PLAY)
except Exception as e:
    print('Error while creating the Game object: {}'.format(e))
    exit(1)

# Set navigate button pin mode to INPUT_PULLUP
NAV_BUTTON = board.get_pin('d:{}:i'.format(NAV_BUTTON_PIN))
SELECT_BUTTON = board.get_pin('d:{}:i'.format(SELECT_BUTTON_PIN))

# Enable reporting for the buttons
NAV_BUTTON.enable_reporting()
SELECT_BUTTON.enable_reporting()


# Define constants for the screen width and height
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Set framerate
FPS = 30

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Define coordinates for the board
BOARD_COORDINATES = [(101, 101), (288, 101), (468, 101), (101, 281),
                     (288, 281), (468, 281), (101, 466), (288, 466), (468, 466)]

# Initialize pygame
pg.init()

# Initialize the font
pg.font.init()

default_font = pg.font.get_default_font()
font_renderer = pg.font.Font(default_font, 30)

# Clock for FPS
fps_clock = pg.time.Clock()

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Set the window title
pg.display.set_caption('Tic Tac Toe')

# Load the images
loading_window = pg.image.load("assets/loading.png")
instruction_window = pg.image.load("assets/instruction.png")
choose_mode_window = pg.image.load("assets/choose_mode.png")
champion_player_o_window = pg.image.load("assets/champion_player_o.png")
champion_player_x_window = pg.image.load("assets/champion_player_x.png")
match_is_draw_window = pg.image.load("assets/match_is_draw.png")
thankyou_window = pg.image.load("assets/thankyou.png")
player_o_won = pg.image.load("assets/player_o_won.png")
player_x_won = pg.image.load("assets/player_x_won.png")
game_is_tie = pg.image.load("assets/game_is_tie.png")
game_board = pg.image.load("assets/game_board.png")
x_img = pg.image.load("assets/x.png")
o_img = pg.image.load("assets/o.png")
life = pg.image.load("assets/life.png")
player_bg = pg.image.load("assets/player_bg.png")
computer_is_thinking = pg.image.load("assets/computer_is_thinking.png")
computer_is_thinking_bg = pg.image.load("assets/computer_is_thinking_bg.png")


# Resize images
loading_window = pg.transform.scale(
    loading_window, (SCREEN_WIDTH, SCREEN_HEIGHT))
instruction_window = pg.transform.scale(
    instruction_window, (SCREEN_WIDTH, SCREEN_HEIGHT))
choose_mode_window = pg.transform.scale(
    choose_mode_window, (SCREEN_WIDTH, SCREEN_HEIGHT))
champion_player_o_window = pg.transform.scale(
    champion_player_o_window, (SCREEN_WIDTH, SCREEN_HEIGHT))
champion_player_x_window = pg.transform.scale(
    champion_player_x_window, (SCREEN_WIDTH, SCREEN_HEIGHT))
match_is_draw_window = pg.transform.scale(
    match_is_draw_window, (SCREEN_WIDTH, SCREEN_HEIGHT))
thankyou_window = pg.transform.scale(
    thankyou_window, (SCREEN_WIDTH, SCREEN_HEIGHT))
game_board = pg.transform.scale(game_board, (SCREEN_WIDTH, SCREEN_HEIGHT))
player_o_won = pg.transform.scale(
    player_o_won, (764, 548))
player_x_won = pg.transform.scale(
    player_x_won, (764, 548))
game_is_tie = pg.transform.scale(
    game_is_tie, (764, 548))
x_img = pg.transform.scale(x_img, (107, 118))
o_img = pg.transform.scale(o_img, (107, 118))
player_x = pg.transform.scale(x_img, (53.5, 59))
player_o = pg.transform.scale(o_img, (53.5, 59))
player_bg = pg.transform.scale(player_bg, (53.5, 59))
life = pg.transform.scale(life, (54, 48))
life_bg = pg.transform.scale(player_bg, (54, 48))
computer_is_thinking = pg.transform.scale(
    computer_is_thinking, (561, 121))
computer_is_thinking_bg = pg.transform.scale(
    computer_is_thinking_bg, (561, 121))


def show_computer_is_thinking():
    screen.blit(computer_is_thinking, (65, 660))
    pg.display.update()


def clear_computer_is_thinking():
    screen.blit(computer_is_thinking_bg, (65, 660))
    pg.display.update()


def show_player_o_won():
    screen.blit(player_o_won, (218, 116))
    pg.display.update()


def show_player_x_won():
    screen.blit(player_x_won, (218, 116))
    pg.display.update()


def show_game_is_tie():
    screen.blit(game_is_tie, (218, 116))
    pg.display.update()


def draw_score(score):

    player_1_score = font_renderer.render(
        str(score[1]), 1, (255, 255, 255))
    player_2_score = font_renderer.render(
        str(score[2]), 1, (255, 255, 255))
    screen.blit(player_1_score, (982, 503))
    screen.blit(player_2_score, (982, 590))
    pg.display.update()


def draw_x(position):
    screen.blit(x_img, position)
    pg.display.update()


def draw_o(position):
    screen.blit(o_img, position)
    pg.display.update()


def update_game_board(leds):
    for i in range(9):
        if leds[i].selected == 1:
            draw_o(BOARD_COORDINATES[i])
        elif leds[i].selected == 2:
            draw_x(BOARD_COORDINATES[i])


def draw_player_x():
    screen.blit(player_bg, (912, 130))
    screen.blit(player_x, (912, 130))
    pg.display.update()


def draw_player_o():
    screen.blit(player_bg, (912, 130))
    screen.blit(player_o, (912, 130))
    pg.display.update()


def draw_life(life_count):
    if life_count == 3:
        screen.blit(life, (894, 220))
        screen.blit(life, (960, 220))
        screen.blit(life, (1026, 220))
    elif life_count == 2:
        screen.blit(life, (894, 220))
        screen.blit(life, (960, 220))
        screen.blit(life_bg, (1026, 220))
    elif life_count == 1:
        screen.blit(life, (894, 220))
        screen.blit(life_bg, (960, 220))
    elif life_count == 0:
        screen.blit(life_bg, (894, 220))

    pg.display.update()


def show_game_board():
    # Displaying over the screen
    screen.blit(game_board, (0, 0))

    # Updating the display
    pg.display.update()


def show_choose_mode_window():
    # Displaying over the screen
    screen.blit(choose_mode_window, (0, 0))

    # Updating the display
    pg.display.update()


def show_loading_window():
    # Displaying over the screen
    screen.blit(loading_window, (0, 0))

    # Updating the display
    pg.display.update()
    time.sleep(3)


def show_instruction_window():
    # Displaying over the screen
    screen.blit(instruction_window, (0, 0))

    # Updating the display
    pg.display.update()


def show_thankyou_window():
    # Displaying over the screen
    screen.blit(thankyou_window, (0, 0))

    # Updating the display
    pg.display.update()


def show_champion_player_o_window():
    # Displaying over the screen
    screen.blit(champion_player_o_window, (0, 0))

    # Updating the display
    pg.display.update()


def show_champion_player_x_window():
    # Displaying over the screen
    screen.blit(champion_player_x_window, (0, 0))

    # Updating the display
    pg.display.update()


def show_match_is_draw_window():
    # Displaying over the screen
    screen.blit(match_is_draw_window, (0, 0))

    # Updating the display
    pg.display.update()


def refresh_game_board(game):
    show_game_board()
    if game.current_player == 1:
        draw_player_o()

    if game.current_player == 2:
        draw_player_x()

    draw_life(game.remaining_chances)

    draw_score(game.score)


def handle_selection(game):
    '''Handles the selection of the navigation button'''
    try:
        game.can_get_input = False
        game.select()
        game.navigation_button_position = 0
        update_game_board(game.leds)

        game.can_get_input = True

        if game.check_for_win():
            game.announce_win()
            if game.current_player == 1:
                show_player_o_won()
            elif game.current_player == 2:
                show_player_x_won()

        elif game.check_for_draw():
            game.announce_draw()
            show_game_is_tie()

        if not game.finished:
            game.switch_players()

            if game.current_player == 1:
                draw_player_o()

            if game.current_player == 2:
                draw_player_x()

            draw_life(game.remaining_chances)

        if game.computer_move:
            show_computer_is_thinking()

        if game.remaining_chances == 0:
            print('\nNo more chances left.')
            game.announce_final_winner()
            if game.score[1] > game.score[2]:
                show_champion_player_o_window()
            elif game.score[1] < game.score[2]:
                show_champion_player_x_window()
            else:
                show_match_is_draw_window()
            game.reset_game()

    except Exception as e:
        print('\n')
        print(e)


def handle_start_again(game):
    game.can_get_input = False
    game.welcome()
    show_loading_window()
    show_choose_mode_window()
    game.can_get_input = True
    game.can_start_again = False


# Start the game
game.welcome()
show_loading_window()
show_instruction_window()
time.sleep(5)
show_choose_mode_window()
game.can_get_input = True
# Main Loop
while True:
    for event in pg.event.get():
        if event.type == QUIT:
            game.handle_exit()
            pg.quit()
            sys.exit()

        # global last_nav_button_state, last_select_button_state, game, NAV_BUTTON, SELECT_BUTTON
    current_time = time.time()
    # Read the buttons' states
    nav_button_state = NAV_BUTTON.read()
    select_button_state = SELECT_BUTTON.read()

    nav_button_pressed = game.can_get_input and nav_button_state and last_nav_button_state != nav_button_state
    select_button_pressed = game.can_get_input and select_button_state and last_select_button_state != select_button_state

    can_start_again = nav_button_pressed and game.can_start_again
    can_select = select_button_pressed and not game.finished and not game.computer_move and game.started
    can_nav = nav_button_pressed and not game.finished and not game.computer_move and game.started
    can_play_next_chance = nav_button_pressed and game.finished and game.started
    can_exit = select_button_pressed and game.finished and game.started
    can_computer_play = game.computer_move and not game.finished and game.computer_vs_human_mode and (
        (current_time - game.computer_move_start_time) > game.computer_move_delay)
    human_vs_human = nav_button_pressed and not game.started
    computer_vs_human = select_button_pressed and not game.started

    if can_start_again:
        handle_start_again(game)

        last_nav_button_state = nav_button_state

    # If the game is not started, then
    if human_vs_human and last_nav_button_state != nav_button_state:
        game.start_game()
        refresh_game_board(game)

    if computer_vs_human:
        game.enable_computer_vs_human_mode()
        game.start_game()
        refresh_game_board(game)

    # If the computer is playing, then
    if can_computer_play:

        game.do_computer_move()
        handle_selection(game)
        clear_computer_is_thinking()

    # If the navigation button state and select button state have changed at same time, then
    if nav_button_pressed and select_button_pressed:
        print('\nPlease use one button at a time.')

    # If the navigation button state has changed and the game is finished, then
    if can_play_next_chance:
        game.handle_play_next_chance()
        refresh_game_board(game)

        last_nav_button_state = nav_button_state

    # # If the select button state has changed and the game is finished, then
    # if can_exit:
    #     game.handle_exit()

    #     last_select_button_state = select_button_state

    # If the navigation button state has changed and the game is not finished, then
    if can_nav:
        game.handle_navigation()

    # If the select button state has changed and the game is not finished, then
    if can_select:
        handle_selection(game)

    # Update the last button states
    last_nav_button_state = nav_button_state
    last_select_button_state = select_button_state

    # Blink all the LEDs which are enabled to blink
    ttt.blink_all(leds)

    pg.display.update()

    # fps_clock.tick(FPS)
