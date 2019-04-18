# coding: utf-8

from tkinter import *
from time import sleep
from tkinter.messagebox import *

# GAME CONSTANTS
GRID_WIDTH = 9
GRID_HEIGHT = 7

# GRAPHICAL CONSTANTS
RADIUS = 10
XMIN = 40
YMIN = 40
DIST = 40
WIDTH = 2*XMIN + 8*DIST
HEIGHT = 2*YMIN + 6*DIST

# COLORS
free = "white"
P1_selected = "deep sky blue"
P1_linked = "dodger blue"
P2_selected = "tomato"
P2_linked = "red"
colors = {  None: {"free": free},
            1: {"free": free, "selected": P1_selected, "linked": P1_linked},
            2: {"free": free, "selected": P2_selected, "linked": P2_linked}}


class GUI:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

        # Setup the window layout
        self.window = Tk()
        self.controls = Frame(self.window, width = WIDTH)
        self.controls.pack()
        self.currentPlayer = player1
        Label(self.controls, text="Jeu de la saucisse").pack()
        self.P1_label = Label(self.controls, text=player1)
        self.P2_label = Label(self.controls, text=player2)
        self.P1_label.pack(side = LEFT)
        self.P2_label.pack(side = LEFT)
        self.setPlayerLabel()
        # Button(self.controls, text="Quitter", command=self.window.quit).pack(side = RIGHT)

        self.canvas = Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        self.grid = []
        self.points = []

        for i in range(GRID_WIDTH):
            self.grid.append([])
            for j in range(GRID_HEIGHT):
                if (i+j) % 2 == 0:
                    rep = self.canvas.create_oval(XMIN+i*DIST-RADIUS, YMIN+j*DIST-RADIUS, XMIN+i*DIST+RADIUS,YMIN+j*DIST+RADIUS, fill=free)
                    self.grid[i].append(Point_rep(i, j, rep))
                    self.points.append(self.grid[i][j])
                else :
                    self.grid[i].append([])

    def nbCurrentPlayer(self):
        if self.currentPlayer == self.player1:
            return 1
        elif self.currentPlayer == self.player2:
            return 2
        else:
            raise ValueError("Cannot give the number of the current player")

    def setPlayerLabel(self):
        if self.currentPlayer == self.player1 :
            self.P1_label.config(background = P1_selected)
            self.P2_label.config(background = free)
        elif self.currentPlayer == self.player2:
            self.P1_label.config(background = free)
            self.P2_label.config(background = P2_selected)

    def setPointState(self, coords, state):
        """Change point state and set color accordingly"""
        global colors
        print("setPointState called !",self.currentPlayer, coords,state)
        (i,j) = coords
        self.canvas.itemconfig(self.grid[i][j].rep, fill = colors[self.nbCurrentPlayer()][state])

    def wrongSelection(self, coords):
        (i,j) = coords
        rep = self.grid[i][j].rep
        self.canvas.scale(rep, i*DIST+XMIN, j*DIST+YMIN, 1.5, 1.5)
        self.canvas.after(100, lambda : self.canvas.scale(rep, i*DIST+XMIN, j*DIST+YMIN, 1/1.5, 1/1.5))

    def changeCurrentPlayer(self):
        print("change f*cking player")
        """Change the current player to who is the turn"""
        self.currentPlayer = self.player1 if self.currentPlayer == self.player2 else self.player2
        self.setPlayerLabel()

    def endGame(self):
        winner = self.player1 if self.currentPlayer == self.player2 else self.player2
        showinfo("Fin du jeu !", icon="info", message = winner + " a gagné !")
        self.window.destroy()

class Point_rep:
    def __init__(self, i, j, rep):
        self.i = i
        self.j = j
        self.rep = rep

    def change_color(self):
        pass
