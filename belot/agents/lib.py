import random
import belot.engine.core as core


class Human(core.Player):

    def play_card(self, game_states):
        legal_moves = self.legal_moves(game_states)
        chosen_move = legal_moves[0]
        self.states["hand"].pop(self.states["hand"].index(chosen_move))
        return chosen_move


class Random(core.Player):

    def play_card(self, game_states):
        legal_moves = self.legal_moves(game_states)
        chosen_move = legal_moves[random.randint(0, len(legal_moves) - 1)]
        self.states["hand"].pop(self.states["hand"].index(chosen_move))
        return chosen_move
