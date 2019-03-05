# coding  = Latin-1
from tkinter import *
def mouse (evt):
    print(evt.keysym)

def color_hole(evt):
    if evt == '<Enter>':
        print("hello")

window = Tk()
window.title("Puissance 4")

C = Canvas(window, width = 725, height = 625, bg = "blue")
C.pack(side = LEFT)

places = list()

for i in range(7):
    liste = list()
    for j in range (6):
        liste.append(C.create_oval(25+ i*100, 25 + j*100, 100 + 100*i, 100 + 100*j, outline = "blue", fill = "white"))
    places.append(liste)

menu = Frame(window)
menu.pack(side = RIGHT)
quitter = Button(menu, text= "Quitter", command = window.destroy)
print(type(places[0][0]))
print(C.places[0][0])

print(places)

places[6][5].bind('<Enter>',mouse)
window.mainloop()
