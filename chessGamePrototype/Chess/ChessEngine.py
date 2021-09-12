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
            ["--", "--", "--", "bP", "--", "--", "--","--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {"P":self.getPawnMoves,"R":self.getRookMoves,"N":self.getKnightMoves,
                              "B":self.getBishopMoves,"Q":self.getQueenMoves,"K":self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
    '''
    takes a move as a parameter and executes it,
    this will not work for castling, promotion and/or en passant'''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)#log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove
        #update the king's location
        if(move.pieceMoved == "wK"):
            self.whiteKingLocation = (move.endRow,move.endCol)
        elif(move.pieceMoved == "bK"):
            self.blackKingLocation = (move.endRow,move.endCol)
        pass
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove# switch turn
            # update the king's location
            if (move.pieceMoved == "wK"):
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif (move.pieceMoved == "bK"):
                self.blackKingLocation = (move.startRow, move.startCol)
    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        moves = self.getAllPossibleMoves()
        for i in range(len(moves)-1,-1,-1):#when moving from a list, move backwards a step
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        #generate all the possible moves
        #For each move, make the move
        #Generate all opponent's move
        #For each of those moves, see if they attack your king
        #if they do, its not a valid move
        if(len(moves) == 0):
            if(self.inCheck()):
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.checkMate = False
        return moves
    #determine if the current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
        pass
    #determine if the enemy can attack the square r c
    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if(move.endRow == r and move.endCol == c):
                return True
        return False
    '''
    All moves not considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):#number of rows
            for c in range(len(self.board[r])): # number of columns in given row
                turn = self.board[r][c][0]

                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    print(self.board[r][c][1])
                    self.moveFunctions[piece](r,c,moves)
        return moves
    '''
    Get moves at specified location
    '''
    def getPawnMoves(self,r,c,moves):
        if(self.whiteToMove): #focus on the white pawns
            if self.board[r-1][c] == "--":
                moves.append(Move((r,c),(r-1,c),self.board))
                if(r == 6 and self.board[r-2][c] == "--"):
                    moves.append(Move((r,c),(r-2,c),self.board))
            if( c-1 >= 0):
                if self.board[r-1][c-1][0] == "b":# there is an enemy piece to capture
                    moves.append(Move((r,c),(r-1,c-1),self.board))
            if(c+1 <= 7):
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r,c),(r-1,c+1),self.board))
        else:
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if (r == 1 and self.board[r + 2][c] == "--"):
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if (c - 1 >= 0):
                if self.board[r + 1][c - 1][0] == "w":  # there is an enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if (c + 1 <= 7):
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
#add pawn promotions later
    def getRookMoves(self,r,c,moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else: # friendly piece invalid
                        break
                else:# off board
                    break

        pass
    def getBishopMoves(self,r,c,moves):
        directions = ((-1, 1), (-1, -1), (1, 1), (1, -1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:  # off board
                    break
        pass
    def getKnightMoves(self,r,c,moves):
        directions = ((-2, -1), (2, 1), (-2, 1), (2, -1), (1, 2), (-1, -2), (-1, 2), (1, -2))
        allyColor = "w" if self.whiteToMove else "b"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))
        pass
    def getQueenMoves(self,r,c,moves):
        directions = ((-1, 1), (-1, -1), (1, 1), (1, -1),(-1,0),(0,-1),(1,0),(0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:  # off board
                    break
        pass
    def getKingMoves(self,r,c,moves):
        directions = ((-1, 1), (-1, -1), (1, 1), (1, -1), (-1, 0), (0, -1), (1, 0), (0, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))
        pass


        pass

class Move():
    #map keys to values
    # key : value
    ranksToRow = {"1":7, "2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowsToRanks = {v : k for k, v in ranksToRow.items()}
    filesToCols = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    colsToFiles = {v:k for k,v in filesToCols.items()}
    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
    '''
    Overriding the equals method
    '''
    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        #you can add to make this a real chess notation
        return self.__getRankFile(self.startRow,self.startCol) + self.__getRankFile(self.endRow, self.endCol)
    def __getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
