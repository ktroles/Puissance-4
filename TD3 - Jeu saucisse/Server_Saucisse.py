# coding: utf-8

import sys
from time import sleep, localtime
import tkinter as tk
from random import choice
import os.path
from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

from game import GameEngine

# CONSTANTS
WAITING_FOR_PLAYERS = 0
STARTED = 1

DISCONNECTED = -1
CONNECTED = 1
PLAYING = 2

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
        """Handle the reception of a nickname
        If the tournament has already begun, the player is only accepted if he was connected at the beginning"""
        self.nickname = data["nickname"]

        if self._server.tournament_state == WAITING_FOR_PLAYERS and self.nickname not in self._server.rating:
            self._server.rating[self.nickname] = {"rating":1000, "state":CONNECTED}
            self._server.PrintPlayers()
            self.Send({"action":"start", "ranking":self._server.rating})
            self._server.showRanking()
            self._server.sendRanking()

        elif self.nickname in self._server.rating and self._server.rating[self.nickname]["state"] != CONNECTED:
            self._server.rating[self.nickname]["state"] = CONNECTED
            self._server.PrintPlayers()
            self.Send({"action":"start", "ranking":self._server.rating})
            self._server.showRanking()
            self._server.sendRanking()

        else:
            self.Send({"action":"rejected"})

    def Network_selectPoint(self, data):
        """Receive a selected point from a player"""
        nickname = data["nickname"]
        partners = data["partners"]
        coords = (i,j) = data["pointCoords"]

        # Check wether the point can be selected or not, or ends a move
        select = s.games[partners].selector(coords) # True, False or list of 3 points

        if select == True :
            # Can be selected, send the information
            [p.Send({"action":"pointState", "pointCoords": coords, "state" : self._server.games[partners].grid[i][j].state}) for p in self._server.players if p.nickname in partners]
        elif type(select) is list and len(select) == 3:
            # Ends a move
            [p.Send({"action":"endTurn", "pointList":select}) for p in self._server.players if p.nickname in partners]

            if s.games[partners].end_move(): # no more playable points
                # Ends the game
                [p.Send({"action":"endGame"}) for p in self._server.players if p.nickname in partners]
                winner = s.games[partners].currentPlayer
                temp = list(partners)
                temp.remove(winner)
                loser = temp[0]
                self._server.rating[winner]["state"] = CONNECTED
                self._server.rating[loser]["state"] = CONNECTED
                self._server.updateRanking(winner, loser)

            else:
                [p.Send({"action":"swapPlayers"}) for p in self._server.players if p.nickname in partners]

        else:
            # Cannot be selected
            [p.Send({"action":"wrongSelection", "pointCoords": coords}) for p in self._server.players if p.nickname in partners]

    def Network_launchGame(self, data):
        if self._server.tournament_state == STARTED:
            player1 = data["players"][0]
            player2 = data["players"][1]
            self._server.rating[player1]["state"] = PLAYING
            self._server.rating[player2]["state"] = PLAYING
            self._server.sendRanking()
            self._server.showRanking()
            self._server.games[(player1, player2)] = GameEngine(player1, player2)
            [p.Send({"action":"startGame", "players":(player1, player2)}) for p in self._server.players if p.nickname in [player1, player2]]
            print("Started a game with {} and {}".format(player1,player2))

    def Network_askGame(self, data):
        player2 = data["players"][1]
        [p.Send({"action":"askGame", "players":data["players"]}) for p in self._server.players if p.nickname == player2]

    def Network_declinedGame(self, data):
        player1 = data["players"][0]
        [p.Send({"action":"declinedGame", "players":data["players"]}) for p in self._server.players if p.nickname == player1]



class MyServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)

        self.active = True
        self.players = {}
        self.games = {}
        self.rating = {}

        self.tournament_state = WAITING_FOR_PLAYERS

        interface = tk.Frame(Window, padx=10, pady=10)
        interface.pack()
        self.logo = tk.PhotoImage(file="logo_server.gif", format="gif")
        tk.Label(interface, image=self.logo).grid(row=0, column=0)

        self.ranking_container = tk.LabelFrame(interface, text = "Classement", padx=10, pady=10)
        self.ranking_container.grid(row=1, column=0, sticky="new")
        self.ranking = tk.Frame(self.ranking_container)

        self.controls = tk.LabelFrame(interface, text="Contrôles", padx=10, pady=10)
        self.controls.grid(row=2, column=0, sticky="new")
        self.startTournament_b = tk.Button(self.controls, text="Lancer le tournoi", command=self.startTournament, padx=5)
        self.startTournament_b.pack(side=tk.LEFT, padx=5)
        tk.Button(self.controls, text="Arrêter le serveur", command=self.Stop, padx=5).pack(side = tk.LEFT, padx=5)
        self.showRanking()

        print('Saucisse server launched :)')

    def Connected(self, channel, addr):
        self.AddPlayer(channel)

    def AddPlayer(self, player):
        print("Un joueur vient de se connecter")
        self.players[player] = True

    def PrintPlayers(self):
        print("Liste des joueurs :", [p.nickname for p in self.players])

    def DelPlayer(self, player):
        print("Supression du joueur " + player.nickname + ", "+ str(player.addr))
        if len([p for p in self.players if p.nickname == player.nickname]) == 1:
            if player.nickname in self.rating:
                self.rating[player.nickname]["state"] = DISCONNECTED
        del self.players[player]
        self.PrintPlayers()
        self.showRanking()
        self.sendRanking()

    def Launch(self):
        while self.active:
            self.Pump()
            Window.update()
            sleep(0.001)

    def Stop(self):
        self.active = False
        print("Serveur éteint.")

    def startTournament(self):
        if self.tournament_state != STARTED:
            self.tournament_state = STARTED
        self.startTournament_b.config(text="Tournoi lancé")

    def showRanking(self):
        """
        Update ranking display in the window
        """
        self.ranking.destroy()
        self.ranking = tk.Frame(self.ranking_container)
        self.ranking.pack(side=tk.LEFT)
        sorted_rank = sorted(self.rating.items(), key = lambda x:x[1]["rating"], reverse=True)

        rank = 1
        for i in range(len(sorted_rank)):
            nickname = sorted_rank[i][0]
            rating = sorted_rank[i][1]["rating"]
            state = sorted_rank[i][1]["state"]

            if i>=1 and rating == sorted_rank[i-1][1]["rating"]:
                tk.Label(self.ranking, text="-").grid(row=i, column=0, padx=15)
            else:
                tk.Label(self.ranking, text=str(rank)+".").grid(row=i, column=0, padx=15)
                rank += 1

            tk.Label(self.ranking, text=nickname).grid(row=i, column = 1, padx=15)
            tk.Label(self.ranking, text=rating).grid(row=i, column = 2, padx=15)

            if state == CONNECTED:
                tk.Label(self.ranking, bitmap="hourglass", bg="green").grid(row=i, column=3, padx=10)
            elif state == DISCONNECTED:
                tk.Label(self.ranking, bitmap="error", bg="red").grid(row=i, column=3, padx=10)
            elif state == PLAYING:
                tk.Label(self.ranking, bitmap="questhead").grid(row=i, column=3, padx=10)



    def sendRanking(self):
        """Send updated ranking to every player"""
        [p.Send({"action":"showRanking", "ranking":self.rating}) for p in self.players]

    def updateRanking(self, winner, loser):
        """Update the rating of winner and loser after a game"""
        g = self.rating[winner]["rating"]
        p = self.rating[loser]["rating"]

        score = int((100 - (g-p)/3))

        self.rating[winner]["rating"] = g + score
        self.rating[loser]["rating"] = p - score

        self.showRanking()
        self.sendRanking()


# get command line argument of server, port
if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
else:
    Window=tk.Tk()
    host, port = sys.argv[1].split(":")
    s = MyServer(localaddr=(host, int(port)))
    s.Launch()
