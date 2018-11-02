import random
import numpy as np

from belot.gui.render import Renderer
from belot.engine.cards import cid2p, cid2s, cid2r, cid2t


class Tournament(object):

    def __init__(self, iters=10):
        self.iters = iters

    def showdown(self, players):
        results = []
        for i in range(self.iters):
            game = Game(players=[player(idx=i) for i, player in enumerate(players)], render=False)
            results.append(game.play_game())

        scores1, scores2 = zip(*results)
        print("Team 1 avg scores:", sum(scores1) / self.iters)
        print("Team 2 avg scores:", sum(scores2) / self.iters)


class Game(object):
    """Game class describes belot dynamics, constraints and internal states"""

    def __init__(self, players, states=None, render=False):

        self.players = players
        self.renderer = Renderer() if render else None

        if states:
            self.states = states
        else:
            self.states = {
                "round": 0,
                "on_table": np.array([0, 0, 0, 0]),
                "played": set(),
                "adut": 0,
                "first_player": 0,
                "scores": [0, 0]
            }

    def play_round(self):

        # Play cards
        for i in range(self.states["first_player"], self.states["first_player"] + 4):

            # Render game state
            if self.renderer:
                self.renderer.render(self.states, self.players[i % 4].states)

            self.states["on_table"][i % 4] = self.players[i % 4].play_card(self.states)

            # Render game state
            if self.renderer:
                self.renderer.render(self.states, self.players[i % 4].states)

        # Infer played cards suit and type
        on_table_suits = cid2s(self.states["on_table"])
        on_table_types = cid2t(self.states["on_table"])

        dominant_color = on_table_suits[self.states["first_player"]]

        # Infer played card strength(rank)
        on_table_rank = cid2r(self.states["on_table"], dominant_color, self.states["adut"])

        # Decide on a winner
        winner = np.argmax(on_table_rank)

        # Update states
        self.states["first_player"] = winner
        self.states["played"].update(self.states["on_table"])

        self.states["scores"][winner % 2] += cid2p(on_table_types, on_table_suits, self.states["adut"])
        if self.states["round"] == 7:
            self.states["scores"][winner % 2] += 10

        self.states["on_table"] = np.array([0, 0, 0, 0])

    def deal_cards(self):

        dealt_cards = {cid for player in self.players for cid in player.states["hand"]}

        # Shuffle unplayed and undealt cards
        cards = list({i for i in range(36)} - {0, 9, 18, 27} - dealt_cards - set(self.states["played"]))
        random.shuffle(cards)

        hand_card_num = 8 - len(self.states["played"]) // 4

        # Deal remaining cards
        for player in self.players:
            while len(player.states["hand"]) < hand_card_num:
                if cards[0] not in player.states["blacklist"]:
                    player.states["hand"].append(cards.pop(0))

        assert len(cards) == 0
        for player in self.players:
            assert len(player.states["hand"]) == hand_card_num

    def play_game(self):
        self.deal_cards()
        print([p.states["hand"] for p in self.players])

        while self.states["round"] < 8:
            self.play_round()
            self.states["round"] += 1

        return self.states["scores"]

    def copy_states(self, states=None):
        if not states:
            states = self.states
        return {
            i: j if isinstance(j, (str, int, float)) else j.copy()
            for i, j in states.items()
        }


class Player(object):

    def __init__(self, idx, states=None, render=None):

        if states:
            self.states = states
        else:
            self.states = {
                "idx": idx,
                "hand": [],
                "blacklist": set()
            }

    def legal_moves(self, game_state):

        self.states["blacklist"].update(np.arange(0, 36).tolist())

        hand = np.array(self.states["hand"])
        hand_suits = cid2s(hand)
        on_table_suits = cid2s(game_state["on_table"])

        if np.sum(game_state["on_table"]) == 0:
            return hand

        dominant_suit = cid2s(game_state["on_table"])[game_state["first_player"]]
        of_dominant_suit = hand[hand_suits == dominant_suit]
        of_adut = hand[hand_suits == game_state["adut"]]

        # Find strongest card of dominant suit on table
        if len(game_state["on_table"][on_table_suits == dominant_suit]) > 0:
            max_dominant = np.max(game_state["on_table"][on_table_suits == dominant_suit])
        else:
            max_dominant = 0

        # Find strongest adut on table
        if len(game_state["on_table"][np.logical_and(on_table_suits == game_state["adut"], on_table_suits != 0)]) > 0:
            max_adut = np.max(game_state["on_table"][on_table_suits == game_state["adut"]])
        else:
            max_adut = 0

        # Holding domainant suit cards?
        if len(of_dominant_suit) > 0:

            if max_adut > 0:
                return of_dominant_suit
            elif len(of_dominant_suit[of_dominant_suit > max_dominant]) == 0:
                # No stronger cards to play
                dominant_color_cards = np.arange(cid2t(max_dominant), 9) + dominant_suit * 9
                self.states["blacklist"].update((dominant_color_cards[dominant_color_cards > max_dominant]).tolist())
                return of_dominant_suit
            else:
                # Have to play stronger cards (uberovanje)
                return of_dominant_suit[of_dominant_suit > max_dominant]

        # No dominant suit cards - blacklisting
        self.states["blacklist"].update((np.arange(9) + dominant_suit * 9).tolist())

        # Holding adut cards?
        if len(of_adut) > 0:

            if len(of_adut[of_adut > max_adut]) > 0:
                # Have to play stronger cards (uberovanje)
                return of_adut[of_adut > max_adut]
            else:
                # No stronger cards to play
                return of_adut

        # No adut cards - blacklisting
        self.states["blacklist"].update((np.arange(9) + game_state["adut"] * 9).tolist())

        return hand

    def play_card(self, game_states):
        raise NotImplementedError

    def copy_states(self, states=None):
        if not states:
            states = self.states
        return {
            i: j if isinstance(j, (str, int, float)) else j.copy()
            for i, j in states.items()
        }


if __name__ == "__main__":

    from belot.agents.lib import Random

    trnmt = Tournament(iters=100)
    trnmt.showdown([Random, Random, Random, Random])
