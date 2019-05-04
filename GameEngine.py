# coding: utf-8
import numpy as np
from functools import reduce

# GAME CONSTANTS
WIDTH = 7
HEIGHT = 6
VIDE = ''

class GameEngine:
    """Class representing a game"""
    def __init__(self, player1, player2):
        self.grid = np.zeros((WIDTH,HEIGHT), dtype="<U16")
        self.player1 = player1
        self.player2 = player2
        self.currentPlayer = player1

    def canPlaceToken(self, i):
        """Check if place is available in the selected column"""
        if i >= 0 and i < WIDTH:
            for j in reversed(range(HEIGHT)):
                if self.grid[i][j] == VIDE:
                    return j
        return False

    def nextPlayer(self):
        self.currentPlayer = (self.player1, self.player2)[self.currentPlayer == self.player1]

    def placeToken(self, i):
        """Place the token into the grid"""
        for j in reversed(range(HEIGHT)):
            if self.grid[i][j] == VIDE:
                self.grid[i][j] = self.currentPlayer
                return
        print ("error, use canPlaceToken before")

    def gameIsOver(self):
        print('winner is : ', self.currentPlayer)

    def checkIf4InARow(self, L):
        """Check if it is a 4 in a row vertically, horizontally, or diagonally"""
        for i in range(0,len(L) - 3):
            if reduce(lambda a,b: a&b, L[i:i+4]) != 0:
                return True
        return False

    def get10Value(self, n):
        """Return 1 if it is the currentPlayer's token
        Return 0 otherwise"""
        return int(n == self.currentPlayer)

    def get10Grid(self):
        """Return a grid of 1 (currentPlayer's tokens)
        and 0 (opponent's tokens or free points)"""
        newGrid = np.zeros((WIDTH,HEIGHT), dtype=int)
        for j in range(HEIGHT):
            for i in range(WIDTH):
                newGrid[i][j] = self.get10Value(self.grid[i][j])
        return newGrid

    def remainingPoints(self):
        """Check if some points still be playable (free)
        Thus, check if game is finished or not"""
        for i in range(WIDTH):
            if self.grid[i][0] == VIDE:
                return True
        return False

    def checkIfWinner(self):
        """Check if the the currentPlayer has won"""
        grid2 = self.get10Grid()
        L1 = []
        for i in range(WIDTH):
            L1.append(int(''.join(map(str, grid2[i])), 2))
        L2 = []
        for j in range(HEIGHT):
            L2.append(int(''.join(map(str, grid2[:,j])), 2))

        L3 = [L1[i] << i for i in range(len(L1))]
        L4 = [L1[HEIGHT-i] << i for i in range(len(L1))]

        if (self.checkIf4InARow(L1) or self.checkIf4InARow(L2) or self.checkIf4InARow(L3) or self.checkIf4InARow(L4)):
            return True
        else:
            self.nextPlayer()
            return False

    def printGrid(self):
        for j in range(HEIGHT):
            for i in range(WIDTH):
                if self.grid[i][j] == VIDE:
                    print(".", end=' ')
                else:
                    print (self.grid[i][j], end=' ')
            print()


if __name__ == "__main__":
    Game = GameEngine("abc","def")
    while True:
        n = int(input())
        if Game.canPlaceToken(n):
            Game.placeToken(n)
        else:
            print("Impossible de jouer dans la colonne {}".format(n))
        Game.printGrid()
        if Game.checkIfWinner():
            Game.gameIsOver()
