# Tic Tac Toe Game with Arduino

The Tic Tac Toe game is implemented on an Arduino board with LEDs and buttons. The game is designed to be played in either human vs human or human vs computer mode. Here's how the game works:

- Connect the Arduino board and initialize the LEDs and buttons.
- When the game starts, the instructions are printed on the screen.
- The game waits for user input to start the game. Pressing the navigation button starts a human vs human game, while pressing the select button starts a human vs computer game.
- Once the game starts, the LEDs corresponding to the Tic Tac Toe grid light up.
- The player (human) can navigate through the grid using the navigation button. Pressing the navigation button iteratively will move the current selection across the grid.
- To make a move, the player can press the select button while the desired cell is selected. The selected cell's LED will change to the player's color.
- If the game is in human vs computer mode, the computer will make its move by changing the LED color of the chosen cell.
- The game continues until either a player wins or the grid is filled without a winner (a draw).
- If the game ends and there are remaining chances to play, the player can press the navigation button to play again. Pressing the select button will exit the game.
- If all the chances to play are exhausted, the game will end, and the game will be restarted after some seconds.

The implementation of the Tic Tac Toe game with Arduino demonstrates the integration of hardware and software components to create an interactive and entertaining game.
