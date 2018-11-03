import random
import time

import belot.engine.core as core
from belot.agents.lib import Random


class MCTS(core.Player):

    def __init__(self, idx, time_limit=0.5):
        super().__init__(idx)

        self.time_limit = time_limit

        self.gst = GameStateTree()
        self.crawler = MCTSCrawler(idx, self.gst)

    def play_card(self, game_states):

        if len(self.states["hand"]) == 1:
            chosen_move = self.states["hand"][0]
        else:
            start = time.time()
            while (time.time() - start) < self.time_limit:
                self.crawler.states = self.copy_states()

                bots = [Random(i) for i in range(4) if i != self.states["idx"]]
                bots.insert(self.states["idx"], self.crawler)

                game = core.Game(bots, states=self.copy_states(game_states))
                self.gst.recursive_update(game.play_game()[self.states["idx"] % 2])

            chosen_move = self.gst.state_transition()

        self.states["hand"].pop(self.states["hand"].index(chosen_move))

        return chosen_move


class MCTSCrawler(core.Player):

    def __init__(self, idx, gst):
        super().__init__(idx)
        self.gst = gst

    def play_card(self, game_states):

        if not self.gst.root:
            self.gst.root = GameState(None, None)
            self.gst.selected = self.gst.root

        # Make legal move at random
        legal_moves = self.legal_moves(game_states)
        chosen_move = legal_moves[random.randint(0, len(legal_moves) - 1)]
        self.states["hand"].pop(self.states["hand"].index(chosen_move))

        # Update game state tree for move statistics
        self.gst.next(chosen_move)

        return chosen_move


class GameStateTree(object):

    def __init__(self):
        self.root = None
        self.selected = None

    def state_transition(self):
        self.root = max(self.root.next_states.values(), key=lambda x: x.avg_points)
        self.selected = self.root
        return self.root.prev_move

    def recursive_update(self, points):

        while True:
            self.selected.n += 1
            self.selected.points += points
            self.selected.avg_points = self.selected.points / self.selected.n
            if self.selected is self.root:
                break
            else:
                self.selected = self.selected.prev_state

    def prev(self):
        if self.selected is self.root:
            return False

        self.selected = self.selected.prev_state
        return True

    def next(self, move):
        if move in self.selected.next_states:
            self.selected = self.selected.next_states[move]
        else:
            self.selected.next_states[move] = GameState(self.selected, move)
            self.selected = self.selected.next_states[move]


class GameState(object):

    def __init__(self, prev_state, prev_move):

        self.prev_move = prev_move
        self.prev_state = prev_state
        self.next_states = {}

        self.n = 0
        self.points = 0
        self.avg_points = 0


if __name__ == "__main__":

    trnmt = core.Tournament(iters=200)
    trnmt.showdown([MCTS, Random, Random, Random])
