# coding  = Latin-1
from tkinter import *

window = Tk()

C = Canvas(window, width = 725, height = 625, bg = "blue")
C.pack()

places = list()

for i in range(7):
    liste = list()
    for j in range (6):
        liste.append(C.create_oval(25+ i*100, 25 + j*100, 100 + 100*i, 100 + 100*j, outline = "blue", fill = "white"))
    places.append(liste)


window.mainloop()
