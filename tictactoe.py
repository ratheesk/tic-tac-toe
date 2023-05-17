# This is a Tic Tac Toe self that is played on a breadboard using an Arduino Uno and a 3x3 LED matrix
# The self is played by two players and the players take turns to play
# The players can navigate through the LEDs using the navigation button and select an LED using the select button
# The player who plays first is chosen randomly
# The player who plays first is represented by 1 and the player who plays second is represented by 2
# The player who plays first is represented by the LED that is turned on and the player who plays second is represented by the LED that is turned off

import time
import os
import random
from pyfirmata import Arduino
import pygame as pg
from pygame.locals import *
import sys
# Classes


class Led:
    '''Represents an LED object that can be turned on, turned off, blinked, and selected'''

    def __init__(self, pin, board):
        '''Initializes the LED object with the pin number and the board
        pin: The pin number of the LED
        board: The Arduino board object
        state: The state of the LED (0 or 1)
        last_time_blinked: The last time the LED blinked
        can_blink: A boolean that represents whether the LED can blink or not
        selected: A boolean that represents whether the LED is selected or not
        '''
        if not isinstance(pin, int):
            raise TypeError('pin must be an integer')
        if not isinstance(board, Arduino):
            raise TypeError('board must be an Arduino object')

        self.board = board
        self.pin = self.board.get_pin('d:' + str(pin) + ':o')
        self.state = 0
        self.last_time_blinked = 0
        self.can_blink = False
        self.selected = 0

    def turn_on(self):
        '''Turns the LED on by writing 1 to the pin and setting the state to 1'''
        self.pin.write(1)
        self.state = 1

    def turn_off(self):
        '''Turns the LED off by writing 0 to the pin and setting the state to 0'''
        self.pin.write(0)
        self.state = 0

    def start_blinking(self):
        '''Starts blinking the LED by setting can_blink to True'''
        self.can_blink = True

    def stop_blinking(self):
        '''Stops blinking the LED by setting can_blink to False'''
        self.can_blink = False

    def reset(self):
        '''Resets the LED by turning it off, stopping blinking, setting selected to 0, setting last_time_blinked to 0, and setting state to 0'''
        self.turn_off()
        self.stop_blinking()
        self.selected = 0
        self.last_time_blinked = 0
        self.can_blink = False
        self.state = 0
        self.matched = False


class Game:
    '''Represents a Tic Tac Toe Game'''

    def __init__(self, leds):
        '''Initializes the game with the LEDs and the chances
        leds: A list of LED objects
        chances: The number of chances each player gets
        started: A boolean that represents whether the game has started or not
        finished: A boolean that represents whether the game is finished or not
        navigation_button_position: The position of the navigation button
        current_player: The current player
        player_played_first: The player who played first
        remaining_chances: The remaining chances
        score: The score of the players
        computer_vs_human_mode: A boolean that represents whether the game is in computer vs human mode or not
        computer_move: A boolean that represents whether the computer is making a move or not
        computer_move_start_time: The time when the computer started making a move
        computer_move_delay: The delay between the computer moves
        can_get_input: A boolean that represents whether the game can get input or not
        can_start_again: A boolean that represents whether the game can start again or not
        '''
        if not isinstance(leds, list):
            raise TypeError('leds must be a list')
        if not isinstance(leds[0], Led):
            raise TypeError('leds must be a list of Led objects')

        self.leds = leds
        self.chances = 3
        self.started = False
        self.finished = False
        self.navigation_button_position = 0
        self.navigation_button_last_position = 0
        self.current_player = 1
        self.player_played_first = 1
        self.remaining_chances = self.chances
        self.score = {1: 0, 2: 0}
        self.computer_vs_human_mode = False
        self.computer_move = False
        self.computer_move_start_time = 0
        self.computer_move_delay = 3
        self.can_get_input = False
        self.can_start_again = False
        self.can_skip_instruction = False
        self.notification_in_screen = False

        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800
        self.CELL_COORDINATES = [(73, 77), (256, 77), (439, 77), (73, 259),
                                 (256, 259), (439, 259), (73, 442), (256, 442), (439, 442)]
        self.BOARD_COORDINATES = [(101, 101), (288, 101), (468, 101), (101, 281),
                                  (288, 281), (468, 281), (101, 466), (288, 466), (468, 466)]

        self.initialize_gui()

    def initialize_gui(self):
        '''Initializes the GUI'''
        # Initialize pygame
        pg.init()

        # Initialize the font
        pg.font.init()

        self.default_font = pg.font.get_default_font()
        self.font_renderer = pg.font.Font(self.default_font, 30)

        # Create the screen object
        self.screen = pg.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Set the window title
        pg.display.set_caption('Tic Tac Toe')

        # Load the images
        self.loading_window = pg.image.load("assets/images/loading.png")
        self.instruction_window = pg.image.load(
            "assets/images/instruction.png")
        self.choose_mode_window = pg.image.load(
            "assets/images/choose_mode.png")
        self.champion_player_o_window = pg.image.load(
            "assets/images/champion_player_o.png")
        self.champion_player_x_window = pg.image.load(
            "assets/images/champion_player_x.png")
        self.match_is_draw_window = pg.image.load(
            "assets/images/match_is_draw.png")
        self.computer_is_thinking = pg.image.load(
            "assets/images/computer_is_thinking.png")
        self.computer_is_thinking_bg = pg.image.load(
            "assets/images/computer_is_thinking_bg.png")
        self.cell_selected_bg = pg.image.load(
            "assets/images/cell_selected.png")
        self.cell_not_selected_bg = pg.image.load(
            "assets/images/cell_not_selected.png")
        self.select_position = pg.image.load(
            "assets/images/select_position.png")
        self.thankyou_window = pg.image.load("assets/images/thankyou.png")
        self.player_o_won = pg.image.load("assets/images/player_o_won.png")
        self.player_x_won = pg.image.load("assets/images/player_x_won.png")
        self.game_is_tie = pg.image.load("assets/images/game_is_tie.png")
        self.game_board = pg.image.load("assets/images/game_board.png")
        self.x_img = pg.image.load("assets/images/x.png")
        self.o_img = pg.image.load("assets/images/o.png")
        self.life = pg.image.load("assets/images/life.png")
        self.player_bg = pg.image.load("assets/images/player_bg.png")

        # Resize images
        self.loading_window = pg.transform.scale(
            self.loading_window, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.instruction_window = pg.transform.scale(
            self.instruction_window, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.choose_mode_window = pg.transform.scale(
            self.choose_mode_window, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.champion_player_o_window = pg.transform.scale(
            self.champion_player_o_window, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.champion_player_x_window = pg.transform.scale(
            self.champion_player_x_window, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.match_is_draw_window = pg.transform.scale(
            self.match_is_draw_window, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.thankyou_window = pg.transform.scale(
            self.thankyou_window, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.game_board = pg.transform.scale(
            self.game_board, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.computer_is_thinking = pg.transform.scale(
            self.computer_is_thinking, (561, 121))
        self.computer_is_thinking_bg = pg.transform.scale(
            self.computer_is_thinking_bg, (561, 121))
        self.cell_selected_bg = pg.transform.scale(
            self.cell_selected_bg, (164, 164))
        self.cell_not_selected_bg = pg.transform.scale(
            self.cell_not_selected_bg, (164, 164))
        self.select_position = pg.transform.scale(
            self.select_position, (561, 121))
        self.player_o_won = pg.transform.scale(self.player_o_won, (764, 548))
        self.player_x_won = pg.transform.scale(self.player_x_won, (764, 548))
        self.game_is_tie = pg.transform.scale(self.game_is_tie, (764, 548))
        self.x_img = pg.transform.scale(self.x_img, (107, 118))
        self.o_img = pg.transform.scale(self.o_img, (107, 118))
        self.player_x = pg.transform.scale(self.x_img, (53.5, 59))
        self.player_o = pg.transform.scale(self.o_img, (53.5, 59))
        self.player_bg = pg.transform.scale(self.player_bg, (53.5, 59))
        self.life = pg.transform.scale(self.life, (54, 48))
        self.life_bg = pg.transform.scale(self.player_bg, (54, 48))

        # Load the sounds
        self.select_sound = pg.mixer.Sound("assets/sounds/select.wav")
        self.start_game_sound = pg.mixer.Sound("assets/sounds/start_game.wav")
        self.won_game_sound = pg.mixer.Sound("assets/sounds/won_game.wav")
        self.announce_champion_sound = pg.mixer.Sound(
            "assets/sounds/announce_champion.wav")
        self.click_button_sound = pg.mixer.Sound(
            "assets/sounds/click_button.wav")
        self.alert_sound = pg.mixer.Sound("assets/sounds/alert.wav")

        # Load the music
        self.intro_music = pg.mixer.music.load(
            "assets/sounds/intro.wav")

        # Play the music
        pg.mixer.music.play(-1)

    def stop_music(self):
        '''Stops the music'''
        pg.mixer.music.stop()

    def show_computer_is_thinking(self):
        '''Shows the computer is thinking message'''
        self.screen.blit(self.computer_is_thinking, (65, 660))
        self.notification_in_screen = True
        pg.display.update()

    def show_select_position(self):
        '''Shows the select position message'''
        self.screen.blit(self.select_position, (65, 660))
        self.notification_in_screen = True
        pg.display.update()

    def clear_notification(self):
        '''Clears the notification'''
        self.screen.blit(self.computer_is_thinking_bg, (65, 660))
        pg.display.update()

    def show_player_o_won(self):
        '''Shows the player O won message'''
        self.screen.blit(self.player_o_won, (218, 116))
        pg.display.update()

    def show_player_x_won(self):
        '''Shows the player X won message'''
        self.screen.blit(self.player_x_won, (218, 116))
        pg.display.update()

    def show_game_is_tie(self):
        '''Shows the game is tie message'''
        self.screen.blit(self.game_is_tie, (218, 116))
        pg.display.update()

    def draw_score(self):
        '''Draws the score on the screen'''
        player_1_score = self.font_renderer.render(
            str(self.score[1]), 1, (255, 255, 255))
        player_2_score = self.font_renderer.render(
            str(self.score[2]), 1, (255, 255, 255))
        self.screen.blit(player_1_score, (982, 503))
        self.screen.blit(player_2_score, (982, 590))
        pg.display.update()

    def draw_x(self, position):
        '''Draws X on the screen'''
        self.screen.blit(self.x_img, position)
        pg.display.update()

    def draw_o(self, position):
        '''Draws O on the screen'''
        self.screen.blit(self.o_img, position)
        pg.display.update()

    def draw_cell_selected(self, position):
        '''Draws cell selected on the screen'''
        self.screen.blit(self.cell_selected_bg, position)
        pg.display.update()

    def draw_cell_not_selected(self, position):
        '''Draws cell not selected on the screen'''
        self.screen.blit(self.cell_not_selected_bg, position)
        pg.display.update()

    def update_game_board(self):
        '''Updates the game board'''
        for i in range(9):
            if self.leds[i].selected == 1:
                self.draw_cell_not_selected(self.CELL_COORDINATES[i])
                self.draw_o(self.BOARD_COORDINATES[i])
            elif self.leds[i].selected == 2:
                self.draw_cell_not_selected(self.CELL_COORDINATES[i])
                self.draw_x(self.BOARD_COORDINATES[i])

    def draw_player_x(self):
        '''Draws player X on the screen'''
        self.screen.blit(self.player_bg, (912, 130))
        self.screen.blit(self.player_x, (912, 130))
        pg.display.update()

    def draw_player_o(self):
        '''Draws player O on the screen'''
        self.screen.blit(self.player_bg, (912, 130))
        self.screen.blit(self.player_o, (912, 130))
        pg.display.update()

    def draw_life(self):
        '''Draws the remaining chances'''
        if self.remaining_chances == 3:
            self.screen.blit(self.life, (894, 220))
            self.screen.blit(self.life, (960, 220))
            self.screen.blit(self.life, (1026, 220))
        elif self.remaining_chances == 2:
            self.screen.blit(self.life, (894, 220))
            self.screen.blit(self.life, (960, 220))
            self.screen.blit(self.life_bg, (1026, 220))
        elif self.remaining_chances == 1:
            self.screen.blit(self.life, (894, 220))
            self.screen.blit(self.life_bg, (960, 220))
        elif self.remaining_chances == 0:
            self.screen.blit(self.life_bg, (894, 220))

        pg.display.update()

    def show_game_board(self):
        '''Shows the game board'''
        # Displaying over gamescreen
        self.screen.blit(self.game_board, (0, 0))

        # Updating the display
        pg.display.update()

    def show_choose_mode_window(self):
        '''Shows the choose mode window'''
        # Displaying over gamescreen
        self.screen.blit(self.choose_mode_window, (0, 0))

        # Updating the display
        pg.display.update()

    def show_loading_window(self):
        '''Shows the loading window'''
        # Displaying over gamescreen
        self.screen.blit(self.loading_window, (0, 0))

        # Updating the display
        pg.display.update()
        time.sleep(3)

    def show_instruction_window(self):
        '''Shows the instruction window'''
        # Displaying over gamescreen
        self.screen.blit(self.instruction_window, (0, 0))

        # Updating the display
        pg.display.update()

    def show_thankyou_window(self):
        '''Shows the thankyou window'''
        # Displaying over gamescreen
        self.screen.blit(self.thankyou_window, (0, 0))

        # Updating the display
        pg.display.update()

    def show_champion_player_o_window(self):
        '''Shows the champion player O window'''
        # Displaying over gamescreen
        self.screen.blit(self.champion_player_o_window, (0, 0))

        # Updating the display
        pg.display.update()

    def show_champion_player_x_window(self):
        '''Shows the champion player X window'''
        # Displaying over gamescreen
        self.screen.blit(self.champion_player_x_window, (0, 0))

        # Updating the display
        pg.display.update()

    def show_match_is_draw_window(self):
        '''Shows the match is draw window'''
        # Displaying over gamescreen
        self.screen.blit(self.match_is_draw_window, (0, 0))

        # Updating the display
        pg.display.update()

    def refresh_game_board(self):
        '''Refreshes the game board'''
        self.show_game_board()
        if self.current_player == 1:
            self.draw_player_o()

        if self.current_player == 2:
            self.draw_player_x()

        self.draw_life()

        self.draw_score()

    def reset_all_leds(self):
        '''Resets all the LEDs'''
        for led in self.leds:
            led.reset()

    def turn_on_all(self):
        '''Turns on all the LEDs'''
        for led in self.leds:
            led.turn_on()

    def turn_off_all(self):
        '''Turns off all the LEDs'''
        for led in self.leds:
            led.turn_off()
            led.stop_blinking()

    def blink_all(self):
        '''Blinks all the LEDs '''
        for led in self.leds:
            led.start_blinking()

    def welcome(self):
        '''Turns on all the LEDs for 1 second to welcome the player'''
        os.system('cls')
        self.turn_on_all()
        time.sleep(1)
        self.turn_off_all()
        print('\n')
        print('Welocme to the game')

    def start_game(self):
        '''Starts the self'''
        self.started = True
        self.welcome()
        self.refresh_game_board()
        pg.mixer.Sound.play(self.start_game_sound)

    def do_all_leds_selected(self):
        '''Returns True if all the LEDs are selected'''
        for led in self.leds:
            if led.selected == 0:
                return False
        return True

    def navigate(self):
        '''Navigates the LEDS using the navigation button'''
        if self.do_all_leds_selected():
            return

        self.navigation_button_last_position = self.navigation_button_position

        self.navigation_button_position = self.navigation_button_position % len(
            self.leds) + 1

        while self.leds[self.navigation_button_position - 1].selected != 0:
            self.navigation_button_position = self.navigation_button_position % len(
                self.leds) + 1

        if self.current_player == 1:
            self.leds[self.navigation_button_position - 1].turn_on()
        else:
            self.leds[self.navigation_button_position - 1].start_blinking()

        for led in self.leds:
            if led != self.leds[self.navigation_button_position - 1] and led.selected == 0:
                led.turn_off()
                led.stop_blinking()

    def enable_computer_vs_human_mode(self):
        '''Enables computer vs human mode'''
        self.computer_vs_human_mode = True

    def disable_computer_vs_human_mode(self):
        '''Disables computer vs human mode'''
        self.computer_vs_human_mode = False

    def disable_computer_move(self):
        '''Disables computer move'''
        self.computer_move = False

    def enable_computer_move(self):
        '''Enables computer move'''
        self.computer_move = True

    def do_computer_move(self):
        '''Computer move for easy level it set the random position for navigation button'''
        game_board = [led.selected for led in self.leds]
        symbol = 2

        if self.do_all_leds_selected():
            raise Exception('All LEDs are selected')

        # Define a list of possible moves
        all_possible_moves = [
            i for i, val in enumerate(game_board) if val == 0]

        # Check if there is an opportunity to win the self
        for move in all_possible_moves:
            test_board = game_board.copy()
            test_board[move] = symbol
            for i in range(3):
                # Check rows
                if test_board[i*3:(i+1)*3] == [symbol]*3:
                    self.navigation_button_position = move + 1
                    return
                # Check columns
                if test_board[i::3] == [symbol]*3:
                    self.navigation_button_position = move + 1
                    return
            # Check diagonals
            if test_board[0::4] == [symbol]*3 or test_board[2:7:2] == [symbol]*3:
                self.navigation_button_position = move + 1
                return

        # Check if the opponent has an opportunity to win
        opponent_symbol = 1 if symbol == 2 else 2
        for move in all_possible_moves:
            test_board = game_board.copy()
            test_board[move] = opponent_symbol
            for i in range(3):
                # Check rows
                if test_board[i*3:(i+1)*3] == [opponent_symbol]*3:
                    self.navigation_button_position = move + 1
                    return
                # Check columns
                if test_board[i::3] == [opponent_symbol]*3:
                    self.navigation_button_position = move + 1
                    return
            # Check diagonals
            if test_board[0::4] == [opponent_symbol]*3 or test_board[2:7:2] == [opponent_symbol]*3:
                self.navigation_button_position = move + 1
                return

        def add_available_positions(list1, list2):
            for i in list2:
                if i not in list1:
                    list1.append(i)
            return list1

            # Check if a empty cell is available near to already selected cell by the computer
        if symbol in game_board:
            positions = [i for i, val in enumerate(
                game_board) if val == symbol]
            possible_moves = []
            for position in positions:
                if position == 0:
                    can_1 = True if (
                        game_board[1] == 0 and game_board[2] == 0) else False
                    can_3 = True if (
                        game_board[3] == 0 and game_board[6] == 0) else False
                    can_4 = True if (
                        game_board[4] == 0 and game_board[8] == 0) else False

                    if can_1 and can_3 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 3, 4, 2, 6, 8])
                    elif can_1 and can_3:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 3, 2, 6])
                    elif can_1 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 4, 2, 8])
                    elif can_3 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [3, 4, 6, 8])
                    elif can_1:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 2])
                    elif can_3:
                        possible_moves = add_available_positions(
                            possible_moves, [3, 6])
                    elif can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [4, 8])

                elif position == 1:
                    can_0 = True if (
                        game_board[0] == 0 and game_board[2] == 0) else False
                    can_4 = True if (
                        game_board[0] == 0 and game_board[8] == 0) else False

                    if can_0 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 4, 2, 8])
                    elif can_0:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 2])
                    elif can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [4, 8])

                elif position == 2:
                    can_1 = True if (
                        game_board[0] == 0 and game_board[1] == 0) else False
                    can_5 = True if (
                        game_board[5] == 0 and game_board[8] == 0) else False
                    can_4 = True if (
                        game_board[4] == 0 and game_board[6] == 0) else False

                    if can_1 and can_5 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 5, 4, 0, 8, 6])
                    elif can_1 and can_5:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 5, 0, 8])
                    elif can_1 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 4, 0, 6])
                    elif can_5 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [5, 4, 8, 6])
                    elif can_1:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 0])
                    elif can_5:
                        possible_moves = add_available_positions(
                            possible_moves, [5, 8])
                    elif can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [4, 6])

                elif position == 3:
                    can_0 = True if (
                        game_board[0] == 0 and game_board[6] == 0) else False
                    can_4 = True if (
                        game_board[4] == 0 and game_board[5] == 0) else False

                    if can_0 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 4, 6, 5])
                    elif can_0:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 6])
                    elif can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [4, 5])

                elif position == 4:
                    can_0 = True if (
                        game_board[0] == 0 and game_board[8] == 0) else False
                    can_1 = True if (
                        game_board[1] == 0 and game_board[7] == 0) else False
                    can_2 = True if (
                        game_board[2] == 0 and game_board[6] == 0) else False
                    can_3 = True if (
                        game_board[3] == 0 and game_board[5] == 0) else False

                    if can_0 and can_1 and can_2 and can_3:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 1, 2, 3, 5, 6, 7, 8])
                    elif can_0 and can_1 and can_2:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 1, 2, 6, 7, 8])
                    elif can_0 and can_1 and can_3:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 1, 3, 5, 7, 8])
                    elif can_0 and can_2 and can_3:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 2, 3, 5, 6, 8])
                    elif can_1 and can_2 and can_3:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 2, 3, 5, 6, 7])
                    elif can_0 and can_1:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 1, 7, 8])
                    elif can_0 and can_2:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 2, 6, 8])
                    elif can_0 and can_3:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 3, 5, 8])
                    elif can_1 and can_2:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 2, 6, 7])
                    elif can_1 and can_3:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 3, 5, 7])
                    elif can_2 and can_3:
                        possible_moves = add_available_positions(
                            possible_moves, [2, 3, 5, 6])
                    elif can_0:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 8])
                    elif can_1:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 7])
                    elif can_2:
                        possible_moves = add_available_positions(
                            possible_moves, [2, 6])
                    elif can_3:
                        possible_moves = add_available_positions(
                            possible_moves, [3, 5])

                elif position == 5:
                    can_2 = True if (
                        game_board[2] == 0 and game_board[8] == 0) else False
                    can_4 = True if (
                        game_board[3] == 0 and game_board[4] == 0) else False

                    if can_2 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [2, 3, 4, 8])
                    elif can_2:
                        possible_moves = add_available_positions(
                            possible_moves, [2, 8])
                    elif can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [3, 4])

                elif position == 6:
                    can_3 = True if (
                        game_board[0] == 0 and game_board[3] == 0) else False
                    can_7 = True if (
                        game_board[7] == 0 and game_board[8] == 0) else False
                    can_4 = True if (
                        game_board[2] == 0 and game_board[4] == 0) else False

                    if can_3 and can_7 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 2, 3, 4, 7, 8])
                    elif can_3 and can_7:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 3, 7, 8])
                    elif can_3 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 2, 3, 4])
                    elif can_7 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [2, 4, 7, 8])
                    elif can_3:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 3])
                    elif can_7:
                        possible_moves = add_available_positions(
                            possible_moves, [7, 8])
                    elif can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [2, 4])

                elif position == 7:
                    can_6 = True if (
                        game_board[6] == 0 and game_board[8] == 0) else False
                    can_4 = True if (
                        game_board[1] == 0 and game_board[4] == 0) else False

                    if can_6 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 4, 6, 8])
                    elif can_6:
                        possible_moves = add_available_positions(
                            possible_moves, [6, 8])
                    elif can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [1, 4])

                elif position == 8:
                    can_7 = True if (
                        game_board[6] == 0 and game_board[7] == 0) else False
                    can_5 = True if (
                        game_board[2] == 0 and game_board[5] == 0) else False
                    can_4 = True if (
                        game_board[0] == 0 and game_board[4] == 0) else False

                    if can_7 and can_5 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 2, 4, 5, 6, 7])
                    elif can_7 and can_5:
                        possible_moves = add_available_positions(
                            possible_moves, [2, 5, 6, 7])
                    elif can_7 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 4, 6, 7])
                    elif can_5 and can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 2, 4, 5])
                    elif can_7:
                        possible_moves = add_available_positions(
                            possible_moves, [6, 7])
                    elif can_5:
                        possible_moves = add_available_positions(
                            possible_moves, [2, 5])
                    elif can_4:
                        possible_moves = add_available_positions(
                            possible_moves, [0, 4])
            if len(possible_moves) != 0:
                self.navigation_button_position = random.choice(
                    possible_moves) + 1
                return

        # If there is no opportunity to win or block the opponent's winning move, sdo a random move
        self.navigation_button_position = random.choice(all_possible_moves) + 1

    def select(self):
        '''Selects the LED using the select button'''
        if self.navigation_button_position == 0:
            return
        elif self.leds[self.navigation_button_position - 1].selected != 0:
            return

        if self.current_player == 1:
            self.leds[self.navigation_button_position - 1].turn_on()
            self.leds[self.navigation_button_position - 1].selected = 1
        else:
            self.leds[self.navigation_button_position - 1].start_blinking()
            self.leds[self.navigation_button_position - 1].selected = 2

    def switch_players(self):
        '''Switches the current player'''
        self.current_player = 1 if self.current_player == 2 else 2

        if self.computer_vs_human_mode:
            if self.computer_move:
                self.disable_computer_move()
            else:
                self.enable_computer_move()
                self.computer_move_start_time = time.time()

    def check_for_win(self):
        '''Checks if the current player has won'''
        # Check for rows
        for i in range(0, len(self.leds), 3):
            if self.leds[i].selected == self.leds[i + 1].selected == self.leds[i + 2].selected != 0:
                return True
        # Check for columns
        for i in range(0, 3):
            if self.leds[i].selected == self.leds[i + 3].selected == self.leds[i + 6].selected != 0:
                return True
        # Check for diagonals
        if self.leds[0].selected == self.leds[4].selected == self.leds[8].selected != 0:
            return True
        if self.leds[2].selected == self.leds[4].selected == self.leds[6].selected != 0:
            return True
        return False

    def check_for_draw(self):
        '''Checks if the self is a draw'''
        if self.do_all_leds_selected():
            return True
        return False

    def handle_win(self):
        '''Handles the win'''
        self.score[self.current_player] += 100
        self.finished = True
        self.remaining_chances -= 1

    def handle_draw(self):
        '''Handles the draw'''
        self.score[1] += 50
        self.score[2] += 50
        self.finished = True
        self.remaining_chances -= 1

    def play_next_chance(self):
        '''Plays the next chance'''
        self.reset_all_leds()
        self.finished = False
        self.navigation_button_position = 0
        self.switch_players()
        self.player_played_first = self.current_player

    def reset_game(self):
        '''Resets the self'''
        self.reset_all_leds()
        self.finished = False
        self.navigation_button_position = 0
        self.current_player = 1
        self.player_played_first = 1
        self.remaining_chances = self.chances
        self.score = {1: 0, 2: 0}
        self.computer_vs_human_mode = False
        self.computer_move = False
        self.computer_move_start_time = 0
        self.started = False
        self.can_start_again = True
        self.can_get_input = True

    def handle_navigation(self):
        '''Handles the navigation button'''
        try:
            if self.notification_in_screen:
                self.clear_notification()

            self.navigate()

            if self.navigation_button_last_position != 0:
                self.draw_cell_not_selected(
                    self.CELL_COORDINATES[self.navigation_button_last_position - 1])

            if self.navigation_button_position != 0:
                self.draw_cell_selected(
                    self.CELL_COORDINATES[self.navigation_button_position - 1])

        except Exception as e:
            print('\n')
            print(e)

    def handle_selection(self):
        '''Handles the selection of the navigation button'''
        if self.navigation_button_position == 0:
            self.show_select_position()
            pg.mixer.Sound.play(self.alert_sound)
            return
        try:
            self.can_get_input = False
            self.select()
            self.navigation_button_position = 0
            self.update_game_board()
            pg.mixer.Sound.play(self.select_sound)

            self.can_get_input = True

            if self.notification_in_screen:
                self.clear_notification()

            if self.check_for_win():
                self.handle_win()
                if self.current_player == 1:
                    self.show_player_o_won()
                    pg.mixer.Sound.play(self.won_game_sound)
                elif self.current_player == 2:
                    self.show_player_x_won()
                    pg.mixer.Sound.play(self.won_game_sound)

            elif self.check_for_draw():
                self.handle_draw()
                self.show_game_is_tie()
                pg.mixer.Sound.play(self.won_game_sound)

            if not self.finished:
                self.switch_players()

                if self.current_player == 1:
                    self.draw_player_o()

                if self.current_player == 2:
                    self.draw_player_x()

                self.draw_life()

            if self.computer_move:
                self.show_computer_is_thinking()

            if self.remaining_chances == 0:
                print('\nNo more chances left.')
                if self.score[1] > self.score[2]:
                    self.show_champion_player_o_window()
                    pg.mixer.Sound.play(self.announce_champion_sound)
                elif self.score[1] < self.score[2]:
                    self.show_champion_player_x_window()
                    pg.mixer.Sound.play(self.announce_champion_sound)
                else:
                    self.show_match_is_draw_window()
                    pg.mixer.Sound.play(self.announce_champion_sound)

                self.reset_game()

        except Exception as e:
            print('\n')
            print(e)

    def handle_exit(self):
        '''Handles the exit button'''
        try:
            # Reset the self
            self.reset_game()
            self.welcome()
        except Exception as e:
            print('\n')
            print(e)

    def handle_play_next_chance(self):
        '''Handles the play next chance button'''
        try:
            self.play_next_chance()
            self.refresh_game_board()
            pg.mixer.Sound.play(self.start_game_sound)

        except Exception as e:
            print('\n')
            print(e)

    def handle_computer_move(self):
        '''Handles the computer move'''
        self.do_computer_move()
        self.handle_selection()

    def handle_start_again(self):
        '''Handles the start again button'''
        self.can_get_input = False
        self.welcome()
        # Play the music
        pg.mixer.music.play(-1)
        self.show_loading_window()
        self.show_choose_mode_window()
        self.can_get_input = True
        self.can_start_again = False

    def play_button_click_sound(self):
        '''Plays the button sound'''
        pg.mixer.Sound.play(self.click_button_sound)

# Functions


def blink_all(leds, delay=0.1):
    '''Blinks all the LEDs by turning them on and off after a delay
    leds: the list of LED objects
    delay: the delay between each blink
    '''
    current_time = time.time()
    for led in leds:
        if current_time - led.last_time_blinked >= delay and led.can_blink:
            if led.state == 0:
                led.turn_on()
            else:
                led.turn_off()

            led.last_time_blinked = current_time


def play_tic_tac_toe(NAV_BUTTON_PIN, SELECT_BUTTON_PIN, LED_PINS,  board):
    '''Plays the tic tac toe game
    NAV_BUTTON_PIN: the pin number of the navigation button
    SELECT_BUTTON_PIN: the pin number of the select button
    LED_PINS: the dictionary of the LED pins
    board: the pyfirmata board object
    '''

    if not isinstance(NAV_BUTTON_PIN, int):
        raise TypeError('NAV_BUTTON_PIN must be an integer')

    if not isinstance(SELECT_BUTTON_PIN, int):
        raise TypeError('SELECT_BUTTON_PIN must be an integer')

    if not isinstance(LED_PINS, dict):
        raise TypeError('LED_PINS must be a dictionary')

    if not isinstance(board, Arduino):
        raise TypeError('board must be a Arduino object')

    # variables
    last_nav_button_state = False
    last_select_button_state = False

    try:
        # Create a list of LED objects
        leds = [Led(pin, board) for pin in LED_PINS.values()]
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
        ttt_game = Game(leds)
    except Exception as e:
        print('Error while creating the Game object: {}'.format(e))
        exit(1)
    # Start the game
    ttt_game.welcome()
    ttt_game.show_loading_window()
    ttt_game.can_skip_instruction = True
    ttt_game.can_get_input = True
    ttt_game.show_instruction_window()

    # Main Loop
    while True:
        for event in pg.event.get():
            if event.type == QUIT:
                ttt_game.handle_exit()
                pg.quit()
                sys.exit()

        random_computer_thinking_time = random.randint(
            1, ttt_game.computer_move_delay)

        current_time = time.time()
        # Read the buttons' states
        nav_button_state = NAV_BUTTON.read()
        select_button_state = SELECT_BUTTON.read()

        nav_button_pressed = ttt_game.can_get_input and nav_button_state and last_nav_button_state != nav_button_state
        select_button_pressed = ttt_game.can_get_input and select_button_state and last_select_button_state != select_button_state

        can_skip_instruction = nav_button_pressed and not ttt_game.started and ttt_game.can_skip_instruction
        can_start_again = nav_button_pressed and ttt_game.can_start_again
        can_select = select_button_pressed and not ttt_game.finished and not ttt_game.computer_move and ttt_game.started
        can_nav = nav_button_pressed and not ttt_game.finished and not ttt_game.computer_move and ttt_game.started
        can_play_next_chance = nav_button_pressed and ttt_game.finished and ttt_game.started
        can_exit = select_button_pressed and ttt_game.finished and ttt_game.started
        can_computer_play = ttt_game.computer_move and not ttt_game.finished and ttt_game.computer_vs_human_mode and (
            (current_time - ttt_game.computer_move_start_time) > random_computer_thinking_time)
        human_vs_human = nav_button_pressed and not ttt_game.started
        computer_vs_human = select_button_pressed and not ttt_game.started

        if can_skip_instruction:
            ttt_game.play_button_click_sound()
            ttt_game.show_choose_mode_window()
            ttt_game.can_skip_instruction = False

            last_nav_button_state = nav_button_state

        if can_start_again and last_nav_button_state != nav_button_state:
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
        blink_all(leds)

        pg.display.update()

        # fps_clock.tick(FPS)
