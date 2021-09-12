'''
Responsible for storing all the information about the current state of a chess game ,
It will also be responsible for determining the valid moves at the current state
it will also keep a move log
'''
class GameState():
    def __init__(self):
        #board is 8x8 2 dimensional list, each element of the list has two characters
        #the first character represents the color of the piece, "b" or "w",
        #the second character represents the type of the piece "k","q","r","b","n","p"
        #the string "--" represents an empty space with no pieces
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["--","--","--","--","--","--","--","--"],
            ["--", "--", "--", "--", "--", "--", "--","--"],
            ["--", "--", "--", "--", "--", "--", "--","--"],
            ["--", "--", "--", "--", "--", "--", "--","--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.whiteToMove = True
        self.moveLog = []
class Move():
    def __init__(self, startSq, endSq, board):
        pass