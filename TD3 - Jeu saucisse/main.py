from tkinter import *

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
            Point.get_point(a[0]).select(self.currentPlayer)

    def endTurn(self, event):
        if self.currentPlayer == 1 :
            self.currentPlayer = 2
        else:
            self.currentPlayer = 1
        self.setPlayerLabel()
        print("Changement de joueur")

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
        """Get a point by its id"""
        for point in Point.points:
            if point.rep == rep :
                return point

    def select(self, player):
        """Check if the point can be selected"""
        if len(Point.selected_points) > 0:
            previous_point = Point.selected_points[-1]
        else :
            previous_point = None

        if self.state == "selected":
            self.unselect()
            return True

        elif self.state == "free":
            if previous_point == None:
                self.state = "selected"
                self.change_color(player)
                Point.selected_points.append(self)
                return True
            else:
                a, b = self.i, self.j
                c, d = previous_point.i, previous_point.j
                print((a,b), (c,d))
                if ((abs(a-c) == 2 and (b-d) == 0 and jeu.grid[(c-a)//2 +a][b].linked == False) # The points are on the same row
                or (abs(a-c) == 1 and abs(b-d) == 1) # The points are on a diagonal
                or (abs(a-c) == 0 and abs(b-d) == 2 and jeu.grid[a][(d-b)//2 + b].linked == False)): # The points are on the same column

                    self.state = "selected"
                    self.change_color(player)
                    Point.selected_points.append(self)
                    Point.link(player)
                    return True

        return False

    def unselect(self):
        self.state = "free"
        self.change_color()
        Point.selected_points.remove(self)

    def link(player):
        if len(Point.selected_points) == 3:
            for point in Point.selected_points:
                point.state = "linked"
                point.change_color(player)


            Point.selected_points.clear()
            jeu.canvas.event_generate("<<EndTurn>>")

    def change_color(self,player = None):
        """Set the color of the point"""
        global colors
        jeu.canvas.itemconfig(self.rep, fill = colors[player][self.state])


class Link:
    def __init__(self):
        self.rep = None # Tkinter object index on canvas
        self.linked = False

jeu = Jeu(window, 1)
window.mainloop()
