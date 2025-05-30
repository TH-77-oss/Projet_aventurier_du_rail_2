import tkinter as tk
from graphic_interface.interface import GameApp
from graphic_interface.start_screen import *

# if __name__ == "__main__":
#     players = ['Victor', 'IA']
#     root = tk.Tk()
#     app = GameApp(root, players)
#     root.mainloop()

if __name__ == "__main__":
    # Créer et lancer l'écran d'accueil
    root = tk.Tk()
    start_screen = StartScreen(root)
    root.mainloop()