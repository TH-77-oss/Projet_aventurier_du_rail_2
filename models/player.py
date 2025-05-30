import numpy.random as rnd

class Player:
    def __init__(self, name, color, is_ai = False):
        self.name = name
        self.color = color
        self.train_cards = []          # Liste des cartes wagons
        self.destination_cards = []    # À ajouter plus tard
        self.routes = []               # Les routes prises
        self.remaining_trains = 45     # Par défaut
        self.score = 0
        self.accomplished_objectives = []
        self.is_ai = is_ai

    def draw_card(self, card):
        if card != None:
            self.train_cards.append(card)
        else:
            return None

    def add_destination_card(self, card):
        self.destination_cards.append(card)

    def __repr__(self):
        return f'Player {self.name}'


    def player_aleatoire(self, coups_possible):
        return rnd.choice(coups_possible)