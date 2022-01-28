from chess import *
import numpy as np


pieces = {"r": -5, "n": -3, "b": -3, "q": -9, "k": -100, "p": -1,
          "R": 5, "N": 3, "B": 3, "Q": 9, "K": 100, "P": 1}


def fen_to_matrix(FEN):
    print(FEN)
    matrix = np.zeros((8, 8))
    index = 0
    row = 0
    for char in FEN:
        if char == " ":
            break
        else:
            if char.isdigit():
                index += int(char)
            elif char == "/":
                index = 0
                row += 1
            elif char.isalpha():
                # piece = pieces[char]
                matrix[row][index] = pieces[char]
                index += 1
    print(matrix)


class Omega0:
    def __init__(self, position):
        self.position = position

    def get_best_move(self, FEN):
        pass

    def generate_move(self, position):
        return self.get_best_move(position)

    def testfun(self, board):
        fen_to_matrix(board.fen())
