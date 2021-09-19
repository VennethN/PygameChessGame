'''
GameState
'''

import pygame as p
import os
from multiprocessing import Process, Queue

print(os.listdir())
from chessGamePrototype.Chess import ChessEngine, ChessAI

p.init()
BOARD_WIDTH = BOARD_HEIGHT = 512  # 400 is another good
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # dimensions of chess boards are 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15  # for animations later on
IMAGES = {}
SOUNDS = {}

'''
load images will initialize a global dictionary of images, will
be called exactly once, in the main
'''


def loadImages():
    pieces = ["wR", "bR", "wP", "bP", "wQ", "bQ", "wB", "bB", "bK", "wK", "bN", "wN"]
    sounds = ["PieceMoved", "PieceCaptured", "Castling", "Check"]
    print(os.listdir())
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/ChessImages/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    for sound in sounds:
        SOUNDS[sound] = p.mixer.Sound("Chess/ChessSounds/" + sound + ".mp3")
    # we can access an image by accessing the dictionary by saying IMAGES["wP"] for example


# The main driver for our code, this iwll handle user input and updating the graphics

def main():
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    moveLogFont = p.font.SysFont("Arial", 12, False, False)
    validMoves = gs.getValidMoves["Advanced"]()
    moveMade = False  # flag variable for when a move is made
    animate = False  # Flag variable for enabling animation or not
    loadImages()  # Only do this once, before the while loop
    running = True
    sqSelected = ()  # no square is` selected initially, keeps track of htel ast click of the user(tuple :: row, col)
    playerClicks = []  # keep track of the player's clicks, ex [[6,4],[1,2]]
    gameOver = False
    playerOne = True  # if a human is playing white,  then this will be true
    playerTwo = False  # if a human is ......-
    playedMove = None
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if gameOver != True:
                    location = p.mouse.get_pos()  # x y of the mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8:  # the user clicked the same square twice, undo
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append for both 1st and 2nd clicks
                    if (len(playerClicks) == 2) and humanTurn:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if (move == validMoves[i]):
                                moveMade = True
                                playedMove = validMoves[i]
                                gs.makeMove(playedMove)
                                sqSelected = ()  # reset user clicks
                                playerClicks = []
                                animateMove(gs.moveLog[-1], screen, gs.board, clock)
                        if not moveMade:
                            playerClicks = [sqSelected]
                    pass
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo move
                    gs.undoMove()
                    moveMade = True
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:  # reset the board
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves["Advanced"]()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
        # AI move finder logic
        if (not gameOver and not humanTurn and not moveUndone):
            if not AIThinking:
                AIThinking = True
                print("thinking...")
                returnQueue = Queue()#used to pass data between threads
                moveFinderProcess = Process(target=ChessAI.moveAlgorithm["NegaMax"], args=(gs,validMoves,3, returnQueue))
                moveFinderProcess.start() # call the threads with defined parameters
                # AIMove = ChessAI.moveAlgorithm["MinMax"](gs,validMoves,2)
                #AIMove = ChessAI.moveAlgorithm["NegaMax"](gs, validMoves, 3)
                # AIMove = ChessAI.moveAlgorithm["Greedy"](gs,validMoves)
                # AIMove = ChessAI.moveAlgorithm["Random"](validMoves)

            if not moveFinderProcess.is_alive():
                print("Done thinking")
                AIMove = returnQueue.get()
                if AIMove == None:
                    AIMove = ChessAI.moveAlgorithm["Random"](validMoves)
                playedMove = AIMove
                gs.makeMove(playedMove)
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
                moveMade = True
                print("finished")
                AIThinking = False

        if moveMade:
            validMoves = gs.getValidMoves["Advanced"]()
            playValidSounds(playedMove, gs)
            moveMade = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)
        if (gs.checkMate or gs.staleMate):
            gameOver = True
            drawEndGameText(screen, "Stalemate" if gs.staleMate else "Black wins by checkmate" if gs.whiteToMove else "White wins by checkmate")
        else:
            gameOver = False
        clock.tick(MAX_FPS)
        p.display.flip()


'''
Responsible for all the graphics within the current game state
'''


def drawGameState(screen, gs, validMoves, squareSelected, moveLogFont):
    drawBoard(screen)  # draw the squares on the board
    highlightSquares(screen, gs, validMoves, squareSelected)
    drawPieces(screen, gs.board)  # draw the pieces ontop of the squares
    drawMoveLog(screen, gs, moveLogFont)


'''
highlight the square selected an the moves for the pieces selected
'''
'''
Draw the squares on the board, the top left square is always light.
'''


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            color = colors[(i + j) % 2]
            p.draw.rect(screen, color, p.Rect(i * SQ_SIZE, j * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, validMoves, sqSelected):
    if (sqSelected != ()):
        r, c = sqSelected
        if (gs.board[r][c][0] == ("w" if gs.whiteToMove else "b")):  # double if statement, makes sure that sqselected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value, if 0 its transparent, if its 255 its opaque(solid)
            s.fill(p.Color('blue'))  # set the fill of s
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
            pass
    pass


def playValidSounds(move, gs):
    if move == None:
        return
    SOUNDS["PieceMoved"].play()
    if (move.isCastleMove):
        SOUNDS["Castling"].play()
    if (move.pieceCaptured != "--"):
        SOUNDS["PieceCaptured"].play()
    if (gs.inCheck):
        SOUNDS["Check"].play()


'''
Draw the pieces on the board
'''


def drawPieces(screen, board):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = board[i][j]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(j * SQ_SIZE, i * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draw the move log
'''


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + "." + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):  # makes sure black makes a move
            moveString += str(moveLog[i + 1]) + "  "
        moveTexts.append(moveString)
    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]
        textObject = font.render(text, True, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

    '''
    animating a move
    '''


def animateMove(move, screen, board, clock):
    global colors
    dr = move.endRow - move.startRow
    dc = move.endCol - move.startCol
    framesPerSquare = 6  # frames to move one square of the animation
    frameCount = (abs(dr) + abs(dc)) * framesPerSquare
    fps = 60
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dr * frame / frameCount, move.startCol + dc * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw the captured piece onto rectangle
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == "b" else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        if move.pieceMoved != "--":
            screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(fps)


'''`
Draw texts
'''


def drawEndGameText(screen, text):
    font = p.font.SysFont("Arial", 32, True, False)
    textObject = font.render(text, 0, p.Color('Grey'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))


# rules for castling
# 1 the square needs to be clear
# 2 the squares cannot be under attack, the king cannot be in check
# 3 it must be the king and  the rook's first move in the game
if __name__ == "__main__":
    main()
