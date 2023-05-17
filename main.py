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


try:
    # Connect to the Arduino board
    board = Arduino(ARDUINO_PORT)

    # Start an iterator thread so that serial buffer doesn't overflow
    it = util.Iterator(board)
    it.start()
except Exception as e:
    print('Error while connecting to the Arduino board: {}'.format(e))
    exit(1)


def play_tic_tac_toe():
    global NAV_BUTTON_PIN, SELECT_BUTTON_PIN, board

    # variables
    last_nav_button_state = False
    last_select_button_state = False

    try:
        # Create a list of LED objects
        leds = [ttt.Led(pin, board) for pin in LED_PINS.values()]
    except Exception as e:
        print('Error while creating the LED objects: {}'.format(e))
        exit(1)

    # Set navigate button pin mode to INPUT_PULLUP
    NAV_BUTTON = board.get_pin('d:{}:i'.format(NAV_BUTTON_PIN))
    SELECT_BUTTON = board.get_pin('d:{}:i'.format(SELECT_BUTTON_PIN))

    # Enable reporting for the buttons
    NAV_BUTTON.enable_reporting()
    SELECT_BUTTON.enable_reporting()
    try:
        # Create the Game object
        ttt_game = ttt.Game(leds)
    except Exception as e:
        print('Error while creating the Game object: {}'.format(e))
        exit(1)
    # Start the game
    ttt_game.welcome()
    ttt_game.show_loading_window()
    ttt_game.show_instruction_window()
    time.sleep(5)
    ttt_game.show_choose_mode_window()
    ttt_game.can_get_input = True

    # Main Loop
    while True:
        for event in pg.event.get():
            if event.type == QUIT:
                ttt_game.handle_exit()
                pg.quit()
                sys.exit()

            # global last_nav_button_state, last_select_button_state, game, NAV_BUTTON, SELECT_BUTTON
        current_time = time.time()
        # Read the buttons' states
        nav_button_state = NAV_BUTTON.read()
        select_button_state = SELECT_BUTTON.read()

        nav_button_pressed = ttt_game.can_get_input and nav_button_state and last_nav_button_state != nav_button_state
        select_button_pressed = ttt_game.can_get_input and select_button_state and last_select_button_state != select_button_state

        can_start_again = nav_button_pressed and ttt_game.can_start_again
        can_select = select_button_pressed and not ttt_game.finished and not ttt_game.computer_move and ttt_game.started
        can_nav = nav_button_pressed and not ttt_game.finished and not ttt_game.computer_move and ttt_game.started
        can_play_next_chance = nav_button_pressed and ttt_game.finished and ttt_game.started
        can_exit = select_button_pressed and ttt_game.finished and ttt_game.started
        can_computer_play = ttt_game.computer_move and not ttt_game.finished and ttt_game.computer_vs_human_mode and (
            (current_time - ttt_game.computer_move_start_time) > ttt_game.computer_move_delay)
        human_vs_human = nav_button_pressed and not ttt_game.started
        computer_vs_human = select_button_pressed and not ttt_game.started

        if can_start_again:
            ttt_game.play_button_click_sound()
            ttt_game.handle_start_again()

            last_nav_button_state = nav_button_state

        # If the game is not started, then
        if human_vs_human and last_nav_button_state != nav_button_state:
            ttt_game.play_button_click_sound()
            ttt_game.stop_music()
            ttt_game.start_game()

        if computer_vs_human:
            ttt_game.play_button_click_sound()
            ttt_game.stop_music()
            ttt_game.enable_computer_vs_human_mode()
            ttt_game.start_game()

        # If the computer is playing, then
        if can_computer_play:
            ttt_game.play_button_click_sound()
            ttt_game.do_computer_move()
            ttt_game.handle_selection()

        # If the navigation button state and select button state have changed at same time, then
        if nav_button_pressed and select_button_pressed:
            ttt_game.play_button_click_sound()
            print('\nPlease use one button at a time.')

        # If the navigation button state has changed and the game is finished, then
        if can_play_next_chance:
            ttt_game.play_button_click_sound()
            ttt_game.handle_play_next_chance()

            last_nav_button_state = nav_button_state

        # If the navigation button state has changed and the game is not finished, then
        if can_nav:
            ttt_game.play_button_click_sound()
            ttt_game.handle_navigation()

        # If the select button state has changed and the game is not finished, then
        if can_select:
            ttt_game.handle_selection()

        # Update the last button states
        last_nav_button_state = nav_button_state
        last_select_button_state = select_button_state

        # Blink all the LEDs which are enabled to blink
        ttt.blink_all(leds)

        pg.display.update()

        # fps_clock.tick(FPS)


play_tic_tac_toe()
pg.quit()
sys.exit()
