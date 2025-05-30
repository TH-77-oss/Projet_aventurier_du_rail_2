import tkinter as tk
from tkinter import messagebox
from collections import Counter
from PIL import Image, ImageTk
from tkinter import PhotoImage
from game import Game
import random
import math
import json
import tkinter.simpledialog as simpledialog
from data.data import *



class GameApp:
    def __init__(self, root, players):
        self.root = root
        self.root.title("Les Aventuriers du Rail - USA")
        self.width = 1100
        self.height = 580
        self.larg_left_col = 300
        self.width_canvas = self.width - self.larg_left_col
        self.height_canvas = self.height
        self.root.geometry(f"{self.width}x{self.height}")
        #self.root.minsize(self.width, self.height)
        self.game = Game(players)
        with open("data/destinations.json", "r", encoding="utf-8") as f:
            self.all_routes = json.load(f)  # Toutes les routes du jeu
        self.game.routes = self.all_routes  # Donne accès à Game
        self.selected_cities = []

        with open("data/villes.json", "r", encoding="utf-8") as f:
            self.villes = json.load(f)

        #with open("data/destinations.json", "r", encoding="utf-8") as f:
        #    self.routes = json.load(f)

        self.game.start_game()
        self.bg_image_tk = None  # Stockage image fond

        self.setup_ui()

    def setup_ui(self):

        from PIL import Image, ImageTk

        self.card_images = {
            color: ImageTk.PhotoImage(Image.open(f"data/{color}.jpg").resize((25, 12)))
            for color in ["blue", "red", "green", "yellow", "black", "white", "orange" ,"pink", "locomotive"]
        }

        # 🧱 Cadre principal horizontal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ⬅️ Colonne gauche : Infos joueur
        # Canvas défilant à gauche
        left_canvas = tk.Canvas(main_frame, width=self.larg_left_col)
        left_canvas.pack(side=tk.LEFT, fill=tk.Y)
        left_canvas.pack_propagate(False)

        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=left_canvas.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        # Frame contenant tous les éléments
        left_frame = tk.Frame(left_canvas)
        left_canvas.create_window((0, 0), window=left_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=scrollbar.set)

        # Mise à jour du scroll lorsque le contenu change
        def on_configure(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))

        left_frame.bind("<Configure>", on_configure)

        # Activer le scroll avec la molette
        def _on_mousewheel(event):
            left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        left_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ➡️ Colonne droite : Carte
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


        # 🧑‍💼 Joueur actuel
        self.player_label = tk.Label(left_frame, text="", font=("Helvetica", 14, "bold"))
        self.player_label.pack(pady=10)

        # 🎮 Boutons d'action
        actions_frame = tk.Frame(left_frame)
        actions_frame.pack(pady=15)

        tk.Button(actions_frame, text="Piocher wagon", command=self.draw_card).pack(pady=2)
        tk.Button(actions_frame, text="Piocher objectif", command=self.draw_objectives).pack(pady=2)
        tk.Button(actions_frame, text="Passer tour", command=self.next_turn).pack(pady=2)

        # 🎴 Cartes wagon
        self.hand_label = tk.Label(left_frame, text="Cartes en main :", font=("Helvetica", 12), anchor="center", justify="center")
        self.hand_label.pack()
        self.cards_frame = tk.Frame(left_frame)
        self.cards_frame.pack(pady=5)

        # 🎯 Objectifs
        self.objectives_label = tk.Label(left_frame, text="Objectifs :", font=("Helvetica", 12), anchor="center", justify="center")
        self.objectives_label.pack(pady=10)
        self.objectives_frame = tk.Frame(left_frame)
        self.objectives_frame.pack()

        # Objectifs réussis
        self.accomplished_label = tk.Label(left_frame, text="Objectifs atteints :", font=("Helvetica", 12), anchor="center", justify="center")
        self.accomplished_label.pack(pady=10)
        self.accomplished_frame = tk.Frame(left_frame)
        self.accomplished_frame.pack()

        # 🃏 Cartes visibles
        self.visible_label = tk.Label(left_frame, text="Cartes visibles :", font=("Helvetica", 12), anchor="center" ,justify="center")
        self.visible_label.pack(pady=10)
        self.visible_frame = tk.Frame(left_frame)
        self.visible_frame.pack()

        # 🗺️ Canvas carte (grande zone)
        self.canvas = tk.Canvas(right_frame, width=self.width_canvas, height=self.height_canvas, bg="white")
        self.canvas.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Initialisation
        self.draw_graph()
        self.update_turn_display()
        self.afficher_main_cartes(self.game.current_player)
        self.update_objectives_display()
        # self.update_visible_cards()


    def draw_graph(self):
        city_coords = {
            entry["city"]: (
                entry["i"] / 100 * self.width_canvas,
                self.height_canvas - entry["j"] / 100 * self.height_canvas
            )
            for entry in self.villes
        }

        self.canvas.delete("all")

        image = Image.open("data/USA_map.jpg").resize((int(self.width_canvas), int(self.height_canvas)))
        self.bg_image_tk = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.bg_image_tk, anchor="nw")

        # Regrouper manuellement les routes par paire de villes
        route_groups = []
        for route in self.all_routes:
            found = False
            for group in route_groups:
                if sorted([route["city1"], route["city2"]]) == sorted([group[0]["city1"], group[0]["city2"]]):
                    group.append(route)
                    found = True
                    break
            if not found:
                route_groups.append([route])

        for group in route_groups:
            route = group[0]
            city1 = route["city1"]
            city2 = route["city2"]

            if city1 in city_coords and city2 in city_coords:
                x1, y1 = city_coords[city1]
                x2, y2 = city_coords[city2]
                dx, dy = x2 - x1, y2 - y1
                length = math.hypot(dx, dy)
                offset_x, offset_y = -dy / length * 6, dx / length * 6  # perpendiculaire

                for i, route in enumerate(group):
                    shift = (i - (len(group) - 1) / 2)  # pour centrer
                    ox = offset_x * shift
                    oy = offset_y * shift

                    color = route.get("color", "gray")
                    points = route["length"]

                    # Vérifie si cette route est revendiquée
                    claimed = None
                    for player in self.game.players:
                        if (route["city1"], route["city2"]) in player.routes or (
                        route["city2"], route["city1"]) in player.routes:
                            color = player.color
                            claimed = player
                            break

                    self.canvas.create_line(x1 + ox, y1 + oy, x2 + ox, y2 + oy, fill=color, width=4)

                    if not claimed:
                        mx, my = (x1 + x2) / 2 + ox, (y1 + y2) / 2 + oy
                        self.canvas.create_text(mx, my, text=str(points), font=("Helvetica", 8), fill="darkred")

        # Villes
        for city, (x, y) in city_coords.items():
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="lightblue", outline="black")
            self.canvas.create_text(x, y - 10, text=city, font=("Helvetica", 11, 'bold'), fill="black")

        self.city_coords = city_coords
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.selected_cities = []

    # ---------------------------------- INTERACTION CARTE --------------------------------------------
    def on_canvas_click(self, event):
        # Déterminer quelle ville est cliquée
        for city, (x, y) in self.city_coords.items():
            if abs(event.x - x) < 8 and abs(event.y - y) < 8:
                self.selected_cities.append(city)

                # Ajouter un cercle rouge temporaire
                self.canvas.create_oval(x - 8, y - 8, x + 8, y + 8, outline="red", width=2)
                break

        if len(self.selected_cities) == 2:
            city1, city2 = self.selected_cities

            self.selected_cities.clear()

            # Tenter de revendiquer la route
            self.attempt_claim_route(city1, city2)
            self.update()

    def attempt_claim_route(self, city1, city2):
        if (city1, city2) in self.game.current_player.routes:
            return
        for route in self.all_routes:
            if {route["city1"], route["city2"]} == {city1, city2}:
                answer = tk.messagebox.askyesno("Revendiquer la route", f"{city1} ↔ {city2} ?")
                if answer:
                    self.claim_route(city1, city2, route)
                return

    def claim_route(self, city1, city2, route):
        player = self.game.current_player
        length = route["length"]
        route_color = route.get("color", "gray")

        if route_color == "gray":
            color_counts = {}
            loco_count = 0
            for card in player.train_cards:
                if card.lower() == "locomotive":
                    loco_count += 1
                else:
                    color_counts[card.lower()] = color_counts.get(card.lower(), 0) + 1

            # Trouver les couleurs possibles
            possible_colors = [color for color, count in color_counts.items() if count + loco_count >= length]
            if not possible_colors:
                messagebox.showwarning("Pas assez de cartes",
                                       f"{player.name} n’a pas assez de cartes d’une couleur (ou locomotives) pour prendre cette route.")
                return

            # Si plusieurs couleurs possibles, demander à l'utilisateur
            if len(possible_colors) > 1 and not player.is_ai:
                # Exemple simplifié : demander la couleur via une boîte de dialogue
                color_choice = simpledialog.askstring("Choix couleur",
                                                         f"Choisissez la couleur pour la route grise parmi {possible_colors}")
                if not color_choice or color_choice.lower() not in possible_colors:
                    messagebox.showinfo("Annulé", "Aucune couleur valide sélectionnée.")
                    return
                chosen_color = color_choice.lower()
            else:
                # Si IA ou une seule couleur possible
                chosen_color = possible_colors[0]

            removed = 0
            new_hand = []
            locomotives_used = 0
            for card in player.train_cards:
                card_lower = card.lower()
                if removed < length and card_lower == chosen_color:
                    removed += 1
                elif removed < length and card_lower == "locomotive":
                    removed += 1
                    locomotives_used += 1
                else:
                    new_hand.append(card)
            player.train_cards = new_hand

            if locomotives_used > 0:
                messagebox.showinfo("Locomotives utilisées",
                                    f"{player.name} utilise {locomotives_used} locomotive(s) pour compléter la route.")

        else:
            # Gestion classique pour les routes colorées
            color_counts = {}
            loco_count = 0
            for card in player.train_cards:
                if card.lower() == "locomotive":
                    loco_count += 1
                else:
                    color_counts[card.lower()] = color_counts.get(card.lower(), 0) + 1

            if color_counts.get(route_color.lower(), 0) + loco_count < length:
                messagebox.showwarning("Pas assez de cartes", f"{player.name} n’a pas {length} cartes {route_color}.")
                return

            removed = 0
            new_hand = []
            locomotives_used = 0
            for card in player.train_cards:
                card_lower = card.lower()
                if removed < length and card_lower == route_color.lower():
                    removed += 1
                elif removed < length and card_lower == "locomotive":
                    removed += 1
                    locomotives_used += 1
                else:
                    new_hand.append(card)
            player.train_cards = new_hand

            if locomotives_used > 0:
                messagebox.showinfo("Locomotives utilisées",
                                    f"{player.name} utilise {locomotives_used} locomotive(s) pour compléter la route.")

        player.routes.append((city1, city2))
        player.score += self.game.SCORE_TABLE.get(length, length)
        messagebox.showinfo("Route revendiquée", f"{player.name} a pris la route {city1} ↔ {city2} !")
        self.update_objectif_accompli()

    def update(self):
        #self.update_hand_display()
        self.afficher_main_cartes(self.game.current_player)
        self.update_turn_display()
        self.update_objectives_display()
        self.update_accomplished_display()# Très important pour affichage joueur actuel
        self.draw_graph()

    # -------------------------------------- TIRAGE -----------------------------------------------
    def draw_objectives(self):
        # Utilise self.game au lieu d'appeler directement
        drawn = self.game.draw_destination_cards(3)

        if not drawn:
            tk.messagebox.showinfo("Objectifs", "Il n'y a plus d'objectifs à piocher.")
            return

        player = self.game.current_player
        msg = "Objectifs tirés :\n" + "\n".join(
            f"{c['city1']} → {c['city2']} ({c['length']} pts)" for c in drawn
        )
        tk.messagebox.showinfo("Nouveaux objectifs", msg)

        for card in drawn:
            player.add_destination_card(card)

        self.update_objectives_display()

    def draw_card(self):
        self.game.player_draw_cards(1)
        self.afficher_main_cartes(self.game.current_player)

    def visible_card_draw(self, index):
        self.game.visible_card_draw(index)
        self.afficher_main_cartes(self.game.current_player)

    # -------------------------------------- UPDATE -----------------------------------------------
    def update_hand_display(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        current = self.game.current_player
        max_per_row = 4  # nombre de cartes par ligne

        for i, card in enumerate(current.train_cards):
            row = i // max_per_row
            col = i % max_per_row
            card_label = tk.Label(self.cards_frame, text=card, relief=tk.RIDGE, borderwidth=2, padx=5, pady=2)
            card_label.grid(row=row, column=col, padx=2, pady=2, sticky="w")

    def get_color_hex(self, color):
        color_map = {
            "red": "#d9534f",
            "blue": "#0275d8",
            "green": "#5cb85c",
            "yellow": "#f0ad4e",
            "black": "#292b2c",
            "white": "#f7f7f7",
            "pink": "#ff69b4",
            "orange": "#f26522",
            "joker": "#cccccc",
            "gray": "#aaaaaa"
        }
        return color_map.get(color.lower(), "gray")


    def update_objectives_display(self):
        for widget in self.objectives_frame.winfo_children():
            widget.destroy()

        current = self.game.current_player
        max_per_row = 1  # par exemple : 1 objectifs par ligne

        for i, obj in enumerate(current.destination_cards):
            row = i // max_per_row
            col = i % max_per_row
            obj_text = f"{obj['city1']} → {obj['city2']} ({obj['length']} pts)"
            obj_label = tk.Label(self.objectives_frame, text=obj_text, relief=tk.SOLID, borderwidth=1, padx=4, pady=2)
            obj_label.grid(row=row, column=col, padx=3, pady=3, sticky="w")

    def update_objectif_accompli(self):
        current = self.game.current_player
        accomplished = []

        for obj in current.destination_cards[:]:
            if self.is_objective_completed(obj):
                current.destination_cards.remove(obj)
                current.accomplished_objectives.append(obj)
                # Ajouter les points de l'objectif au score
                current.score += obj['length']/2
                # Afficher un message
                messagebox.showinfo("Objectif accompli",
                                    f"{current.name} a accompli l'objectif {obj['city1']} → {obj['city2']} et gagne {obj['length']} points!")

        self.update_objectives_display()
        self.update_accomplished_display()
        self.update_turn_display()  # Pour afficher le nouveau score

    def is_objective_completed(self, objective):
        from collections import deque

        graph = {}
        for c1, c2 in self.game.current_player.routes:
            graph.setdefault(c1, []).append(c2)
            graph.setdefault(c2, []).append(c1)

        start = objective['city1']
        target = objective['city2']
        visited = set()
        queue = deque([start])

        while queue:
            city = queue.popleft()
            if city == target:
                return True
            if city not in visited:
                visited.add(city)
                queue.extend(graph.get(city, []))

        return False

    def update_accomplished_display(self):
        for widget in self.accomplished_frame.winfo_children():
            widget.destroy()

        self.update_objectives_display()

        current = self.game.current_player
        for i, obj in enumerate(current.accomplished_objectives):
            obj_text = f"{obj['city1']} → {obj['city2']} ({obj['length']} pts)"
            obj_label = tk.Label(self.accomplished_frame, text=obj_text, relief=tk.GROOVE, bg="lightgreen", padx=4,
                                 pady=2)
            obj_label.pack(padx=2, pady=2, anchor="w")

    def update_turn_display(self):
        current = self.game.current_player
        self.player_label.config(text=f"Joueur : {current.name} - Score : {current.score} points")


    def afficher_main_cartes(self, player):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        counts = Counter(player.train_cards)

        for idx, (color, count) in enumerate(counts.items()):
            row = idx // 4
            col = idx % 4
            frame = tk.Frame(self.cards_frame)
            frame.grid(row=row, column=col, padx=5, pady=5)

            img_label = tk.Label(frame, image=self.card_images[color])
            img_label.image = self.card_images[color]
            img_label.pack(side="top")

            count_label = tk.Label(frame, text=f"x{count}", font=("Arial", 10))
            count_label.pack(side="top")

    def next_turn(self):
        self.game.next_turn()
        self.afficher_main_cartes(self.game.current_player)
        self.update_turn_display()
        self.update_objectives_display()
        self.update_accomplished_display()

        # Si c'est à l'IA de jouer, lance son tour
        if self.game.current_player.is_ai:
            self.play_ai_turn()

    def coups_possibles(self, player=None):
        if player is None:
            player = self.current_player

        possible_moves = []

        # 1. Piocher une carte wagon face cachée
        if self.train_deck:
            possible_moves.append(("draw_train_card", None))

        # 2. Piocher une carte visible
        for idx, card in enumerate(self.visible_cards):
            possible_moves.append(("draw_visible_card", idx))

        # 3. Piocher des cartes destination
        if len(self.destinations) >= 3:
            possible_moves.append(("draw_destinations", None))

        # 4. Revendiquer une route - PARTIE CRUCIALE
        cards_counter = Counter([c.lower() for c in player.train_cards])
        locos = cards_counter.get("locomotive", 0)

        print(f"\n{player.name} possède: {dict(cards_counter)} (total: {len(player.train_cards)} cartes)")

        for route in self.all_routes:
            city1, city2 = route["city1"], route["city2"]
            length = route["length"]
            color = route.get("color", "gray").lower()

            # Vérifier si la route est déjà prise
            route_taken = any(
                (city1, city2) in p.routes or (city2, city1) in p.routes
                for p in self.players
            )
            if route_taken:
                continue

            # Vérifier si le joueur a assez de wagons
            if len(player.train_cards) < length:
                continue

            # Pour les routes grises
            if color == "gray":
                for c in WAGON_COLORS:
                    if c == "locomotive":
                        continue
                    count = cards_counter.get(c, 0)
                    if count + locos >= length:
                        possible_moves.append(("claim_route", (city1, city2, c, length)))
                        print(f"Route possible (gris): {city1}-{city2} avec {c} ({count}+{locos} locos)")
                        break
            else:
                # Pour les routes colorées
                count = cards_counter.get(color, 0)
                if count + locos >= length:
                    possible_moves.append(("claim_route", (city1, city2, color, length)))
                    print(f"Route possible ({color}): {city1}-{city2}")

        # 5. Passer
        possible_moves.append(("pass", None))

        print(f"Total coups possibles: {len(possible_moves)}")
        return possible_moves

    def play_random_move(self):
        player = self.game.current_player
        if not player.is_ai:
            return False

        # Pioche des objectifs si nécessaire
        if len(player.destination_cards) == 0:
            self.draw_objectives()
            self.update()
            self.next_turn()
            return True

        possible_moves = self.game.coups_possibles(player)
        print(f"\nCoups possibles pour {player.name}:")
        for i, (action, param) in enumerate(possible_moves):
            print(f"{i}. {action} {param if param else ''}")

        if not possible_moves:
            self.next_turn()
            return False

        move = random.choice(possible_moves)
        action, param = move

        if action == "draw_train_card":
            self.draw_card()
        elif action == "draw_visible_card":
            self.visible_card_draw(param)
        elif action == "draw_destinations":
            self.draw_objectives()
        elif action == "claim_route":
            city1, city2, color, length = param
            # Trouver la route correspondante dans all_routes
            for route in self.all_routes:
                if ({route["city1"], route["city2"]} == {city1, city2} and
                        str(route["length"]) == str(length) and
                        route.get("color", "gray").lower() == color):
                    print(f"\n{player.name} tente de prendre {city1}-{city2} ({color})")
                    self.claim_route(city1, city2, route)
                    break
        elif action == "pass":
            pass

        self.update()
        self.next_turn()
        return True

    def play_ai_turn(self):
        if not self.game.current_player.is_ai:
            return

        # Exécute le mouvement de l'IA après un court délai
        self.root.after(1000, self.execute_ai_move)

    def execute_ai_move(self):
        if not self.game.current_player.is_ai:
            return

        self.play_random_move()

        # Si c'est encore à l'IA de jouer (cas rare), on relance
        if self.game.current_player.is_ai:
            self.root.after(1000, self.play_ai_turn)