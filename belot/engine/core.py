import time
import random
import numpy as np

from belot.gui.render import Renderer
from belot.engine.cards import cid2p, cid2s, cid2r, cid2t
from belot.agents.shuffling import CardConfigTree


class Tournament(object):

    def __init__(self, iters=10):
        self.iters = iters

    def showdown(self, players, render=False):
        results = []
        start = time.time()
        for i in range(self.iters):
            game = Game(players=[player(idx=i) for i, player in enumerate(players)], render=render)
            results.append(game.play_game())
            print(i)

        print("It took {} s per game".format((time.time() - start) / self.iters))

        scores1, scores2 = zip(*results)
        print("Team 1 avg scores:", sum(scores1) / self.iters)
        print("Team 2 avg scores:", sum(scores2) / self.iters)


class Game(object):
    """Game class describes belot dynamics, constraints and internal states"""

    def __init__(self, players, states=None, render=False):

        self.players = players
        self.renderer = Renderer() if render else None

        self.states = {
            "round": 0,
            "on_table": np.array([0, 0, 0, 0]),
            "played": set(),
            "adut": 0,
            "first_player": 0,
            "scores": [0, 0],
            "whitelists": [player.states["whitelist"] for player in self.players]
        }

        if states:
            self.states.update(states)

    def play_round(self):

        # Play cards
        for i in range(self.states["first_player"] + np.sum(self.states["on_table"] != 0),
                       self.states["first_player"] + np.sum(self.states["on_table"] != 0) + 4):

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

        cct = CardConfigTree(cards, players=self.players)

        while cct.next():
            pass

        card_configuration = cct.selected.deal_config

        for player in self.players:
            if not player.states["hand"]:
                player.states["hand"] = card_configuration.pop(0)

        assert True

    def play_game(self):
        self.deal_cards()

        while self.states["round"] < 8:
            self.play_round()
            self.states["round"] += 1

        return self.states["scores"]

    def copy_states(self, states=None):
        if not states:
            states = self.states
        return {
            i: j if isinstance(j, (str, int, float)) else [k.copy() for k in j] if i == "whitelists" else j.copy()
            for i, j in states.items()
        }


class Player(object):

    def __init__(self, idx, states=None, renderer=None):

        self.states = {
            "idx": idx,
            "hand": [],
            "whitelist": {i for i in range(36)} - {0, 9, 18, 27}
        }

        if states:
            self.states.update(states)

    def legal_moves(self, game_state):

        in_hand = np.array(self.states["hand"])
        on_table = game_state["on_table"]

        if game_state["first_player"] == self.states["idx"]:
            return in_hand

        in_hand_suits = cid2s(in_hand)
        on_table_suits = cid2s(on_table)

        dominant_suit = on_table_suits[game_state["first_player"]]
        adut_suit = game_state["adut"]

        in_hand_dominant = in_hand[in_hand_suits == dominant_suit]
        in_hand_adut = in_hand[in_hand_suits == adut_suit]

        on_table_dominant = on_table[on_table_suits == dominant_suit]
        on_table_adut = on_table[on_table_suits == adut_suit]

        has_dominant = True if len(in_hand_dominant) else False
        has_adut = True if len(in_hand_adut) else False

        is_game_sliced = True if len(on_table_adut) > 0 and dominant_suit != adut_suit else False

        if has_dominant:
            in_hand_max_dominant = np.max(cid2r(in_hand_dominant, dominant_suit, adut_suit))
            on_table_max_dominant = np.max(cid2r(on_table_dominant, dominant_suit, adut_suit))
            has_stronger_dominant = True if in_hand_max_dominant > on_table_max_dominant else False

            if has_stronger_dominant and not is_game_sliced:
                return in_hand_dominant[cid2r(in_hand_dominant, dominant_suit, adut_suit) > on_table_max_dominant]
            else:
                if not is_game_sliced:
                    all_dominant_ids = np.arange(9) + dominant_suit * 9
                    self.states["whitelist"] -= set(
                        all_dominant_ids[cid2r(all_dominant_ids, dominant_suit, adut_suit) > on_table_max_dominant]
                    )
                return in_hand_dominant
        else:
            # No dominant suit - blacklisting
            self.states["whitelist"] -= set(np.arange(9) + dominant_suit * 9)

            if has_adut:
                return in_hand_adut
            else:
                # No adut suit - blacklisting
                self.states["whitelist"] -= set(np.arange(9) + game_state["adut"] * 9)
                return in_hand

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

    trnmt = Tournament(iters=10)
    trnmt.showdown([Random, Random, Random, Random])

