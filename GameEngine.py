# coding: utf-8
import numpy as np
from functools import reduce

# GAME CONSTANTS
WIDTH = 7
HEIGHT = 6
VIDE = 0

class GameEngine:
    """Class representing a game"""
    def __init__(self, player1, player2):
        self.grid = np.zeros((7,6), dtype=int)
        self.player1 = player1
        self.player2 = player2
        self.currentPlayer = player1

    def can_place_point(self, i):
        if i >= 0 and i < WIDTH:
            for j in reversed(range(HEIGHT)):
                if self.grid[i][j] == VIDE:
                    return True
        return False

    def nextPlayer(self):
        self.currentPlayer = (self.player1, self.player2)[self.currentPlayer == self.player1]

    def place_jeton(self, i):
        for j in reversed(range(HEIGHT)):
            if self.grid[i][j] == VIDE:
                self.grid[i][j] = self.currentPlayer
                return
        print ("error, use can_place_point before")

    def gameIsOver(self):
        print('winner is : ', self.currentPlayer)

    def checkIfWin(self, L):
        for i in range(0,len(L) - 3):
            if reduce(lambda a,b: a&b, L[i:i+4]) != 0:
                self.gameIsOver()

    def get10value(self, n):
        return int(n == self.currentPlayer)

    def get10grid(self):
        newGrid = np.zeros((WIDTH,HEIGHT), dtype=int)
        for j in range(HEIGHT):
            for i in range(WIDTH):
                newGrid[i][j] = self.get10value(self.grid[i][j])
        return newGrid

    def verifIfThereIsAWinner(self):
        grid2 = self.get10grid()
        L1 = []
        for i in range(WIDTH):
            L1.append(int(''.join(map(str, grid2[i])), 2))
        L2 = []
        for j in range(HEIGHT):
            L2.append(int(''.join(map(str, grid2[:,j])), 2))

        L3 = [L1[i] << i for i in range(len(L1))]
        L4 = [L1[HEIGHT-i] << i for i in range(len(L1))]

        self.checkIfWin(L1)
        self.checkIfWin(L2)
        self.checkIfWin(L3)
        self.checkIfWin(L4)

        self.nextPlayer()

    def printGrid(self):
        for j in range(HEIGHT):
            for i in range(WIDTH):
                print (self.grid[i][j], end=' ')
            print()


Game = GameEngine(2,1)
while True:
    n = int(input())
    if Game.can_place_point(n):
        Game.place_jeton(n)
    else:
        print("Impossible de jouer dans la colonne {}".format(n))
    Game.printGrid()
    Game.verifIfThereIsAWinner()
