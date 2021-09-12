'''
GameState
'''

import pygame as p
import os
from chessGamePrototype.Chess import ChessEngine
p.init()
WIDTH = HEIGHT = 512 # 400 is another good option
DIMENSION = 8 # dimensions of chess boards are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # for animations later on
IMAGES = {}

'''
load images will initialize a global dictionary of images, will
be called exactly once, in the main
'''
def loadImages():
    pieces = ["wR","bR","wP","bP","wQ","bQ","wB","bB","bK","wK","bN","wN"]
    print(os.listdir())
    for piece in pieces:
        print(piece);

        IMAGES[piece] = p.transform.scale(p.image.load("Chess/ChessImages/"+ piece +".png"), (SQ_SIZE,SQ_SIZE))
    #we can access an image by accessing the dictionary by saying IMAGES["wP"] for example
#The main driver for our code, this iwll handle user input and updating the graphics

def main():
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # flag variable for when a move is made
    loadImages() # Only do this once, before the while loop
    running = True
    sqSelected = () # no square is selected initially, keeps track of htel ast click of the user(tuple :: row, col)
    playerClicks = [] #keep track of the player's clicks, ex [[6,4],[1,2]]

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()#x y of the mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                if sqSelected == (row, col): #the user clicked the same square twice, undo
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)# append for both 1st and 2nd clicks
                if(len(playerClicks) == 2):
                    move = ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                    print(move.getChessNotation())
                    if(move in validMoves):
                        moveMade = True
                        gs.makeMove(move)
                        sqSelected = () #reset user clicks
                        playerClicks = []
                    else:
                        playerClicks = [sqSelected]
                    pass
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(screen,gs)
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Responsible for all the graphics within the current game state
'''
def drawGameState(screen,gs):
    drawBoard(screen)#draw the squares on the board
    #add in piece highlighting, move suggestions
    drawPieces(screen,gs.board)#draw the pieces ontop of the squares
'''
Draw the squares on hte board, the top left square is always light.
'''
def drawBoard(screen,colors = [p.Color("white"),p.Color("gray")]):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            color = colors[(i+j)%2]
            p.draw.rect(screen, color, p.Rect(i*SQ_SIZE,j*SQ_SIZE,SQ_SIZE,SQ_SIZE))


'''
Draw the pieces on the board
'''
def drawPieces(screen,board):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = board[i][j]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(j*SQ_SIZE,i*SQ_SIZE,SQ_SIZE,SQ_SIZE))

if __name__ == "__main__":
    main()







