# coding: utf-8

# GAME CONSTANTS
GRID_WIDTH = 9
GRID_HEIGHT = 7

class GameEngine:
    """Class representing a game"""
    def __init__(self, player1, player2):
        # Initialize the grid containing Points and Links
        # Points are on the case where (i+j)%2 == 0
        self.grid = []
        self.player1 = player1
        self.player2 = player2
        self.currentPlayer = player1
        self.selected_points = []

        for i in range(GRID_WIDTH):
            self.grid.append(list())
            for j in range(GRID_HEIGHT):
                if (i+j) % 2 == 0:
                    self.grid[i].append(Point(i, j))
                else:
                    self.grid[i].append(Link())

    def accessible_neighbor(self, point):
        """Return an accessible neighor"""
        i, j = point.i, point.j
        for (dx,dy) in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (-1, 1), (1, 1), (1, -1)]:
            x,y = i + dx, j + dy
            if x >= 0 and x < len(self.grid) and y >= 0 and y < len(self.grid[x]):
                if ((abs(x-i) == 2 and (y-j) == 0 and self.grid[(i-x)//2 +x][y].linked == False) # The points are on the same row
                    or (abs(x-i) == 1 and abs(y-j) == 1) # The points are on a diagonal
                    or (abs(x-i) == 0 and abs(y-j) == 2 and self.grid[x][(j-y)//2 + y].linked == False)): # The points are on the same column
                    if self.grid[x][y].state == "free":
                            return self.grid[x][y]
        return None

    def selector(self, pointCoords):
        (i, j) = pointCoords
        point = self.grid[i][j]
        if point.state == "selected":
            self.selected_points.remove(point)
            point.unselect()
            return True
        elif self.playable(point):
            self.selected_points.append(point)
            point.select()
            if len(self.selected_points) == 3:
                return [(point.i, point.j) for point in self.selected_points]
            return True
        return False

    def playable(self, point):
        """Check if a point can be played"""
        if point.state == "free":
            if len(self.selected_points) > 0:
                previous_point = self.selected_points[-1]
                a, b = point.i, point.j
                c, d = previous_point.i, previous_point.j
                if ((abs(a-c) == 2 and (b-d) == 0 and self.grid[(c-a)//2 +a][b].linked == False) # The points are on the same row
                    or (abs(a-c) == 1 and abs(b-d) == 1) # The points are on a diagonal
                    or (abs(a-c) == 0 and abs(b-d) == 2 and self.grid[a][(d-b)//2 + b].linked == False)): # The points are on the same column
                    return True

            elif len(self.selected_points) == 0:
                voisin1 = self.accessible_neighbor(point)
                if voisin1 != None:
                    voisin1.state = "selected"
                    voisin2 = self.accessible_neighbor(point)
                    if voisin2 != None:
                        voisin1.state = "free"
                        return True
                    else :
                        point.state = "selected"
                        voisin2 = self.accessible_neighbor(voisin1)
                        if voisin2 != None:
                            voisin1.state = "free"
                            point.state = "free"
                            return True
                    voisin1.state = "free"
                    point.state = "free"

        return False

        # if point.state == "free":
        #     if len(self.selected_points) == 0:
        #         voisin1 = self.accessible_neighbor(point)
        #         if voisin1 != None:
        #             voisin1.state = "selected"
        #             voisin2 = self.accessible_neighbor(point)
        #             if voisin2 != None:
        #                 voisin1.state = "free"
        #                 return True
        #             else :
        #                 self.state = "selected"
        #                 voisin2 = self.accessible_neighbor(voisin1)
        #                 if voisin2 != None:
        #                     voisin1.state = "free"
        #                     self.state = "free"
        #                     return True
        #             voisin1.state = "free"
        #             self.state = "free"
        #
        #     elif len(self.selected_points) > 0:
        #         a, b = point.i, point.j
        #         previous_point = self.selected_points[-1]
        #         c, d = previous_point.i, previous_point.j
        #         if ((abs(a-c) == 2 and (b-d) == 0 and self.grid[(c-a)//2 +a][b].linked == False) # The points are on the same row
        #             or (abs(a-c) == 1 and abs(b-d) == 1) # The points are on a diagonal
        #             or (abs(a-c) == 0 and abs(b-d) == 2 and self.grid[a][(d-b)//2 + b].linked == False)): # The points are on the same column
        #             return True

    def check_possible_moves(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if (i+j) % 2 == 0:
                    point = self.grid[i][j]
                    if self.playable(point):
                        return True
        return False

    def end_move(self):
        for point in self.selected_points:
            point.state = "linked"

        a,b = self.selected_points[0].i, self.selected_points[0].j
        c,d = self.selected_points[1].i, self.selected_points[1].j
        e,f = self.selected_points[2].i, self.selected_points[2].j

        if abs(a-c) == 2 and (b-d) == 0:
            self.grid[(c-a)//2 +a][b].mark_linked()
        if (a-c) == 0 and abs(b-d) == 2:
            self.grid[a][(d-b)//2 + b].mark_linked()
        if abs(c-e) == 2 and (d-f) == 0:
            self.grid[(e-c)//2 +c][d].mark_linked()
        if (c-e) == 0 and abs(d-f) == 2:
            self.grid[c][(f-d)//2 + d].mark_linked()

        self.selected_points.clear()

        if self.check_possible_moves():
            if self.currentPlayer == self.player1 :
                self.currentPlayer = self.player2
            else:
                self.currentPlayer = self.player1
            return False

        return True


class Point:
    def __init__(self, i, j):
        self.state = "free"

        # Coordinates of the points on the grid
        self.i = i
        self.j = j

        self.rep = None

    def select(self):
        self.state = "selected"

    def unselect(self):
        self.state = "free"

class Link:
    def __init__(self):
        self.linked = False # The link is free

    def mark_linked(self):
        self.linked = True # The link is blocked
