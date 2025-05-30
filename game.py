import random
from data.data import *
from models.player import Player
import json
from collections import Counter

class Game:
    def __init__(self, players):
        self.players = []
        for i, player_info in enumerate(players):
            # Si c'est un string (ancienne version), on convertit
            if isinstance(player_info, str):
                player_info = {'name': player_info, 'is_ai': player_info == 'IA'}

            # Création du joueur avec les paramètres par défaut
            self.players.append(Player(
                name=player_info['name'],
                color=PLAYER_COLORS[i],
                is_ai=player_info.get('is_ai', False)  # False par défaut
            ))

        self.current_player_index = 0
        self.train_deck = WAGON_COLORS * 12
        random.shuffle(self.train_deck)

        self.SCORE_TABLE = {}

        with open("data/destinations.json", "r", encoding="utf-8") as f:
            self.destinations = json.load(f)

        self.visible_cards = []
        for _ in range(5):
            if self.train_deck:
                self.visible_cards.append(self.train_deck.pop())

        self.routes = []

    def start_game(self):
        for player in self.players:
            for _ in range(4):
                if self.train_deck:
                    player.draw_card(self.train_deck.pop())

    def get_visible_cards(self):
        return self.visible_cards

    def draw_destination_cards(self, count=3):
        cards = []
        for _ in range(count):
            if self.destinations:
                cards.append(self.destinations.pop())
        return cards

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def draw_train_card(self):
        if self.train_deck:
            return self.train_deck.pop()
        return None

    def player_draw_cards(self, nb_cards):
        for _ in range(nb_cards):
            card = self.draw_train_card()
            if card:
                self.current_player.draw_card(card)

    def visible_card_draw(self, index):
        if 0 <= index < len(self.visible_cards):
            card = self.visible_cards[index]
            self.current_player.train_cards.append(card)
            if self.train_deck:
                self.visible_cards[index] = self.train_deck.pop()
            else:
                del self.visible_cards[index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def is_route_useful(self, player, city1, city2):
        # Construction du graphe actuel des routes du joueur
        graph = {}
        for c1, c2 in player.routes:
            graph.setdefault(c1, set()).add(c2)
            graph.setdefault(c2, set()).add(c1)

        # Ajout temporaire de la route candidate
        graph.setdefault(city1, set()).add(city2)
        graph.setdefault(city2, set()).add(city1)

        # Vérifie pour chaque objectif si un chemin existe
        def dfs(current, target, visited):
            if current == target:
                return True
            visited.add(current)
            for neighbor in graph.get(current, []):
                if neighbor not in visited and dfs(neighbor, target, visited):
                    return True
            return False

        for obj in player.destination_cards:
            start = obj.get("from") or obj.get("city1")
            end = obj.get("to") or obj.get("city2")
            if not start or not end:
                continue

            if dfs(start, end, set()):
                return True  # Cette route aide à atteindre un objectif

        return False  # Route inutile à tout objectif

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

        # 3. Piocher des cartes destination (s’il en reste au moins 3)
        if len(self.destinations) >= 3:
            possible_moves.append(("draw_destinations", None))

        # 4. Revendiquer une route
        cards = Counter([c.lower() for c in player.train_cards])
        locos = cards.get("locomotive", 0)

        print(f"{player.name} possède : {dict(cards)} - {player.train_cards} wagons")

        for route in self.routes:
            city1, city2 = route["city1"], route["city2"]
            length = route["length"]
            color = route.get("color", "gray").lower()

            # Vérifier si route déjà prise
            route_taken = any(
                (city1, city2) in p.routes or (city2, city1) in p.routes
                for p in self.players
            )
            if route_taken:
                continue

            # Pour l'IA : ignorer les routes qui ne sont pas utiles aux objectifs
            if player.is_ai and not self.is_route_useful(player, city1, city2):
                continue

            # Vérifie assez de wagons
            if len(player.train_cards) < length:
                continue

            # Route grise : tester toutes les couleurs possibles
            if color == "gray":
                for c in WAGON_COLORS:
                    count = cards.get(c, 0)
                    if count + locos >= length:
                        possible_moves.append(("claim_route", (city1, city2, color, length)))
                        print(f"→ Possibilité IA : claim_route GRAY {city1} ↔ {city2} avec {c} + {locos} loco(s)")
                        break
            else:
                if cards.get(color, 0) + locos >= length:
                    possible_moves.append(("claim_route", (city1, city2, color, length)))
                    print(
                        f"→ Possibilité IA : claim_route {color} {city1} ↔ {city2} avec {cards.get(color, 0)} + {locos} loco(s)")

        # 5. Passer
        possible_moves.append(("pass", None))

        return possible_moves

    def play_random_move(self):
        player = self.current_player

        # Si l'IA n'a pas encore d'objectifs, elle doit en piocher
        if player.is_ai and len(player.destination_cards) == 0:
            new_objectives = self.draw_destination_cards(3)
            for obj in new_objectives:
                player.add_destination_card(obj)
            return True  # Un tour utilisé à tirer des objectifs

        possible_moves = self.coups_possibles()
        if not possible_moves:
            return False

        move = random.choice(possible_moves)
        action, param = move

        if action == "draw_train_card":
            self.player_draw_cards(1)
        elif action == "draw_visible_card":
            self.visible_card_draw(param)
        elif action == "claim_route":
            pass
        elif action == "pass":
            pass

        self.next_turn()
        return True

