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
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {"P":self.getPawnMoves,"R":self.getRookMoves,"N":self.getKnightMoves,
                              "B":self.getBishopMoves,"Q":self.getQueenMoves,"K":self.getKingMoves}
        self.getValidMoves = {"Naive":self.naiveAlgorithm,"Advanced":self.advancedAlgorithm}
        self.whiteToMove = True
        self.moveLog = []
        self.enpassantLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.inCheck = False
        self.checkMate = False
        self.staleMate = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = () #coordinates for thes quare where an en passant capture is possible
        self.enpassantLog = []
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)]
    '''
    takes a move as a parameter and executes it,
    this will not work for castling, promotion and/or en passant'''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)#log the move so we can undo it later
        self.enpassantLog.append(self.enpassantPossible)
        self.whiteToMove = not self.whiteToMove
        #update the king's location
        if(move.pieceMoved == "wK"):
            self.whiteKingLocation = (move.endRow,move.endCol)
        elif(move.pieceMoved == "bK"):
            self.blackKingLocation = (move.endRow,move.endCol)
        #pawn promotion
        if (move.isPawnPromotion):
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] +"Q"
        #enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"
        #update enpassantpossible variable
        if move.pieceMoved[1] == "P" and abs(move.startRow-move.endRow) ==2:
            self.enpassantPossible = ((move.startRow+move.endRow)//2,move.startCol)
        else:
            self.enpassantPossible = ()
        #castle move
        if (move.isCastleMove):
            if (move.endCol - move.startCol == 2):#king side castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol + 1] = "--"
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"
                pass
        #update the castling rights whenever its a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
        #for i in self.castleRightsLog:
            #print(f"({i.wks},{i.wqs},{i.bks},{i.bqs})",end="")
        #print("\n")


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
            #undo en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            ##undo two square pawn advance
            #if move.pieceMoved[1] == "P" and abs(move.startRow-move.endRow) == 2:
            #    self.enpassantPossible = ()
            self.enpassantLog.pop()
            self.enpassantPossible = self.enpassantLog[-1]
            self.castleRightsLog.pop() #get rid of new castlerisghts from the move we are undoing
            self.currentCastlingRight = CastleRights(self.castleRightsLog[-1].wks,self.castleRightsLog[-1].bks,self.castleRightsLog[-1].wqs,self.castleRightsLog[-1].bqs)
            #undo castle move
            if (move.isCastleMove):
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"
            self.checkMate = False
            self.staleMate = False
    '''
    update the castle rights given the move
    '''
    def updateCastleRights(self,move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wqs = False
            self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bqs = False
            self.currentCastlingRight.bks = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False
        # if a rook is captured
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if (move.endCol == 0):
                    self.currentCastlingRight.wqs = False
                elif (move.endCol == 7):
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if (move.endCol == 0):
                    self.currentCastlingRight.bqs = False
                elif(move.endCol == 7):
                    self.currentCastlingRight.bks = False
    '''
    All moves considering checks
    '''
    def advancedAlgorithm(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForValidPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if (len(self.checks) == 1):
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow,checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow,kingCol,moves)
        else:
            moves = self.getAllPossibleMoves()
        if (self.whiteToMove):
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves,"w")
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves,"b")
        if (len(moves) == 0):
            if (self.InCheck()):
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
        return moves


        pass

    def naiveAlgorithm(self):
        tempEnpassantPossible = self.enpassantPossible
        moves = self.getAllPossibleMoves()
        for i in range(len(moves)-1,-1,-1):#when moving from a list, move backwards a step
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.InCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        #generate all the possible moves
        #For each move, make the move
        #Generate all opponent's move
        #For each of those moves, see if they attack your king
        #if they do, its not a valid move
        if(len(moves) == 0):
            if(self.InCheck()):
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
        self.enpassantPossible = tempEnpassantPossible
        return moves

    def checkForValidPinsAndChecks(self):
        pins =[]
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 1), (-1, -1), (1, 1), (1, -1),(-1,0),(0,-1),(1,0),(0,1))
        for i in range(len(directions)):
            d = directions[i]
            possiblePin = ()
            for j in range(1,8):
                endRow = startRow + d[0] * j
                endCol = startCol + d[1] * j
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == () :
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:#2nd pinned piece, no possible checks or pin
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        #1. Orthogonally away
                        #2.Diagonally away
                        #3. 1 Square away
                        #4 any direction infinite range
                        #5 any direction one square away
                        if (0<= i <= 3 and type == "B") or \
                            (4 <= i <= 7 and type == "R") or \
                                (j == 1 and type == "P" and ((enemyColor == "b" and 0 <= i <= 1) or (enemyColor == "w" and 2 <= i <= 3))) or \
                                (type == "Q") or (j == 1 and type == "K"):
                            if(possiblePin == ()):
                                inCheck = True
                                checks.append((endRow,endCol, d[0], d[1]))
                                break
                            else:# piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: #enemy piece not applying check
                            break
                else:# off board
                    break
        #check for knight moves
        knightMoves = ((-2, -1), (-2, 1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N": #enemy knight attacking king
                    inCheck = True
                    checks.append((endRow,endCol,m[0],m[1]))
        return inCheck,pins, checks

    #determine if the current player is in check
    def InCheck(self):
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
                    self.moveFunctions[piece](r,c,moves)
        return moves
    '''
    Get moves at specified location
    '''
    def getPawnMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = "b"
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = "w"
            kingRow, kingCol = self.blackKingLocation
        if self.board[r+moveAmount][c] == "--":#1 square move
            if not piecePinned or pinDirection == (moveAmount,0):
                moves.append(Move((r,c),(r+moveAmount,c),self.board))
                if r == startRow and self.board[r+2*moveAmount][c] == "--":#2 square moves
                    moves.append(Move((r,c),(r+2*moveAmount,c),self.board))
        if (c-1 >=0):
            if not piecePinned or pinDirection == (moveAmount,-1):
                if self.board[r+moveAmount][c-1][0] == enemyColor:
                    moves.append(Move((r,c),(r+moveAmount,c-1),self.board))
                if (r + moveAmount,c-1)== self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c: # king is left of the pawn
                            #inside between the king and the pawn, outside range between the pawn adn the border
                            insideRange = range(kingCol+1,c-1)
                            outsideRange = range(c+1,len(self.board))
                        else:
                            insideRange = range(kingCol -1, c,-1)
                            outsideRange = range(c-2,-1,-1)
                        for i in insideRange:
                            if self.board[r][i] != "--":#some other piece beside the en passant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):#attacking piece
                                attackingPiece = True
                                break
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r,c),(r+moveAmount,c-1),self.board,isEnpassantMove=True))
        if (c+1 <=7):# capture to the right
            if not piecePinned or pinDirection == (moveAmount,+1):
                if self.board[r+moveAmount][c+1][0] == enemyColor:
                    moves.append(Move((r,c),(r+moveAmount,c+1),self.board))
                if (r + moveAmount,c+1)== self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:  # king is left of the pawn
                            # inside between the king and the pawn, outside range between the pawn adn the border
                            insideRange = range(kingCol + 1, c)
                            outsideRange = range(c + 2, len(self.board))
                        else:
                            insideRange = range(kingCol - 1, c + 1, -1)
                            outsideRange = range(c - 1, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--":  # some other piece beside the en passant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):  # attacking piece
                                attackingPiece = True
                                break
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r,c),(r+moveAmount,c+1),self.board,isEnpassantMove=True))


        '''
        if (self.whiteToMove):  # focus on the white pawns
            if self.board[r - 1][c] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if (r == 6 and self.board[r - 2][c] == "--"):
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if (c - 1 >= 0):  # capture to the left
                if self.board[r - 1][c - 1][0] == "b":  # there is an enemy piece to capture
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if (c + 1 <= 7):  # capture to the right
                if self.board[r - 1][c + 1][0] == "b":
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))
        if(self.whiteToMove): #focus on the white pawns
            if self.board[r-1][c] == "--":
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r,c),(r-1,c),self.board))
                    if(r == 6 and self.board[r-2][c] == "--"):
                        moves.append(Move((r,c),(r-2,c),self.board))
            if( c-1 >= 0):#capture to the left
                if self.board[r-1][c-1][0] == "b":# there is an enemy piece to capture
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append(Move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board,isEnpassantMove=True))
            if(c+1 <= 7):#capture to the right
                if self.board[r-1][c+1][0] == "b":
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board,isEnpassantMove=True))
        else:
            if self.board[r + 1][c] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if (r == 1 and self.board[r + 2][c] == "--"):
                        moves.append(Move((r, c), (r + 2, c), self.board))

            if (c - 1 >= 0):#capture to the left
                if self.board[r + 1][c - 1][0] == "w":  # there is an enemy piece to capture
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1,c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board,isEnpassantMove=True))
            if (c + 1 <= 7):#capture to the right
                if self.board[r + 1][c + 1][0] == "w":
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r+1,c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board,isEnpassantMove=True))
        '''
#add pawn promotions later
    def getRookMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])#can't remove queen from pin on rook move, only remove it on bishop moves
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1,0),(0,-1),(1,0),(0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
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
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])  # can't remove queen from pin on rook move, only remove it on bishop moves
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, 1), (-1, -1), (1, 1), (1, -1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
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
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-2, -1), (2, 1), (-2, 1), (2, -1), (1, 2), (-1, -2), (-1, 2), (1, -2))
        allyColor = "w" if self.whiteToMove else "b"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
        pass
    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)
        pass
    def getKingMoves(self,r,c,moves):
        rowMoves = (-1,-1,-1,0,0,1,1,1)
        colMoves = (-1,0,1,-1,1,-1,0,1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow,endCol)
                    else:
                        self.blackKingLocation = (endRow,endCol)
                    inCheck,pins,checks = self.checkForValidPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    if allyColor == "w":
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)

    '''
    Generate caslting moves
    '''
    def getCastleMoves(self,r,c,moves,allyColor):
        if(self.squareUnderAttack(r,c)):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or(not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(r,c,moves,allyColor)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or(not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(r,c,moves,allyColor)

    def getKingSideCastleMoves(self,r,c,moves,allyColor):
        if(self.board[r][c+1] == "--" and self.board[r][c+2] == "--"):
            if (not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2)):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove = True))
    def getQueenSideCastleMoves(self,r,c,moves,allyColor):
        if (self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--"):
            if (not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2)):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))
        #for d in directions:
        #    endRow = r + d[0]
        #    endCol = c + d[1]
        #    if 0 <= endRow < 8 and 0 <= endCol < 8:
        #        endPiece = self.board[endRow][endCol]
        #        if endPiece != allyColor:
        #            moves.append(Move((r, c), (endRow, endCol), self.board))
        pass


        pass
class CastleRights():
    def __init__(self, wks,bks,wqs,bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    #map keys to values
    # key : value
    ranksToRow = {"1":7, "2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowsToRanks = {v : k for k, v in ranksToRow.items()}
    filesToCols = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    colsToFiles = {v:k for k,v in filesToCols.items()}
    def __init__(self, startSq, endSq, board, isEnpassantMove = False,isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isEnpassantMove = isEnpassantMove
        #Pawn promotion
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0)or(self.pieceMoved == "bP" and self.endRow ==7 )
        #En passant
        if (self.isEnpassantMove):
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        # is castle move
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != "--"
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    '''
    Overriding the equals method
    '''
    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID == other.moveID
        return False
    #overriding the str() function
    def __str__(self):
        #castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
        endSquare = self.__getRankFile(self.endRow,self.endCol)
        #pawn moves
        if self.pieceMoved[1] == "P":
            if (self.isCapture):
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare
        #Pawn promotions
        #two of the same type of piece moving to a square, Nbd2 if both knights can move to d2
        #adding + for a check move and # for a checkmate move
        #piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare

    def getChessNotation(self):
        #you can add to make this a real chess notation
        return self.__getRankFile(self.startRow,self.startCol) + self.__getRankFile(self.endRow, self.endCol)
    def __getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

'''
UI improvements:
-Menu to select AI/Human
-Flip board options (display from black perspective)
-Change color of board/pieces - different piece skins
-Mouse click/drag for pieces

Engine improvements:
-Add 50 move draw and 3 move repeating draw rule
-Move ordering - look at checks, captures and threats first, prioritize castling/king safety, look at pawn moves last (this will improve alpha-beta pruning). Also start with moves that previously scored higher (will also improve pruning).
-Calculate both players moves given a position
-Change move calculation to make it more efficient. Instead of recalculating all moves, start with moves from previous board and change based on last move made
-Use a numpy array instead of 2d list of strings or store the board differently (maybe with bit boards: https://www.chessprogramming.org/Bitb...
)
-Hash board positions already visited to improve computation time for transpositions. (https://en.wikipedia.org/wiki/Zobrist...
)
-If move is a capture move, even at max depth, continue evaluating until no captures remain (https://www.chessprogramming.org/Quie...
)
'''
