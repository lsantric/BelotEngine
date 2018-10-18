import random
import numpy as np

from agents import human
from engine.cards import cards_to_points
from gui.render import Renderer


class Game(object):
    """Game class describes belot dynamics and internal states"""

    def __init__(self, players, states=None):

        self.players = players
        self.renderer = Renderer()

        # Enumerate players and fix their position on the table
        for i, player in enumerate(players):
            player.idx = i

        if states:
            self.states = states
        else:
            self.states = {
                "on_table": np.array([0, 0, 0, 0]),
                "played": set(),
                "adut": 0,
                "first_player": 0,
                "scores": [0, 0]
            }

    def play_round(self, round_id):

        # Throw cards
        for i in range(self.states["first_player"], self.states["first_player"] + 4):
            self.renderer.render(self.states, self.players[i % 4].states)
            self.states["on_table"][i % 4] = self.players[i % 4].play_card(self.states)
            self.renderer.render(self.states, self.players[i % 4].states)

        # Infer played card color and type
        on_table_colors = self.states["on_table"] // 9
        on_table_cards = self.states["on_table"] % 9

        dominant_color = on_table_colors[self.states["first_player"]]

        # Adjust car strength multipliers
        on_table_strength = on_table_cards.copy()
        on_table_strength[on_table_colors == dominant_color] += 10
        on_table_strength[on_table_colors == self.states["adut"]] += 20
        on_table_strength[on_table_strength == 2] += 20
        on_table_strength[on_table_strength == 3] += 20

        # Decide on a winner
        winner = np.argmax(on_table_strength)

        # Update states
        self.states["first_player"] = winner
        self.states["played"].update(self.states["on_table"])

        self.states["scores"][winner % 2] += cards_to_points(on_table_cards, on_table_colors, self.states["adut"])
        if round_id == 7:
            self.states["scores"][winner % 2] += 10

        self.states["on_table"] = np.array([0, 0, 0, 0])

    def deal_cards(self):
        cards = [i for i in range(1, 36) if i not in (9, 18, 27)]
        random.shuffle(cards)

        for i, player in enumerate(self.players):
            player.states["hand"] = cards[8 * i: 8 * (i + 1)]

    def play_game(self):
        self.deal_cards()
        for i in range(8):
            self.play_round(i)
            print(self.states)


class Player(object):

    def __init__(self, states=None):

        if states:
            self.states = states
        else:
            self.states = {
                "hand": None
            }

    def legal_moves(self, game_state):
        hand = np.array(self.states["hand"])
        if len(game_state["on_table"]) == 0:
            return hand
        dominant_color = game_state["on_table"][game_state["first_player"]]
        of_dominant_color = hand[hand // 9 == dominant_color]
        of_adut = hand[hand // 9 == game_state["adut"]]
        if len(game_state["on_table"][game_state["on_table"] // 9 == dominant_color]) > 0:
            max_dominant = np.max(game_state["on_table"][game_state["on_table"] // 9 == dominant_color])
        else:
            max_dominant = 0

        if len(game_state["on_table"][game_state["on_table"] // 9 == game_state["adut"]]) > 0:
            max_adut = np.max(game_state["on_table"][game_state["on_table"] // 9 == game_state["adut"]])
        else:
            max_adut = 0

        if len(of_dominant_color) != 0:
            if max_adut > 0:
                return of_dominant_color
            elif len(of_dominant_color[of_dominant_color > max_dominant]) == 0:
                return of_dominant_color
            else:
                return of_dominant_color[of_dominant_color > max_dominant]
        elif len(of_adut) > 0:
            if len(of_adut[of_adut > max_adut]) > 0:
                return of_adut[of_adut > max_adut]
            else:
                return of_adut

        return hand

    def play_card(self, game_states):
        raise NotImplementedError


if __name__ == "__main__":
    a = Game([human.Human(), human.Human(), human.Human(), human.Human()])
    import time
    start = time.time()
    a.play_game()
    print(time.time() - start)
