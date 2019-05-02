# coding: utf-8

import sys
from time import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener

import tkinter as tk
from tkinter import simpledialog
from Gui import *

# STATE CONSTANTS
INITIAL = 0
ACTIVE = 1
DEAD = -1
PLAYING = 2
WAITING = 3

CONNECTED = 1
DISCONNECTED = -1

class Client(ConnectionListener):

    def __init__(self, host, port):
        self.window = tk.Tk()
        self.window.withdraw() # hide main window
        self.interface = tk.Frame(self.window, padx=10, pady=10)
        self.interface.pack()

        self.logo = tk.PhotoImage(file="logo_puissance_4.gif", format="gif")
        tk.Label(self.interface, image=self.logo).pack()
        self.tournament_state = False # False if tournament is launched, True otherwise
        self.tournament_state_label = tk.StringVar()
        self.tournament_state_label.set("En attente des autres joueurs ...")
        tk.Label(self.interface, textvariable=self.tournament_state_label).pack()

        print("Bienvenue au jeu de la saucisse !")
        print("Appuyez sur Ctrl-C pour fermer cette fenêtre")
        self.nickname = simpledialog.askstring("Puissance 4", "Bienvenue au Puissance 4 ! \nQuel est votre prénom ?")
        if self.nickname in [None, ""]:
            exit()
        self.window.deiconify() # reveal the window

        self.Connect((host, port))
        self.state=INITIAL
        connection.Send({"action": "nickname", "nickname": self.nickname})
        self.Loop() # a single loop to send to the server my nickname

        self.ranking_container = tk.LabelFrame(self.interface, text = "Classement", padx=10, pady=10)
        self.ranking_container.pack()
        self.ranking = tk.Frame(self.ranking_container)

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
            self.window.update()
            self.Loop()
            sleep(0.001)
        exit()

    def Network_error(self, data):
        print('Erreur :', data['error'][1])
        connection.Close()

    def Network_rejected(self, data):
        print("Le tournoi a déjà démarré...")
        connection.Close()

    def Network_disconnected(self, data):
        print('Serveur déconnecté')
        exit()

    def Network_showRanking(self,data):
        """ Update ranking display in the window """
        score = data["ranking"] # dictionnary of scores for every player
        my_rating = score[self.nickname]["rating"]
        my_state = score[self.nickname]["state"]
        sorted_rank = sorted(score.items(), key = lambda x:x[1]["rating"], reverse=True)
        self.ranking.destroy()
        self.ranking = Label(self.ranking_container)
        self.ranking.pack(side=LEFT)

        rank = 1
        for i in range(len(sorted_rank)):
            nickname = sorted_rank[i][0]
            rating = sorted_rank[i][1]["rating"]
            state = sorted_rank[i][1]["state"]
            if i>=1 and rating == sorted_rank[i-1][1]["rating"]:
                Label(self.ranking, text="-").grid(row=i, column=0, padx=15)
            else:
                Label(self.ranking, text=str(rank)+".").grid(row=i, column=0, padx=15)
                rank += 1

            Label(self.ranking, text=nickname).grid(row=i, column = 1, padx=15)
            Label(self.ranking, text=rating).grid(row=i, column = 2, padx=15)


            if self.nickname != sorted_rank[i][0]:
                if state == CONNECTED:
                    tk.Label(self.ranking, bitmap="hourglass", bg="green").grid(row=i, column=3, padx=10)

                    if my_state == CONNECTED and self.tournament_state:
                        gap = abs(my_rating - rating)
                        if gap < 300:
                            if gap < 200:
                                command = lambda name : lambda name=name : connection.Send({"action":"launchGame", "players":[self.nickname, name]})
                            else:
                                command = lambda name : lambda name=name : connection.Send({"action":"askGame", "players":[self.nickname, name]})
                            Button(self.ranking, text="Défier !", command=command(nickname)).grid(row=i, column = 4, padx=20)
                elif state == DISCONNECTED:
                    tk.Label(self.ranking, bitmap="error", bg="red").grid(row=i, column=3, padx=10)
                elif state == PLAYING:
                    tk.Label(self.ranking, bitmap="questhead").grid(row=i, column=3, padx=10)

    def Network_startGame(self, data):
        """Start a game with a partner"""
        (player1, player2) = self.currentGamePartners = data["players"]

        if self.nickname == player1:
            showinfo("Partie lancée", icon = "info", message = "Partie lancée avec {}.".format(data["players"][1]))
            self.state = PLAYING
        elif self.nickname == player2:
            showinfo("Partie lancée", icon = "info", message = "Partie lancée avec {}.".format(data["players"][0]))
            self.state = WAITING

        self.game_ui = GUI(player1, player2)
        self.game_ui.canvas.bind("<Button-1>", self.click)

    def Network_placePoint(self, data):
        column = data["column"]
        line = data["line"]
        self.game_ui.placePoint(column, line)

    def Network_wrongSelection(self, data):
        coords = data["pointCoords"]
        self.game_ui.wrongSelection(coords)

    def Network_swapPlayers(self, data):
        self.game_ui.changeCurrentPlayer()
        self.state = WAITING if self.state == PLAYING else PLAYING

    def Network_equality(self, data):
        self.game_ui.endGame(equality = True)
        self.state = ACTIVE

    def Network_endGame(self, data):
        self.game_ui.endGame()
        self.state = ACTIVE

    def Network_askGame(self, data):
        """Ask acceptation of player2 to launch a game
        because rating gap between the 2 players is higher than 200"""
        opponent = data["players"][0]

        if askyesno("Demande de partie", message="Voulez-vous lancer une partie contre {} ?".format(opponent)):
            connection.Send({"action":"launchGame", "players":data["players"]})
        else:
            connection.Send({"action":"declinedGame", "players":data["players"]})

    def Network_declinedGame(self, data):
        showinfo("Partie refusée", icon = "info", message = "Partie refusée par {}.".format(data["players"][1]))

    def Network_startTournament(self, data):
        showinfo("Le tournoi a commencé !", icon = "info", message = "Vous pouvez maintenant défier les autres joueurs")
        self.tournament_state = True
        self.tournament_state_label.set("Tournoi en cours")



    def click(self, event):
        (x,y) = event.x, event.y
        a = self.game_ui.canvas.find_overlapping(x, y, x, y)
        if len(a) == 1:
            rep = a[0]
            for point in self.game_ui.points:
                if point.rep == rep:
                    if self.state == PLAYING:
                        connection.Send({"action":"selectPoint", "nickname" : self.nickname,
                                "partners": self.currentGamePartners, "column" : point.i})
                    else:
                        self.game_ui.wrongSelection((point.i, point.j))


#########################################################

if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    exit()

host, port = sys.argv[1].split(":")
c = Client(host, int(port))
sleep(0.5)
# first loop to say to the server that I exist
c.Loop()
