from stockfish import Stockfish

class Stockfishclass:
    def __init__(self, position):
        #self.engine = Stockfish("C:/Users/Crgla/Desktop/Personal Coding Projects/chessengine/stockfish-11-win/Windows/stockfish_20011801_x64.exe")
        # self.engine = Stockfish(
        #     "C:/Users/Crgla/Desktop/Personal Coding Projects/chessengine/stockfish_14_win_x64_avx2/stockfish_14_x64_avx2.exe")
        self.engine = Stockfish(
            "C:/Users/Crgla/Desktop/Personal Coding Projects/chess-engine/lib/stockfish/stockfish_14_win_x64_avx2/stockfish_14_x64_avx2.exe")
        self.position = position
        self.engine.set_fen_position(position)
        self.engine.set_depth(20)
        print(self.engine.get_parameters())

    def generate_move(self, position):
        self.engine.set_fen_position(position)
        print(self.engine.get_evaluation())
        return self.engine.get_best_move()
