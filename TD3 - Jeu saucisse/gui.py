from tkinter import *

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
    def __init__(self, window, player1, player2):
        self.game = game

        # Setup the window layout
        self.controls = Frame(window, width = WIDTH)
        self.controls.pack()
        self.currentPlayer = player
        Label(self.controls, text="     Jeu de la saucisse     ").pack()
        self.P1_label = Label(self.controls, text=player1)
        self.P2_label = Label(self.controls, text=player2)
        self.P1_label.pack(side = LEFT)
        self.P2_label.pack(side = LEFT)
        self.setPlayerLabel()
        Button(self.controls, text="Quitter", command=window.quit).pack(side = RIGHT)

        self.canvas = Canvas(window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        self.points = []

        for i in range(GRID_WIDTH):
            for j in range(GRID_HEIGHT):
                if (i+j) % 2 == 0:
                    rep = self.canvas.create_oval(XMIN+i*DIST-RADIUS, YMIN+j*DIST-RADIUS, XMIN+i*DIST+RADIUS,YMIN+j*DIST+RADIUS, fill=free)
                    self.points.append(Point_rep(i, j, rep))


        self.canvas.bind("<Button-1>", self.click)

    def setPlayerLabel(self):
        if self.game.currentPlayer == 1:
            self.P1_label.config(background = P1_selected)
            self.P2_label.config(background = free)
        else:
            self.P1_label.config(background = free)
            self.P2_label.config(background = P2_selected)

    def click(self, event):
        (x,y) = event.x, event.y
        a = self.canvas.find_overlapping(x, y, x, y)
        if len(a) == 1:
            rep = a[0]
            for point in self.points:
                if point.rep == rep:
                    return (point.i, point.j)

class Point_rep:
    def __init__(self, i, j, rep):
        self.i = i
        self.j = j
        self.rep = rep
