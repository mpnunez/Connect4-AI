import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QPushButton, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox

from connect4lib.aiplayer import AIPlayer
from connect4lib.player import RandomPlayer, HumanPlayer
from connect4lib.game import Game, GameStatus
from connect4lib.player import Player
import numpy as np
from keras.models import load_model


import time

import functools
import pickle

"""

When the game starts or the user presses a button,
loop through next players until the game ends or until you 
reach a human player

"""

class HumanGUIPlayer(Player):
    requires_user_input = True
    def __init__(self,name=None,gui=None):
        super().__init__(name)
        self.next_move = 0
    
    def get_move_scores_deterministic(self,board: np.array) -> np.array:
        n_cols = board.shape[2]
        move_scores = np.zeros(n_cols)
        move_scores[self.next_move] = 1
        return move_scores

def window(game: Game):
    app = QApplication(sys.argv)
    win = QWidget()
    grid = QGridLayout()
    
    _, nrows, ncols = game.board.shape
    
    
    
    pix_maps = {}
    for color in ("empty","red","blue"):
        pix_maps[color] = QPixmap(f'assets/{color}.png')
        pix_maps[color] = pix_maps[color].scaledToWidth(100)
    
    label_grid = []
    for i in range(nrows):
        label_row = []
        for j in range(ncols):
        
            label = QLabel()
            label.setPixmap(pix_maps["empty"])
            grid.addWidget(label,i,j)
            label_row.append(label)
        
        label_grid.append(label_row)


    def update_board():
        for i in range(nrows):
            for j in range(ncols):
                if game.board[0,i,j] == 1:
                    pixmap = pix_maps["red"]
                elif game.board[1,i,j] == 1:
                    pixmap = pix_maps["blue"]
                else:
                    pixmap = pix_maps["empty"]
                pixmap = pixmap.scaledToWidth(100)
                label_grid[i][j].setPixmap(pixmap)

    msg = QMessageBox()
    msg.setWindowTitle("Connect4")
    

    def check_game_completion() -> bool:
        if game.status == GameStatus.COMPLETE:
            game.finish_game()
            msg.setText("Game is complete!")
            msg.exec_()
            
        return game.status == GameStatus.COMPLETE

    @pyqtSlot()
    def move_until_next_human_player():
        while game.status == GameStatus.INPROGRESS and not game.players[game.current_player].requires_user_input:
            time.sleep(1)
            game.next_player_make_move()
            update_board()
            if check_game_completion():
                return

    @pyqtSlot()
    def make_human_move(j):
        if game.status == GameStatus.NOTSTARTED:
            msg.setText("Press 'New Game' to start game")
            msg.exec_()
            return
        if check_game_completion():
            return
        
        if not game.players[game.current_player].requires_user_input:
            return
        
        game.players[game.current_player].next_move = j
        game.next_player_make_move()
        update_board()
        
        if check_game_completion():
            return
        
           
    for j in range(ncols):
        drop_button = QPushButton("Drop")
        grid.addWidget(drop_button,nrows,j)
        drop_button.clicked.connect(functools.partial(make_human_move, j))
        drop_button.clicked.connect(move_until_next_human_player)
        
    # Start game button
    @pyqtSlot()
    def start_new_game():
        game.start_game()
        move_until_next_human_player()
        update_board()

    start_button = QPushButton("New Game")
    start_button.clicked.connect(start_new_game)
    grid.addWidget(start_button,nrows+1,0)
    #game.start_game()
    move_until_next_human_player()

    player_selectors = [QComboBox(), QComboBox()]
    for ind, ps in enumerate(player_selectors):
        ps.addItems(['Human', 'Random', 'Column Spammer', 'Load model'])
        grid.addWidget(ps,nrows+1,ind+1)
    			
    
        
    win.setLayout(grid)
    win.setWindowTitle("PyQt Grid Example")
    win.setGeometry(50,50,200,200)
    win.show()
    
    sys.exit(app.exec_())



def main():
    g = Game()
    human = HumanGUIPlayer(name="Human")
    magnus = AIPlayer(name="Magnus")
    magnus.model = load_model('magnus-2.h5')
    g.players = [human,magnus]
    g.verbose = True

    window(g)
    
    

if __name__ == '__main__':
   main()