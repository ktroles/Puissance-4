# coding: utf-8

import sys
from time import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener

import tkinter as tk
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
        interface = tk.LabelFrame(Window, text = "Jeu de la Saucisse - Serveur", padx=10, pady=10)
        interface.pack()

        self.ranking_container = tk.LabelFrame(interface, text = "Classement", padx=10, pady=10)
        # self.ranking_container.grid(row=0, column=0, sticky="new")
        self.ranking_container.pack()
        self.ranking = tk.Frame(self.ranking_container)

        print("Bienvenu au jeu de la saucise !")
        print("Appuyez sur Ctrl-C pour fermer cette fenêtre")
        print("Quel est votre prénom ? ")
        nickname=str(stdin.readline().rstrip("\n"))
        self.nickname=nickname
        self.Connect((host, port))
        self.state=INITIAL
        connection.Send({"action": "nickname", "nickname": nickname})
        # a single loop to send to the server my nickname
        self.Loop()

    def Network_connected(self, data):
        print("Vous êtes maintenant connecté au serveur !")

    def Loop(self):
        connection.Pump()
        self.Pump()

    def quit(self):
        Window.destroy()
        self.state = DEAD

    def Network_start(self,data):
        self.state = ACTIVE
        self.Network_showRanking(data)
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

    def Network_showRanking(self,data):
        print("show")
        score = data["ranking"] # dictionnary of scores for every player
        sorted_rank = sorted(score.items(), key = lambda x:x[1])
        self.ranking.destroy()
        self.ranking = Label(self.ranking_container)
        self.ranking.pack(side=LEFT)

        for i in range(len(sorted_rank)):
            Label(self.ranking, text=str(i+1)).grid(row=i, column=0)
            Label(self.ranking, text=sorted_rank[i][0]).grid(row=i, column = 1)
            Label(self.ranking, text=sorted_rank[i][1]).grid(row=i, column = 2)

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
        self.game_ui.setPointState(data["pointCoords"], data["state"])

    def Network_wrongSelection(self, data):
        coords = data["pointCoords"]
        self.game_ui.wrongSelection(coords)

    def Network_endTurn(self,data):
        """Finish current move and swap players"""
        pointList = data["pointList"]
        for point in pointList:
            self.game_ui.setPointState(point, "linked")
        self.game_ui.changeCurrentPlayer()
        self.state = WAITING if self.state == PLAYING else PLAYING

    def Network_endGame(self,data):
        self.game_ui.endGame()
        self.state = ACTIVE


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
Window=tk.Tk()
c = Client(host, int(port))
Window.update()
sleep(0.1)


# first loop to say to the server that I exist
c.Loop()
