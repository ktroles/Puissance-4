# coding: utf-8

import sys
from time import sleep, localtime
import tkinter as tk
from random import choice
from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

from game0 import GameEngine

class ClientChannel(Channel):
    """
    This is the server representation of a connected client.
    """
    def __init__(self, *args, **kwargs):
        self.nickname = "anonymous"
        Channel.__init__(self, *args, **kwargs)

    def Close(self):
        self._server.DelPlayer(self)

    def Network_newPoint(self, data):
        self._server.SendToOthers({"newPoint": data["newPoint"], "who": self.nickname})

    def Network_nickname(self, data):
        self.nickname = data["nickname"]
        self._server.PrintPlayers()
        self.Send({"action":"start"})

class MyServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = {}
        self.games = []

        self.players_tk = tk.StringVar()
        interface = tk.LabelFrame(Window, text = "Server - Saucisse", padx=10, pady=10)
        interface.pack()
        PlayerLabel = tk.Label(interface, textvariable=self.players_tk)
        PlayerLabel.pack
        tk.Button(interface, text="Launch a game", command=self.LaunchGame).pack()

        print('Saucisse server launched')

    def Connected(self, channel, addr):
        self.AddPlayer(channel)

    def AddPlayer(self, player):
        print("New Player connected")
        self.players[player] = True

    def PrintPlayers(self):
        print("players' nicknames :",[p.nickname for p in self.players])
        self.players_tk.set(str([p.nickname for p in self.players]))

    def DelPlayer(self, player):
        print("Deleting Player " + player.nickname + " at "+str(player.addr))
        del self.players[player]

    def SendToOthers(self, data):
        [p.Send({"action":"newPoint", "newPoint" : data["newPoint"]}) for p in self.players if p.nickname != data["who"]]

    def Launch(self):
        while True:
            self.Pump()
            Window.update()
            sleep(0.001)

    def LaunchGame(self):
        if len(self.players) == 2:
            players = list(self.players.keys())
            player1 = choice(players)
            player2 = choice(players)
            while player2 == player1:
                player2 = choice(players)
            self.games.append(GameEngine(player1.nickname, player2.nickname))
            [p.Send({"action":"startGame", "players":(player1.nickname, player2.nickname)}) for p in players]


# get command line argument of server, port
if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
else:
    Window=tk.Tk()
    host, port = sys.argv[1].split(":")
    s = MyServer(localaddr=(host, int(port)))
    s.Launch()
