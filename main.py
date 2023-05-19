# Import libaries
import pygame as pg
import sys
from pygame.locals import *
from pyfirmata import Arduino, util, INPUT, OUTPUT, PWM
from tictactoe import play_tic_tac_toe

# Constants
ARDUINO_PORT = 'COM6'
LED_PINS = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10}
BUTTON_1 = 11
BUTTON_2 = 12
BUTTON_3 = 13
NAV_BUTTON_PIN = BUTTON_1
SELECT_BUTTON_PIN = BUTTON_2
BACK_BUTTON_PIN = BUTTON_3


# Main function
if __name__ == '__main__':

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
        # Start to play the tic tac toe game
        play_tic_tac_toe(NAV_BUTTON_PIN, SELECT_BUTTON_PIN,
                         BACK_BUTTON_PIN, LED_PINS, board)
    except Exception as e:
        print('Error while playing tic-tac-toe: {}'.format(e))

    pg.quit()
    sys.exit()
