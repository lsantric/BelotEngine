from engine.core import Player
from engine.cards import printCard

class Human(Player):

    def play_card(self, game_states):
        print('')
        print("Ruka", printCard(self.states["hand"]))
        print("Ploča", printCard(game_states["on_table"]))
        legal_moves = self.legal_moves(game_states)
        print("Legalci:", printCard(legal_moves))
        chosen_move = legal_moves[0]
        self.states["hand"].pop(self.states["hand"].index(chosen_move))
        return chosen_move