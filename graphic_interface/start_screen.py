from models.player import Player
from graphic_interface.interface import *
import tkinter as tk
from tkinter import messagebox
from collections import Counter
from PIL import Image, ImageTk
from tkinter import PhotoImage


class StartScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Les Aventuriers du Rail")

        # Récupérer les dimensions de l'écran
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Configuration en plein écran
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        # self.root.attributes('-fullscreen', True)  # Alternative pour un vrai plein écran

        # Charger et redimensionner l'image de fond
        try:
            self.bg_image = Image.open("data/start_screen_bg.jpg")
            self.bg_image = self.bg_image.resize((self.screen_width, self.screen_height), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'image de fond: {str(e)}")
            self.bg_photo = None

        # Créer un canvas pour l'interface
        self.canvas = tk.Canvas(root, width=self.screen_width, height=self.screen_height)
        self.canvas.pack(fill="both", expand=True)

        if self.bg_photo:
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        else:
            # Fallback si l'image ne charge pas
            self.canvas.configure(bg="#2c3e50")

        # Style moderne pour le bouton
        button_style = {
            'text': "Un ticket pour l'aventure",
            'font': ("Helvetica", 18, "bold"),
            'bg': "#e74c3c",
            'fg': "white",
            'activebackground': "#c0392b",
            'activeforeground': "white",
            'relief': tk.RAISED,
            'borderwidth': 3,
            'padx': 30,
            'pady': 15
        }

        # Création et positionnement du bouton
        self.start_btn = tk.Button(
            self.canvas,
            **button_style,
            command=self.start_game
        )

        # Positionnement en bas de l'écran (87% de la hauteur)
        self.canvas.create_window(
            self.screen_width // 2,
            self.screen_height * 0.87,
            window=self.start_btn
        )

        # Effets de survol
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(bg="#c0392b"))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(bg="#e74c3c"))

    def start_game(self):
        self.root.destroy()
        players = ['Victor', 'IA']
        game_root = tk.Tk()
        app = GameApp(game_root, players)
        game_root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    start_screen = StartScreen(root)
    root.mainloop()