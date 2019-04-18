# coding: utf-8

import sys
from time import sleep, localtime
import tkinter as tk
from random import choice
import os.path
import pickle
import elo
from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

from game import GameEngine

class ClientChannel(Channel):
    """
    This is the server representation of a connected client.
    """
    def __init__(self, *args, **kwargs):
        self.nickname = "anonymous"
        Channel.__init__(self, *args, **kwargs)

    def Close(self):
        self._server.DelPlayer(self)

    def Network_nickname(self, data):
        self.nickname = data["nickname"]
        self._server.PrintPlayers()
        # TODO: Check nickname, if already connected, cry, else send ranking
        self._server.rating[self.nickname] = 1000
        self.Send({"action":"start", "ranking":self._server.rating})
        self._server.showRanking()
        self._server.sendRanking()

    def Network_selectPoint(self, data):
        nickname = data["nickname"]
        partners = data["partners"]
        coords = (i,j) = data["pointCoords"]

        select = s.games[partners].selector(coords)

        if select == True :
            [p.Send({"action":"pointState", "pointCoords": coords, "state" : self._server.games[partners].grid[i][j].state}) for p in self._server.players if p.nickname in partners]
        elif type(select) is list and len(select) == 3:
            [p.Send({"action":"endTurn", "pointList":select}) for p in self._server.players if p.nickname in partners]

            if s.games[partners].end_move() == False: # no more playable points
                # TODO: change score, current is looser
                # self._server.changeScore
                #
                # s.games[partners].currentPlayer

                [p.Send({"action":"endGame"}) for p in self._server.players if p.nickname in partners]
        else:
            [p.Send({"action":"wrongSelection", "pointCoords": coords}) for p in self._server.players if p.nickname in partners]


    def Network_launchGame(self, data):
        """Check if a game can be launched"""
        player1 = data["players"][0] # player1 is the player asking for the game
        player2 = data["players"][1] # player2 is the opponent player1 chooses
        confirmation = data["confirmation"]

        print("LaunchGame, player1 = {}, player2 = {}".format(player1,player2))
        launchGame = False
        if confirmation == False:
            [p.Send({"action":"message", "messageType":"GameRefused","opponent":player1}) for p in self._server.players if p.nickname == player2]
        elif confirmation == None:
            if abs(self._server.rating[player1] - self._server.rating[player2]) > 300:
                [p.Send({"action": "message", "messageType":"RatingGapTooHigh"}) for p in self._server.players if p.nickname == player1]
            elif abs(self._server.rating[player1] - self._server.rating[player2]) > 200:
                [p.Send({"action": "message", "messageType": "AskLaunchGame", "asker": player1}) for p in self._server.players if p.nickname == player2]
            else:
                launchGame = True

        if launchGame or confirmation:
            self._server.games[(player1, player2)] = GameEngine(player1, player2)
            [p.Send({"action":"startGame", "players":(player1, player2)}) for p in self._server.players if p.nickname in [player1, player2]]

class MyServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)

        self.active = True
        self.players = {}
        self.games = {}

        self.rating = {}
        # if os.path.isfile("ranking.game"):
        #     with open("ranking.game", "rb") as ranking:
        #         self.rating = pickle.load(ranking)

        interface = tk.LabelFrame(Window, text = "Jeu de la Saucisse - Serveur", padx=10, pady=10)
        interface.pack()
        self.ranking_container = tk.LabelFrame(interface, text = "Classement", padx=10, pady=10)
        self.ranking_container.grid(row=0, column=0, sticky="new")
        self.ranking = tk.Frame(self.ranking_container)

        self.controls = tk.LabelFrame(interface, text="Contrôles", padx=10, pady=10)
        self.controls.grid(row=1, column=0, sticky="new")
        tk.Button(self.controls, text="Arrêter le serveur", command=self.Stop).pack(side = tk.LEFT)
        tk.Button(self.controls, text="Send ranking DEBUG", command=self.sendRanking).pack(side=tk.LEFT)
        self.showRanking()

        print('Saucisse server launched :)')

    def Connected(self, channel, addr):
        self.AddPlayer(channel)

    def AddPlayer(self, player):
        print("New Player connected")
        self.players[player] = True

    def PrintPlayers(self):
        print("players' nicknames :",[p.nickname for p in self.players])

    def DelPlayer(self, player):
        print("Deleting Player " + player.nickname + " at "+str(player.addr))
        del self.players[player]
        self.PrintPlayers()

    def SendToOthers(self, data):
        [p.Send({"action":"newPoint", "newPoint" : data["newPoint"]}) for p in self.players if p.nickname != data["who"]]

    def Launch(self):
        while self.active:
            self.Pump()
            Window.update()
            sleep(0.001)

    def Stop(self):
        self.active = False
        print("See you!")

    def showRanking(self):
        self.ranking.destroy()
        self.ranking = tk.Frame(self.ranking_container)
        self.ranking.pack(side=tk.LEFT)
        sorted_rank = sorted(self.rating.items(), key = lambda x:x[1])

        for i in range(len(sorted_rank)):
            tk.Label(self.ranking, text=str(i+1)).grid(row=i, column=0)
            tk.Label(self.ranking, text=sorted_rank[i][0]).grid(row=i, column = 1)
            tk.Label(self.ranking, text=sorted_rank[i][1]).grid(row=i, column = 2)

    def sendRanking(self):
        print('Sent!')
        [p.Send({"action":"showRanking", "ranking":self.rating}) for p in self.players]


    # def network_LaunchGame(self, data):
    #     """Check if a game can be launched"""
    #     # if len(self.players) == 2:
    #     #     players = list(self.players.keys())
    #     #     player1 = choice(players)
    #     #     player2 = choice(players)
    #     #     while player2 == player1:
    #     #         player2 = choice(players)
    #     #     player1 = player1.nickname
    #     #     player2 = player2.nickname
    #     print("LaunchGame")
    #     player1 = data["players"][0] # player1 is the player asking for the game
    #     player2 = data["players"][1] # player2 is the opponent player1 chooses
    #     confirmation = data["confirmation"]
    #
    #     launchGame = False
    #     if confirmation == False:
    #         player2.Send({"action":"message", "messageType":"GameRefused","opponent":player1})
    #     elif confirmation == None:
    #         if abs(self.rating[player1] - self.rating[player2]) > 300:
    #             [p.Send({"action": "message", "messageType":"RatingGapTooHigh"}) for p in self.players if p.nickname == player1]
    #         elif abs(self.rating[player1] - self.rating[player2]) > 200:
    #             [p.Send({"action": "message", "messageType": "AskLaunchGame", "asker": player1}) for p in self.players if p.nickname == player2]
    #         else:
    #             launchGame = True
    #
    #     if launchGame or confirmation:
    #         self.games[(player1, player2)] = GameEngine(player1, player2)
    #         [p.Send({"action":"startGame", "players":(player1, player2)}) for p in self.players if p.nickname in [player1, player2]]

# get command line argument of server, port
if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
else:
    Window=tk.Tk()
    host, port = sys.argv[1].split(":")
    s = MyServer(localaddr=(host, int(port)))
    s.Launch()
