# coding: utf-8

import sys
from time import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener

from tkinter import *
from gui import *

# INITAL WINDOW CONSTANTS
WIDTH=300
HEIGHT=200
R=5

# STATE CONSTANTS
INITIAL = 0
ACTIVE = 1
DEAD = -1
PLAYING = 2
WAITING = 3

class Client(ConnectionListener):

    def __init__(self, host, port):
        self.Connect((host, port))
        self.state=INITIAL
        print("Bienvenu au jeu de la saucise !")
        print("Appuyez sur Ctrl-C pour fermer cette fenêtre")
        print("Quel est votre prénom ? ")
        nickname=str(stdin.readline().rstrip("\n"))
        self.nickname=nickname
        connection.Send({"action": "nickname", "nickname": nickname})
        # a single loop to send to the server my nickname
        self.Loop()

    def Network_connected(self, data):
        print("Vous êtes maintenant connecté au serveur ! server")

    def Loop(self):
        connection.Pump()
        self.Pump()

    def quit(self):
        Window.destroy()
        self.state = DEAD

    def Network_start(self,data):
        self.state = ACTIVE
        while self.state != DEAD:
            Window.update()
            self.Loop()
            sleep(0.001)
        exit()

    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()

    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()

    def Network_startGame(self, data):
        """Start a game with a partner"""
        (player1, player2) = self.currentGamePartners = data["players"]

        print("Should start a game with {} and {}".format(player1, player2))

        if self.nickname == player1:
            self.state = PLAYING
        elif self.nickname == player2:
            self.state = WAITING

        self.game_ui = GUI(player1, player2)
        self.game_ui.canvas.bind("<Button-1>", self.click)

    def Network_pointState(self, data):
        print("Network PointState called")
        self.game_ui.setPointState(data["pointCoords"], data["state"])

    def Network_endTurn(self,data):
        pointList = data["pointList"]
        for point in pointList:
            self.game_ui.setPointState(point, "linked")
        self.game_ui.changeCurrentPlayer()
        self.state = WAITING if self.state == PLAYING else PLAYING

    def Network_endGame(self,data):
        self.game_ui.printEndGame()
        self.state = ACTIVE

    def Network_wrongSelection(self, data):
        coords = data["pointCoords"]
        self.game_ui.wrongSelection(coords)

    def click(self, event):
        (x,y) = event.x, event.y
        a = self.game_ui.canvas.find_overlapping(x, y, x, y)
        if len(a) == 1:
            rep = a[0]
            for point in self.game_ui.points:
                if point.rep == rep:
                    if self.state == PLAYING:
                        connection.Send({"action":"selectPoint", "nickname" : self.nickname,
                                "partners": self.currentGamePartners, "pointCoords" : (point.i,point.j)})
                        print("Trying to select ", point.i, " ", point.j)
                    else:
                        self.game_ui.wrongSelection((point.i, point.j))

#########################################################

if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    exit()

host, port = sys.argv[1].split(":")
c = Client(host, int(port))

Window=Tk()
myCanvas = Canvas(Window, width=WIDTH, height = HEIGHT, bg='white')
myCanvas.pack(side=TOP)

Quit=Button(Window,text='Quitter',command = c.quit)
Quit.pack(side=BOTTOM)

# first loop to say to the server that I exist
c.Loop()
