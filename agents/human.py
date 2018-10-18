from engine.core import Player
from engine.cards import print_card


class Human(Player):

    def play_card(self, game_states):
        print("\nRuka", print_card(self.states["hand"]))
        print("Plochka", print_card(game_states["on_table"]))
        legal_moves = self.legal_moves(game_states)
        print("Legalci:", print_card(legal_moves))
        chosen_move = legal_moves[0]
        self.states["hand"].pop(self.states["hand"].index(chosen_move))
        return chosen_move
