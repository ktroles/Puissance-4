# coding: utf-8

from tkinter import *
from time import sleep
from tkinter.messagebox import *

# GAME CONSTANTS
GRID_WIDTH = 7
GRID_HEIGHT = 6

# GRAPHICAL CONSTANTS
RADIUS = 20
XMIN = 2*RADIUS
YMIN = 2*RADIUS
DIST = 2.8*RADIUS
WIDTH = 2*XMIN + (GRID_WIDTH-1)*DIST
HEIGHT = 2*YMIN + (GRID_HEIGHT-1)*DIST

class GUI:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.colors = {"bg": "#0652DD", "free": "white", player1:"#FFC312", player2:"#EA2027"}

        # Setup the window layout
        self.window = Tk()
        self.controls = Frame(self.window, width = WIDTH)
        self.controls.pack()
        self.currentPlayer = player1
        Label(self.controls, text="Puissance 4").pack()
        self.P1_label = Label(self.controls, text=player1)
        self.P2_label = Label(self.controls, text=player2)
        self.P1_label.pack(side = LEFT)
        self.P2_label.pack(side = RIGHT)
        self.setPlayerLabel()

        self.canvas = Canvas(self.window, width=WIDTH, height=HEIGHT,bg = self.colors["bg"])
        self.canvas.pack()

        self.grid = []
        self.points = []

        for i in range(GRID_WIDTH):
            self.grid.append([])
            for j in range(GRID_HEIGHT):
                    rep = self.canvas.create_oval(XMIN+i*DIST-RADIUS, YMIN+j*DIST-RADIUS, XMIN+i*DIST+RADIUS,YMIN+j*DIST+RADIUS, fill=self.colors["free"], outline = self.colors["bg"])
                    self.grid[i].append(Point_rep(i, j, rep))
                    self.points.append(self.grid[i][j])


    def nbCurrentPlayer(self):
        if self.currentPlayer == self.player1:
            return 1
        elif self.currentPlayer == self.player2:
            return 2

    def setPlayerLabel(self):
        if self.currentPlayer == self.player1 :
            self.P1_label.config(background = self.colors[self.player1])
            self.P2_label.config(background = self.colors["free"])
        elif self.currentPlayer == self.player2:
            self.P1_label.config(background = self.colors["free"])
            self.P2_label.config(background = self.colors[self.player2])

    def placePoint(self,column):
        j = GRID_HEIGHT
        for j in reversed(range(GRID_HEIGHT)):
            if self.canvas.itemconfig(self.grid[column][j].rep)["fill"][-1] == self.colors["free"]:
                self.canvas.itemconfig(self.grid[column][j].rep, fill = self.colors[self.currentPlayer])
                return


    def wrongSelection(self, coords):
        (i,j) = coords
        rep = self.grid[i][j].rep
        self.canvas.scale(rep, i*DIST+XMIN, j*DIST+YMIN, 1.5, 1.5)
        self.canvas.after(100, lambda : self.canvas.scale(rep, i*DIST+XMIN, j*DIST+YMIN, 1/1.5, 1/1.5))

    def changeCurrentPlayer(self):
        """Change the current player to who is the turn"""
        self.currentPlayer = self.player1 if self.currentPlayer == self.player2 else self.player2
        self.setPlayerLabel()

    def endGame(self, equality = False):
        if equality:
            showinfo("Egalité", icon="info", message = "Votre score reste inchangé !")
        else:
            showinfo("Fin du jeu", icon="info", message = self.currentPlayer + " a gagné !")

        self.window.destroy()

class Point_rep:
    def __init__(self, i, j, rep):
        self.i = i
        self.j = j
        self.rep = rep

if __name__ == '__main__':
    gui = GUI("Fabien", "Killian")
    gui.window.mainloop()
