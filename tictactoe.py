# This is a Tic Tac Toe game that is played on a breadboard using an Arduino Uno and a 3x3 LED matrix
# The game is played by two players and the players take turns to play
# The players can navigate through the LEDs using the navigation button and select an LED using the select button
# The player who plays first is chosen randomly
# The player who plays first is represented by 1 and the player who plays second is represented by 2
# The player who plays first is represented by the LED that is turned on and the player who plays second is represented by the LED that is turned off

import time
import os
import random
from pyfirmata import Arduino
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
        matched: A boolean that represents whether the LED is matched or not
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
        self.matched = False

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
    '''Represents a Tic Tac Toe game'''

    def __init__(self, leds, chances):
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
        if not isinstance(chances, int):
            raise TypeError('chances must be an integer')
        if not isinstance(leds[0], Led):
            raise TypeError('leds must be a list of Led objects')

        self.leds = leds
        self.chances = chances
        self.started = False
        self.finished = False
        self.navigation_button_position = 0
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

    def color_text(self, text, fg_color='white', bg_color='black'):
        '''Returns the text with the specified foreground and background color'''
        colors = {
            'black': '235',
            'red': '196',
            'green': '46',
            'yellow': '228',
            'blue': '45',
            'purple': '165',
            'cyan': '159',
            'white': '231',
            'orange': '209',
            'dark red': '88',
            'dark green': '22',
            'dark blue': '18',
        }
        text = "\033[48;5;{}m\033[38;5;{}m{}\033[0;0m".format(
            colors[bg_color], colors[fg_color], text)

        return text

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
        bullet = self.color_text('~', 'red', 'black')
        print('\n')
        message = "    Welcome to Tic Tac Toe!    "

        print(self.color_text(' ' + '~' *
              (len(message) + 2) + ' ', 'white', 'dark blue'))
        print(self.color_text('  ' + message + '  ', 'yellow', 'dark blue'))
        print(self.color_text(' ' + '~' *
              (len(message) + 2) + ' ', 'white', 'dark blue'))

        print('\n' + self.color_text('📌 Instructions', 'green', 'black'))
        print('\n' + bullet +
              self.color_text(' Player 1 starts first', 'white', 'black'))
        print(bullet + self.color_text(' Use the navigation button to navigate to the LED you want to select', 'white', 'black'))
        print(bullet + self.color_text(
            ' Use the select button to select the LED you want to select', 'white', 'black'))
        print(bullet + self.color_text(' Player 1 is represented by a solid LED', 'white', 'black'))
        print(bullet + self.color_text(' Player 2 is represented by a blinking LED', 'white', 'black'))
        print(bullet + self.color_text(' The first player to get 3 LEDs in a row, column or diagonal wins', 'white', 'black'))
        print(bullet + self.color_text(
            ' If all the LEDs are selected and no one has won, it is a draw', 'white', 'black'))
        print(bullet + self.color_text(' You will have {} chances to play and if you can stop the game at any time of the end of a match'.format(5), 'white', 'black'))
        print('\n 😍 ' + self.color_text('Good luck!', 'yellow', 'black'))

        if self.started:
            print(self.color_text(
                '\n >> Now the person 1 can start the game by pressing the navigation button!', 'white', 'black'))
        else:
            print(self.color_text(
                '\n >> Press the navigation button to play in "human vs human mode" or press select button to play in "computer vs human mode"!', 'white', 'black'))

    def print_score_board(self):
        print('\n' + self.color_text('-') * 22)
        # print it is human vs human or human vs computer
        if self.computer_vs_human_mode:
            print(self.color_text('Game Mode: {}'.format(self.color_text(
                " Computer vs Human ", 'white', 'dark red')), 'blue', 'black'))
        else:
            print(self.color_text('Game Mode: {}'.format(self.color_text(
                " Human vs Human ", 'white', 'dark red')), 'blue', 'black'))

        if self.computer_move:
            print(self.color_text('Current player: {}'.format(self.color_text(
                " " + 'Computer' + " ", 'white', 'dark red')), 'blue', 'black'))
        else:
            print(self.color_text('Current player: {}'.format(self.color_text(
                " " + str(self.current_player) + " ", 'white', 'dark red')), 'blue', 'black'))
        if self.remaining_chances == 0:
            print(self.color_text('Remaining chances: {}'.format(self.color_text(
                " " + '0' + " ", 'white', 'dark red')), 'blue', 'black'))
        else:
            print(self.color_text('Remaining lives: {}'.format(self.color_text(
                " " + ("🤍")*self.remaining_chances + " ", 'white', 'dark red')), 'blue', 'black'))
        print(self.color_text('-') * 22)
        print(self.color_text('Score:', 'white', 'black'))
        print(self.color_text('Player 1 Score: {}'.format(self.color_text(
            " " + str(self.score[1]) + " ", 'white', 'dark red')), 'blue', 'black'))
        print(self.color_text('Player 2 Score: {}'.format(self.color_text(
            " " + str(self.score[2]) + " ", 'white', 'dark red')), 'blue', 'black'))
        print(self.color_text('-') * 22)
        if self.computer_vs_human_mode and self.computer_move:
            print('\n' + self.color_text('😎 Computer is thinking...', 'yellow', 'black'))

    def print_game_board(self):
        # Define the characters for the lines and boxes
        horizontal_line = self.color_text("-", 'white', 'dark green')
        vertical_line = self.color_text("|", 'white', 'dark green')
        corner = self.color_text("+", 'white', 'dark green')
        space = self.color_text(" ", 'white', 'dark green')
        circle = self.color_text("O", 'white', 'dark green')
        cross = self.color_text("X", 'white', 'dark green')
        red_circle = self.color_text("O", 'red', 'dark green')
        red_cross = self.color_text("X", 'red', 'dark green')
        value = []

        i = 0
        for led in self.leds:
            if led.selected == 1 and led.matched:
                value.append(red_circle)
            elif led.selected == 1 and not led.matched:
                value.append(circle)
            elif led.selected == 2 and led.matched:
                value.append(red_cross)
            elif led.selected == 2 and not led.matched:
                value.append(cross)
            elif led.selected == 0 and self.navigation_button_position == i + 1:
                if self.current_player == 1:
                    value.append(self.color_text("O", 'yellow', 'dark green'))
                else:
                    value.append(self.color_text("X", 'yellow', 'dark green'))
            else:
                value.append(space)

            i += 1

        print('\n')
        # Print the grid
        print(space + corner + horizontal_line * 3 + corner +
              horizontal_line * 3 + corner + horizontal_line * 3 + corner + space)
        print(space + vertical_line + space + value[0] + space + vertical_line +
              space + value[1] + space + vertical_line + space + value[2] + space + vertical_line + space)
        print(space + corner + horizontal_line * 3 + corner +
              horizontal_line * 3 + corner + horizontal_line * 3 + corner + space)
        print(space + vertical_line + space + value[3] + space + vertical_line +
              space + value[4] + space + vertical_line + space + value[5] + space + vertical_line + space)
        print(space + corner + horizontal_line * 3 + corner +
              horizontal_line * 3 + corner + horizontal_line * 3 + corner + space)
        print(space + vertical_line + space + value[6] + space + vertical_line +
              space + value[7] + space + vertical_line + space + value[8] + space + vertical_line + space)
        print(space + corner + horizontal_line * 3 + corner +
              horizontal_line * 3 + corner + horizontal_line * 3 + corner + space)

    def start_game(self):
        '''Starts the game'''
        self.started = True
        self.welcome()
        self.print_score_board()
        self.print_game_board()

    def do_all_leds_selected(self):
        '''Returns True if all the LEDs are selected'''
        for led in self.leds:
            if led.selected == 0:
                return False
        return True

    def navigate(self):
        '''Navigates the LEDS using the navigation button'''
        if self.do_all_leds_selected():
            raise Exception('All LEDs are selected')

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
        print('Computer move')
        game_board = [led.selected for led in self.leds]
        print(game_board)
        symbol = 2

        if self.do_all_leds_selected():
            raise Exception('All LEDs are selected')

        # Define a list of possible moves (i.e., indices of the board where the value is 0)
        possible_moves = [i for i, val in enumerate(game_board) if val == 0]

        # Check if there is an opportunity to win the game
        for move in possible_moves:
            test_board = game_board.copy()
            test_board[move] = symbol
            for i in range(3):
                # Check rows
                if test_board[i*3:(i+1)*3] == [symbol]*3:
                    self.navigation_button_position = move
                # Check columns
                if test_board[i::3] == [symbol]*3:
                    self.navigation_button_position = move
            # Check diagonals
            if test_board[0::4] == [symbol]*3 or test_board[2:7:2] == [symbol]*3:
                self.navigation_button_position = move

        # Check if the opponent has an opportunity to win
        opponent_symbol = 1 if symbol == 2 else 2
        for move in possible_moves:
            test_board = game_board.copy()
            test_board[move] = opponent_symbol
            for i in range(3):
                # Check rows
                if test_board[i*3:(i+1)*3] == [opponent_symbol]*3:
                    self.navigation_button_position = move
                # Check columns
                if test_board[i::3] == [opponent_symbol]*3:
                    self.navigation_button_position = move
            # Check diagonals
            if test_board[0::4] == [opponent_symbol]*3 or test_board[2:7:2] == [opponent_symbol]*3:
                self.navigation_button_position = move

        # If there is no opportunity to win or block the opponent's winning move, sdo a random move
        self.navigation_button_position = random.choice(possible_moves)

    def select(self):
        '''Selects the LED using the select button'''
        if self.navigation_button_position == 0:
            raise Exception(
                'Please select a position using the navigation button')
        elif self.leds[self.navigation_button_position - 1].selected != 0:
            raise Exception('This position is already selected')

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

        os.system('cls')
        self.print_score_board()
        self.print_game_board()

    def check_for_win(self):
        '''Checks if the current player has won'''
        # Check for rows
        for i in range(0, len(self.leds), 3):
            if self.leds[i].selected == self.leds[i + 1].selected == self.leds[i + 2].selected != 0:
                self.leds[i].matched = True
                self.leds[i + 1].matched = True
                self.leds[i + 2].matched = True
                return True
        # Check for columns
        for i in range(0, 3):
            if self.leds[i].selected == self.leds[i + 3].selected == self.leds[i + 6].selected != 0:
                self.leds[i].matched = True
                self.leds[i + 3].matched = True
                self.leds[i + 6].matched = True
                return True
        # Check for diagonals
        if self.leds[0].selected == self.leds[4].selected == self.leds[8].selected != 0:
            self.leds[0].matched = True
            self.leds[4].matched = True
            self.leds[8].matched = True
            return True
        if self.leds[2].selected == self.leds[4].selected == self.leds[6].selected != 0:
            self.leds[2].matched = True
            self.leds[4].matched = True
            self.leds[6].matched = True
            return True
        return False

    def check_for_draw(self):
        '''Checks if the game is a draw'''
        if self.do_all_leds_selected():
            return True
        return False

    def announce_win(self):
        '''Announces the winner'''
        self.score[self.current_player] += 100
        self.finished = True
        self.remaining_chances -= 1
        os.system('cls')
        self.print_score_board()
        self.print_game_board()
        print('\nPlayer {} wins!'.format(self.current_player))
        print(
            '\nTo play again, press the navigation button. To exit, press the select button.')

    def announce_draw(self):
        self.score[1] += 50
        self.score[2] += 50
        self.finished = True
        self.remaining_chances -= 1
        os.system('cls')
        self.print_score_board()
        self.print_game_board()
        print('\nDraw!')
        print(
            '\nTo play again, press the navigation button. To exit, press the select button.')

    def announce_final_winner(self):
        '''Announces the winner'''
        os.system('cls')
        self.print_score_board()
        self.print_game_board()
        print('\nGame Over!')
        print('\n')
        if self.score[1] > self.score[2]:
            print('Player 1 wins!')
        elif self.score[1] < self.score[2]:
            print('Player 2 wins!')
        else:
            print('It is a draw!')

    def play_next_chance(self):
        '''Plays the next chance'''
        self.reset_all_leds()
        self.finished = False
        self.navigation_button_position = 0
        self.switch_players()
        self.player_played_first = self.current_player
        os.system('cls')
        print('\nPlaying the next chance!')
        self.print_score_board()
        self.print_game_board()

    def reset_game(self):
        '''Resets the game'''
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

    def handle_selection(self):
        '''Handles the selection of the navigation button'''
        try:
            self.select()
            self.navigation_button_position = 0

            if self.check_for_win():
                self.announce_win()
            elif self.check_for_draw():
                self.announce_draw()

            if not self.finished:
                self.switch_players()

            if self.remaining_chances == 0:
                print('\nNo more chances left.')
                self.announce_final_winner()
                self.reset_game()

        except Exception as e:
            print('\n')
            print(e)

    def handle_navigation(self):
        '''Handles the navigation button'''
        try:
            self.navigate()
            os.system('cls')
            self.print_score_board()
            self.print_game_board()
        except Exception as e:
            print('\n')
            print(e)

    def handle_exit(self):
        '''Handles the exit button'''
        try:
            # Reset the game
            print('\nYou have chosen to reset the game.')
            self.announce_final_winner()
            print('\nResetting the game in 3 seconds...')
            self.reset_game()
            self.welcome()
        except Exception as e:
            print('\n')
            print(e)

    def handle_play_next_chance(self):
        '''Handles the play next chance button'''
        try:
            print('\nYou have chosen to play the next chance.')
            self.play_next_chance()
        except Exception as e:
            print('\n')
            print(e)

    def handle_computer_move(self):
        '''Handles the computer move'''
        self.do_computer_move()
        self.handle_selection()

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
