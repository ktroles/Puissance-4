import sys
from time import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener

from tkinter import *
WIDTH=300
HEIGHT=200
R=5

INITIAL=0
ACTIVE=1
DEAD=-1
PLAYING = 2

class Client(ConnectionListener):

    def __init__(self, host, port):
        self.Connect((host, port))
        self.state=INITIAL
        print("Client started")
        print("Ctrl-C to exit")
        print("Enter your nickname: ")
        nickname=stdin.readline().rstrip("\n")
        self.nickname=nickname
        connection.Send({"action": "nickname", "nickname": nickname})
        # a single loop to send to the server my nickname
        self.Loop()

    def Network_connected(self, data):
        print("You are now connected to the server")

    def Loop(self):
        connection.Pump()
        self.Pump()

    def quit(self):
        Window.destroy()
        self.state=DEAD

    def Network_start(self,data):
        self.state=ACTIVE
        while self.state!=DEAD:
            Window.update()
            self.Loop()
            sleep(0.001)
        exit()

    def Network_newPoint(self, data):
        (x,y)=data["newPoint"]
        myCanvas.create_oval(x-R,y-R,x+R,y+R)
        myCanvas.update()

    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()

    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()

    def Network_startGame(self, data):
        (player1, player2) = data["players"]
        print(player1, player2)

        # Setup the window layout
        self.controls = Frame(Window, width = WIDTH)
        self.controls.pack()
        self.currentPlayer = self.nickname if player1 == self.nickname else player2.nickname
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

        def click(self, event):
            (x,y) = event.x, event.y
            a = self.canvas.find_overlapping(x, y, x, y)
            if len(a) == 1:
                rep = a[0]
                for point in self.points:
                    if point.rep == rep:
                        c.Send({"action":"newPoint","newPoint" : (evt.x,evt.y)})
                        return (point.i, point.j)

#########################################################

if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    exit()

host, port = sys.argv[1].split(":")
c = Client(host, int(port))

Window=Tk()
myCanvas = Canvas(Window, width=WIDTH, height = HEIGHT,bg='white')
myCanvas.pack(side=TOP)

def drawNewPoint(evt):
    myCanvas.create_oval(evt.x-R,evt.y-R,evt.x+R,evt.y+R)
    c.Send({"action":"newPoint","newPoint" : (evt.x,evt.y)})

myCanvas.bind("<Button-1>",drawNewPoint)
Quit=Button(Window,text='Quitter',command = c.quit)
Quit.pack(side=BOTTOM)

# first loop to say to the server that I exist
c.Loop()
