from tkinter import *
from tkinter.messagebox import *

# CONSTANTS
RADIUS = 10
XMIN = 40
YMIN = 40
DIST = 40
WIDTH = 2*XMIN + 8*DIST
HEIGHT = 2*YMIN + 6*DIST

#colors
free = "white"
P1_selected = "deep sky blue"
P1_linked = "dodger blue"
P2_selected = "tomato"
P2_linked = "red"
colors = {  None: {"free": free},
            1: {"free": free, "selected": P1_selected, "linked": P1_linked},
            2:{"free":free, "selected": P2_selected, "linked": P2_linked}}

window = Tk()

class Jeu:
    def __init__(self, window, firstPlayer):
        # Setup the window layout
        self.controls = Frame(window, width = WIDTH)
        self.controls.pack()
        self.currentPlayer = firstPlayer
        Label(self.controls, text="     Jeu de la saucisse - Mode local     ").pack()
        self.P1_label = Label(self.controls, text="Joueur 1")
        self.P2_label = Label(self.controls, text="Joueur 2")
        self.P1_label.pack(side = LEFT)
        self.P2_label.pack(side = LEFT)
        self.setPlayerLabel()
        Button(self.controls, text="Quitter", command=window.quit).pack(side = RIGHT)

        self.canvas = Canvas(window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<<EndTurn>>", self.endTurn)

        # Setup the grid and create the 32 points
        self.grid = list()
        for i in range(9):
            self.grid.append(list())
            for j in range(7):
                if (i+j) % 2 == 0:
                    self.grid[i].append(Point(i, j))
                    self.grid[i][j].rep = self.canvas.create_oval(XMIN+i*DIST-RADIUS, YMIN+j*DIST-RADIUS,
                                                    XMIN+i*DIST+RADIUS,YMIN+j*DIST+RADIUS, fill=free)
                else:
                    self.grid[i].append(Link())

    def setPlayerLabel(self):
        if self.currentPlayer == 1:
            self.P1_label.config(background = P1_selected)
            self.P2_label.config(background = free)
        else:
            self.P1_label.config(background = free)
            self.P2_label.config(background = P2_selected)

    def click(self, event):
        (x,y) = event.x, event.y
        a = self.canvas.find_overlapping(x, y, x, y)
        if len(a) == 1:
            point = Point.get_point(a[0])
            print(Point.get_point(a[0]).state)
            if not point.handle_click(self.currentPlayer):
                self.canvas.scale(point.rep, point.i*DIST+XMIN, point.j*DIST+YMIN, 1.5, 1.5)
                self.canvas.after(100, lambda : self.canvas.scale(point.rep, point.i*DIST+XMIN, point.j*DIST+YMIN, 1/1.5, 1/1.5))

    def endTurn(self, event):
        if self.currentPlayer == 1 :
            self.currentPlayer = 2
        else:
            self.currentPlayer = 1
        self.setPlayerLabel()
        if not self.check_possible_moves():
            askretrycancel("Perdu !", icon="warning", message="Le joueur "+str(self.currentPlayer)+" a perdu...")

    def check_possible_moves(self):
        """Mark every point that can be played during the next turn"""
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if (i+j) % 2 == 0:
                    point = self.grid[i][j]
                    if point.playable():

                        return True
        return False

class Point:
    points = [] # List of every created point
    selected_points = [] # List of the current selected points (by order of selection)

    def __init__(self,i,j):
        self.color = "white"

        # Coordinates of the points on the grid
        self.i = i
        self.j = j

        self.rep = None # Tkinter object index on canvas
        self.state = "free"
        Point.points.append(self)

    def get_point(rep):
        """Get a point by its tkinter id, point.rep"""
        for point in Point.points:
            if point.rep == rep :
                return point

    def playable(self):
        """Check if a point can be played"""
        if self.state == "free":
            if len(Point.selected_points) > 0:
                previous_point = Point.selected_points[-1]
                a, b = self.i, self.j
                c, d = previous_point.i, previous_point.j
                if ((abs(a-c) == 2 and (b-d) == 0 and jeu.grid[(c-a)//2 +a][b].linked == False) # The points are on the same row
                    or (abs(a-c) == 1 and abs(b-d) == 1) # The points are on a diagonal
                    or (abs(a-c) == 0 and abs(b-d) == 2 and jeu.grid[a][(d-b)//2 + b].linked == False)): # The points are on the same column
                    return True

            elif len(Point.selected_points) == 0:
                voisin1 = self.has_accessible_neighbor()
                if voisin1 != None:
                    voisin1.state = "selected"
                    voisin2 = self.has_accessible_neighbor()
                    if voisin2 != None:
                        voisin1.state = "free"
                        return True
                    else :
                        self.state = "selected"
                        voisin2 = voisin1.has_accessible_neighbor()
                        if voisin2 != None:
                            voisin1.state = "free"
                            self.state = "free"
                            return True
                    voisin1.state = "free"
                    self.state = "free"

        return False

    def handle_click(self, player):
        """Check if the point can be selected"""
        if self.state == "selected":
            self.unselect()
            return True

        elif self.playable():
            Point.selected_points.append(self)
            self.select(player)
            return True

        return False

    def select(self, player):
        self.state = "selected"
        self.change_color(player)
        Point.link(player)

    def unselect(self):
        self.state = "free"
        self.change_color()
        Point.selected_points.remove(self)

    def link(player):
        if len(Point.selected_points) == 3:
            for point in Point.selected_points:
                point.state = "linked"
                point.change_color(player)

            a,b = Point.selected_points[0].i, Point.selected_points[0].j
            c,d = Point.selected_points[1].i, Point.selected_points[1].j
            e,f = Point.selected_points[2].i, Point.selected_points[2].j

            if abs(a-c) == 2 and (b-d) == 0: jeu.grid[(c-a)//2 +a][b].mark_linked()
            if (a-c) == 0 and abs(b-d) == 2: jeu.grid[a][(d-b)//2 + b].mark_linked()

            if abs(c-e) == 2 and (d-f) == 0: jeu.grid[(e-c)//2 +c][d].mark_linked()
            if (c-e) == 0 and abs(d-f) == 2: jeu.grid[c][(f-d)//2 + d].mark_linked()

            jeu.canvas.create_line(XMIN+a*DIST, YMIN+b*DIST, XMIN+c*DIST, YMIN+d*DIST, width=RADIUS*2, fill=colors[player]["linked"])
            jeu.canvas.create_line(XMIN+c*DIST, YMIN+d*DIST, XMIN+e*DIST, YMIN+f*DIST, width=RADIUS*2, fill=colors[player]["linked"])

            Point.selected_points.clear()
            jeu.canvas.event_generate("<<EndTurn>>")

    def change_color(self,player = None):
        """Set the color of the point"""
        global colors
        jeu.canvas.itemconfig(self.rep, fill = colors[player][self.state])

    def has_accessible_neighbor(self):
        """Return an accessible neighor"""
        for (dx,dy) in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (-1, 1), (1, 1), (1, -1)]:
            i,j = self.i, self.j
            x,y = self.i + dx, self.j + dy
            if x >= 0 and x < len(jeu.grid) and y >= 0 and y < len(jeu.grid[x]):
                if ((abs(x-i) == 2 and (y-j) == 0 and jeu.grid[(i-x)//2 +x][y].linked == False) # The points are on the same row
                    or (abs(x-i) == 1 and abs(y-j) == 1) # The points are on x diagonal
                    or (abs(x-i) == 0 and abs(y-j) == 2 and jeu.grid[x][(j-y)//2 + y].linked == False)): # The points are on the same column
                    if jeu.grid[x][y].state == "free":
                            return jeu.grid[x][y]
        return None

class Link:
    def __init__(self):
        self.rep = None # Tkinter object index on canvas
        self.linked = False # The link is free

    def mark_linked(self):
        self.linked = True # The link is blocked

jeu = Jeu(window, 1)
window.mainloop()
