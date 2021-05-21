from player import Player
# from board import Board
import random


class IA(Player):

    name = "Berlin"
    gameSize = 5
    no_win = 0
    color = ["black", "white"]
    DEPTH = 1
    turn = 0
    
    #declared here to prevent from initialization at each method calls
    corners = ((0,0), (0,4), (4,0), (4,4))
    borders = ((0,1), (0,2), (0,3), (1,0), (1,4), (2,0), (2,4), (3,0), (3,4), (4,1), (4,2), (4,3))
    centers = ((1,1), (1,2), (1,3), (2,1), (2,3), (3,1), (3,2), (3,3))
    horizontalEntrapmentCoords = ((0,0), (0,1), (0,2), (0,3), (0,4), (4,0), (4,1), (4,2), (4,3), (4,4))
    verticalEntrapmentCoords = ((0,0), (1,0), (2,0), (3,0), (4,0), (0,4), (1,4), (2,4), (3,4), (4,4))


    def __init__(self, position, gameSize):
        Player.__init__(self, position, gameSize)

    def play(self, dethToCover, board, step):
        if step == 0:
            a, b = self.playStep0(board)
            return a, b
        elif step == 1:
            a, b, c, d = self.playStep1(self.clone(board))
            return a, b, c, d

    def playOld(self, board, step):
        if(step == 0):
            for i in range(self.gameSize):
                for j in range(self.gameSize):
                    if(self.canPlayHere(board, step, i, j)):
                        return (i, j)
        if(step == 1):
            for i in range(self.gameSize):
                for j in range(self.gameSize):
                    if(self.canPlayHere(board, step, i, j)):
                        if board[i][j] == self.playerColor:
                            if len(self.getRealsMoves(board, i, j)) > 0:
                                print("ici", i, j, self.getRealsMoves(
                                    board, i, j)[0])
                                (c, d) = self.getRealsMoves(board, i, j)[0]
                                return (i, j, c, d)
        return -1

    def playRandom(self, board, step):
        playable = []
        if(step == 0):
            for i in range(self.gameSize):
                for j in range(self.gameSize):
                    if self.canPlayHere(board, step, i, j):
                        playable.append((i, j))
            choix = playable[random.randint(0, len(playable)-1)]
            return choix[0], choix[1]
        if(step == 1):
            origins = self.getMovingPiece(board, self.playerColor)
            origin = origins[random.randint(0, len(origins)-1)]
            destinations = self.getRealsMoves(board, origin[0], origin[1])
            destination = destinations[random.randint(0, len(destinations)-1)]
            print(origin[0], origin[1], destination[0], destination[1])
            return (origin[0], origin[1], destination[0], destination[1])
        return -1

    # Method called on step of initialisation
    # To ensure our pieces are on the sides (better approach or... maybe not haha)
    def playStep0(self, board):

        self.turn += 1

        if self.turn == 3:
            print(board)

        side = random.randint(0, 3)

        for i in range(self.gameSize):
            for j in range(self.gameSize):
                if self.canPlayHere(board, 0, i, 0):
                    return (i, 0)
                if self.canPlayHere(board, 0, 0, j):
                    return (0, j)
                if self.canPlayHere(board, 0, i, 4):
                    return (i, 4)
                if self.canPlayHere(board, 0, 4, j):
                    return (4, j)

        return self.playRandom(board, 0)

    # Method play called on step of moving pieces based on minimax with alpha beta pruning
    def playStep1(self, board):

        bestMove = None
        bestMoveScore = 0
        possibleBoards = []
        moves = []

        piecesCanMove = self.getMovingPiece(board, self.playerColor)

        for piece in piecesCanMove:
            piecesDestinations = self.getRealsMoves(board, piece[0], piece[1])

            for destination in piecesDestinations:
                move = piece[0], piece[1], destination[0], destination[1], self.playerColor
                moves.append(move)

                newBoard = self.clone(board)
                self.doMove(newBoard, move)
                possibleBoards.append(newBoard)

        bestMove = moves[0]
        bestMoveScore = self.evaluatePosition(
            possibleBoards[0], float('-inf'), float('inf'), self.DEPTH, self.getOpponentColor())

        i = -1
        for aBoard in possibleBoards:
            i += 1

            if i > 1:
                score = self.evaluatePosition(
                    aBoard, float('-inf'), float('inf'), self.DEPTH, self.getOpponentColor())
                if score > bestMoveScore:
                    bestMove = moves[i]
                    bestMoveScore = score

        w, x, y, z, color = bestMove

        return w, x, y, z

    # doMove simulate a movement on the board
    # Its implementation looks like the play method from ia_game_cli.py file with some updates
    def doMove(self, board, move):

        a, b, c, d, playerColor = move

        if self.isPiece(board, a, b) and (c, d) in self.getRealsMoves(board, a, b):

            board[a][b] = None
            board[c][d] = playerColor

            captured = self.hasCaptured(board, c, d, playerColor)
            if len(captured) > 0:
                self.no_win = 0
                for pos in captured:
                    board[pos[0]][pos[1]] = 'None'
            else:
                self.no_win += 1
        return


    # return the score (beta for this IA, alpha for the other IA) of the game at the depth "depth" with the state of board in "board"
    # playerColor indicate the current player (the one who can do some movement)
    def evaluatePosition(self, board, alpha, beta, depth, playerColor):

        if depth == 0:
            evaluation = self.evaluate(board)
            return evaluation

        if playerColor == self.getOpponentColor():
            moves = []
            piecesCanMove = self.getMovingPiece(board, playerColor)
            for piece in piecesCanMove:
                destinations = self.getRealsMoves(board, piece[0], piece[1])

                for destination in destinations:
                    move = piece[0], piece[1], destination[0], destination[1], playerColor
                    moves.append(move)

            newBeta = beta
            for move in moves:
                successorBoard = self.clone(board)
                self.doMove(successorBoard, move)
                newBeta = min(newBeta, self.evaluatePosition(
                    successorBoard, alpha, beta, depth-1, self.playerColor))  
                if newBeta <= alpha:
                    break

            return newBeta
        else:
            moves = []
            piecesCanMove = self.getMovingPiece(board, playerColor)
            for piece in piecesCanMove:
                destinations = self.getRealsMoves(board, piece[0], piece[1])

                for destination in destinations:
                    move = piece[0], piece[1], destination[0], destination[1], playerColor
                    moves.append(move)

            newAlpha = alpha
            for move in moves:
                successorBoard = self.clone(board)
                self.doMove(successorBoard, move)
                newAlpha = max(newAlpha, self.evaluatePosition(
                    successorBoard, alpha, beta, depth - 1, self.getOpponentColor())) 
                if beta <= newAlpha:
                    break

            return newAlpha

    # Return a number which indicates how good is the board for this IA
    # We personnally do a simple difference between scores (but this is the method that must be improved, we think)
    def evaluate(self, board):
        myScore = self.getScore(board, self.getOpponentColor())
        opponentScore = self.getScore(board, self.playerColor)

        return myScore - opponentScore







    # -----------------------------------------------------------
    # Evaluation features  f1...f13                             |
    # -----------------------------------------------------------


    #corner domination
    def f1(self, board):
        opponentColor = self.getOpponentColor()

        #nb pièces de notre joueur
        nbSelf = 0
        #nb pièces adversaire
        nbOpponent = 0
        for corner in self.corners:
            if(board[corner[0]][corner[1]] == self.playerColor):
                nbSelf+=1
            elif(board[corner[0]][corner[1]] == opponentColor):
                nbOpponent+=1
        
        return (nbSelf - nbOpponent)/4

        
    #border domination  
    def f2(self, board):
        opponentColor = self.getOpponentColor()

        nbSelf = 0
        nbOpponent = 0

        for border in self.borders:
            if(board[border[0]][border[1]] == self.playerColor):
                nbSelf+=1
            elif(board[border[0]][border[1]] == opponentColor):
                nbOpponent+=1
        
        return (nbSelf - nbOpponent)/12

    
    #Horizontal clustering for playerColor (f3 for Berlin's color & f5 for his opponent)

    def f3(self, board):
        return self.numberPiecesAdjacentHoriz(board, self.playerColor)/12

    def f5(self, board):
        return self.numberPiecesAdjacentHoriz(board, self.getOpponentColor())/12

    
    #Vertical clustering for playerColor (f4 for Berlin's color & f6 for his opponent)

    def f4(self, board):
        return self.numberPiecesAdjacentVert(board, self.playerColor)/12

    def f6(self, board):
        return self.numberPiecesAdjacentVert(board, self.getOpponentColor())/12


    # Horizontal mass dist
    def f7(self, board):
        return abs(self.horizontalCenterMass(board, self.playerColor) - self.horizontalCenterMass(board, self.getOpponentColor()))/4

    # Vertical mass dist
    def f8(self, board):
        return abs(self.verticalCenterMass(board, self.playerColor) - self.verticalCenterMass(board, self.getOpponentColor()))/4


    #horizontal entrapment
    def f9(self, board):
        opponentColor = self.getOpponentColor()
         
        nbSelf = 0
        nbOpponent = 0

        for square in self.horizontalEntrapmentCoords:
            if(board[square[0]][square[1]] == self.playerColor):
                nbSelf+=1
            elif(board[square[0]][square[1]] == opponentColor):
                nbOpponent+=1
        return (nbSelf - nbOpponent)/10

    #vertical entrapment
    def f10(self, board):
        opponentColor = self.getOpponentColor()
         
        nbSelf = 0
        nbOpponent = 0

        for square in self.verticalEntrapmentCoords:
            if(board[square[0]][square[1]] == self.playerColor):
                nbSelf+=1
            elif(board[square[0]][square[1]] == opponentColor):
                nbOpponent+=1
        return (nbSelf - nbOpponent)/10

    # Counts number of Berlin's pieces vs. his opponent
    def f11(self, board):
        return (self.countPieces(board, self.playerColor) - self.countPieces(board, self.getOpponentColor()))/11


    #phase two starts
    #how many captures Black (us) will make on the first move in phase one
    def f12(self, board):  #on passe le board du début de la phase 2
        captured = 0
        #Récupérer les pièces qui peuvent bouger.
        piecesCanMove = self.getMovingPiece(board, self.playerColor)

        #Si aucune, (donc aucune au bord du centre) donc aucun gain possible
        #sinon calculer le gain possible
        if(len(piecesCanMove) == 0):
            for piece in piecesCanMove:
                piecesDestinations = self.getRealsMoves(board, piece[0], piece[1])

                for destination in piecesDestinations:

                    newBoard = self.clone(board)
                    move = piece[0], piece[1], destination[0], destination[1], self.playerColor

                    result = self.doMoveForF12(newBoard, move)
                    if(result > captured):
                        captured = result
        return captured

    #black can start
    #returns 0 if the four squares around the middle square are occupied 
    #by White (i.e. Black cannot make the first move), and
    #returns 1 otherwise.
    def f13(self):
        if(self.playerColor in self.centers):
            return 1
        else:
            return 0







    # -----------------------------------------------------------
    # Helpers functions                                         |
    # -----------------------------------------------------------


    def numberPiecesAdjacentHoriz(self, board, playerColor):
        numberHorizontallyAdjacent = 0
        for i in range(self.gameSize):
            for j in range(self.gameSize):
                if board[i][j] == playerColor:
                    #Si la pièce courante est notre et a une voisine notre à gauche ou à droite
                    if 0 <= i-1 < self.gameSize:
                        if board[i-1][j] == playerColor:
                            numberHorizontallyAdjacent += 1
                    elif 0 <= i+1 < self.gameSize:
                        if board[i+1][j] == playerColor:
                             numberHorizontallyAdjacent += 1

        return  numberHorizontallyAdjacent

    def numberPiecesAdjacentVert(self, board, playerColor):
        numberVerticallyAdjacent = 0
        for i in range(self.gameSize):
            for j in range(self.gameSize):
                if board[i][j] == playerColor:
                    #Si la pièce courante est notre et a une voisine en haut ou en bas
                    if 0 <= j-1 < self.gameSize:
                        if board[i][j-1] == playerColor:
                            numberVerticallyAdjacent += 1
                    elif 0 <= j+1 < self.gameSize:
                        if board[i][j+1] == playerColor:
                             numberVerticallyAdjacent += 1

        return  numberVerticallyAdjacent

    def horizontalCenterMass(self, board, playerColor):
        totalWeight = 0
        totalX = 0
        for i in range(self.gameSize):
            for j in range(self.gameSize):
                if(board[i][j] == playerColor):
                    totalX += j
                    totalWeight += 1

        return totalX/totalWeight 

    def verticalCenterMass(self, board, playerColor):
        totalWeight = 0
        totalY = 0
        for i in range(self.gameSize):
            for j in range(self.gameSize):
                if(board[i][j] == playerColor):
                    totalY += i
                    totalWeight += 1

        return totalY/totalWeight 
             

    def getOpponentColor(self):
        return self.color[(self.position+1) % 2]

    # playColor est ici la couleur de l'adversaire
    def getScore(self, board, playerColor):
        score = 0
        nbPiecesRestantes = 0
        for i in range(self.gameSize):
            for j in range(self.gameSize):
                if board[i][j] == playerColor:
                    nbPiecesRestantes += 1

        score = 12 - nbPiecesRestantes

        return score
    
    # count the number of pieces of a given color (playerColor)
    def countPieces(self, board, color): 
        nbPieces = 0
        for i in range(self.gameSize):
            for j in range(self.gameSize):
                if board[i][j] == color:
                    nbPieces += 1

        return nbPieces   

    #Move piece for f12 function
    def doMoveForF12(self, board, move):

        a, b, c, d, playerColor = move

        if self.isPiece(board, a, b) and (c, d) in self.getRealsMoves(board, a, b):

            board[a][b] = None
            board[c][d] = playerColor

            captured = self.hasCaptured(board, c, d, playerColor)
        
        return captured
