# coding: utf-8

import sys
from time import sleep, localtime
import tkinter as tk
from random import choice
import os.path
from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

from GameEngine import GameEngine

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
            self.Send({"action":"start", "ranking":self._server.rating, "tournament_state":self._server.tournament_state})
            self._server.showRanking()
            self._server.sendRanking()

        elif self.nickname in self._server.rating and self._server.rating[self.nickname]["state"] != CONNECTED:
            self._server.rating[self.nickname]["state"] = CONNECTED
            self._server.PrintPlayers()
            self.Send({"action":"start", "ranking":self._server.rating, "tournament_state":self._server.tournament_state})
            self._server.showRanking()
            self._server.sendRanking()

        else:
            self.Send({"action":"rejected"})

    def Network_selectPoint(self, data):
        """Receive a selected point from a player"""
        nickname = data["nickname"]
        partners = data["partners"]
        column = data["column"]

        # Check wether the point can be selected or not, or ends a move
        j = s.games[partners].canPlaceToken(column)
        if type(j) is int :
            # Can be selected, send the information
            s.games[partners].placeToken(column)
            [p.Send({"action":"placeToken", "column": column, "line":j}) for p in self._server.players if p.nickname in partners]
            if s.games[partners].checkIfWinner():
                # Winner is currentPlayer
                [p.Send({"action":"endGame"}) for p in self._server.players if p.nickname in partners]
                winner = s.games[partners].currentPlayer
                temp = list(partners)
                temp.remove(winner)
                loser = temp[0]
                self._server.rating[winner]["state"] = CONNECTED
                self._server.rating[loser]["state"] = CONNECTED
                self._server.updateRanking(winner, loser)
            else:
                if s.games[partners].remainingPoints():
                    [p.Send({"action":"swapPlayers"}) for p in self._server.players if p.nickname in partners]
                else:
                    [p.Send({"action":"equality"}) for p in self._server.players if p.nickname in partners]
                    for player in partners:
                        self._server.rating[player]["state"] = CONNECTED
                    self._server.updateRanking(winner, loser)

        # else:
        #     # Cannot be selected
        #     [p.Send({"action":"wrongSelection", "pointCoords": coords}) for p in self._server.players if p.nickname in partners]

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
        """When someone asks for a game against an opponent
        with more than 200 pts score difference,
        ask the opponent if he is OK to start a game"""
        player1 = data["players"][0]
        player2 = data["players"][1]
        s.rating[player1]["state"] = PLAYING
        s.rating[player2]["state"] = PLAYING
        self._server.sendRanking()
        self._server.showRanking()
        [p.Send({"action":"askGame", "players":data["players"]}) for p in self._server.players if p.nickname == player2]

    def Network_askWhoStart(self, data):
        """Ask randomly to one of the 2 players if he wants to start"""
        player1 = data["players"][0]
        player2 = data["players"][1]
        s.rating[player1]["state"] = PLAYING
        s.rating[player2]["state"] = PLAYING
        self._server.sendRanking()
        self._server.showRanking()
        random_player = choice(data["players"])
        print(player1, player2, random_player)
        [p.Send({"action":"askBegin", "players":data["players"]}) for p in self._server.players if p.nickname == random_player]

    def Network_declinedGame(self, data):
        """Send the asking player that the opponent
        refused the game"""
        player1 = data["players"][0]
        player2 = data["players"][1]
        s.rating[player1]["state"] = CONNECTED
        s.rating[player2]["state"] = CONNECTED
        self._server.sendRanking()
        self._server.showRanking()
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
        self.logo = tk.PhotoImage(file="logo_puissance_4.gif", format="gif")
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

        print('Serveur du Puissance 4 démarré :)')

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
        [p.Send({"action":"startTournament"}) for p in self.players]
        self.startTournament_b.config(text="Tournoi lancé")
        self.sendRanking()

    def showRanking(self):
        """Update ranking display in the window"""
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
    Window.title("Puissance 4 - Serveur")
    host, port = sys.argv[1].split(":")
    s = MyServer(localaddr=(host, int(port)))
    s.Launch()
