from stockfish import Stockfish

class Stockfishclass:
    def __init__(self, position):
        self.engine = Stockfish(
            "./lib/stockfish/stockfish_14_win_x64_avx2/stockfish_14_x64_avx2.exe")
        self.position = position
        self.engine.set_fen_position(position)
        self.engine.set_depth(20)
        print(self.engine.get_parameters())

    def generate_move(self, position):
        self.engine.set_fen_position(position)
        print(self.engine.get_evaluation())
        return self.engine.get_best_move()
