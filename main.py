# tic tac toe game.
# group name:
# group members:

import time
from pyfirmata import Arduino, util, INPUT, OUTPUT, PWM
import tictactoe as ttt

# Constants
ARDUINO_PORT = 'COM6'
LED_PINS = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10}
NAV_BUTTON_PIN = 11
SELECT_BUTTON_PIN = 12
CHANCES_TO_PLAY = 2

# variables
last_nav_button_state = False
last_select_button_state = False
navigation_button_position = 0

try:
    # Connect to the Arduino board
    board = Arduino(ARDUINO_PORT)

    # Start an iterator thread so that serial buffer doesn't overflow
    it = util.Iterator(board)
    it.start()
except Exception as e:
    print('Error while connecting to the Arduino board: {}'.format(e))
    exit(1)


# Create a list of LED objects
leds = [ttt.Led(pin, board) for pin in LED_PINS.values()]

# Create the Game object
game = ttt.Game(leds, CHANCES_TO_PLAY)

# Set navigate button pin mode to INPUT_PULLUP
NAV_BUTTON = board.get_pin('d:{}:i'.format(NAV_BUTTON_PIN))
SELECT_BUTTON = board.get_pin('d:{}:i'.format(SELECT_BUTTON_PIN))

# Enable reporting for the buttons
NAV_BUTTON.enable_reporting()
SELECT_BUTTON.enable_reporting()


# Start the game
game.welcome()

while True:
    current_time = time.time()
    # Read the buttons' states
    nav_button_state = NAV_BUTTON.read()
    select_button_state = SELECT_BUTTON.read()

    nav_button_pressed = nav_button_state and last_nav_button_state != nav_button_state
    select_button_pressed = select_button_state and last_select_button_state != select_button_state

    can_select = select_button_pressed and not game.finished and not game.computer_move and game.started
    can_nav = nav_button_pressed and not game.finished and not game.computer_move and game.started
    can_play_next_chance = nav_button_pressed and game.finished and game.started
    can_exit = select_button_pressed and game.finished and game.started
    can_computer_play = game.computer_move and not game.finished and game.computer_vs_human_mode and (
        (current_time - game.computer_move_start_time) > game.computer_move_delay)
    human_vs_human = nav_button_pressed and not game.started
    computer_vs_human = select_button_pressed and not game.started

    # If the game is not started, then
    if human_vs_human:
        game.start_game()

    if computer_vs_human:
        game.enable_computer_vs_human_mode()
        game.start_game()

    # If the computer is playing, then
    if can_computer_play:
        game.handle_computer_move()

    # If the navigation button state and select button state have changed at same time, then
    if nav_button_pressed and select_button_pressed:
        print('\nPlease use one button at a time.')

    # If the navigation button state has changed and the game is finished, then
    if can_play_next_chance:
        game.handle_play_next_chance()

        last_nav_button_state = nav_button_state

    # If the select button state has changed and the game is finished, then
    if can_exit:
        game.handle_exit()

        last_select_button_state = select_button_state

    # If the navigation button state has changed and the game is not finished, then
    if can_nav:
        game.handle_navigation()

    # If the select button state has changed and the game is not finished, then
    if can_select:
        game.handle_selection()

    # Update the last button states
    last_nav_button_state = nav_button_state
    last_select_button_state = select_button_state

    # Blink all the LEDs which are enabled to blink
    ttt.blink_all(leds)

    # Sleep for 1 millisecond
    time.sleep(0.001)
