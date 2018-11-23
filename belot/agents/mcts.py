import random

import belot.engine.core as core
from belot.agents.lib import Random


class MCTS(core.Player):

    def __init__(self, idx, num_limit=100):
        super().__init__(idx)

        self.num_limit = num_limit
        self.crawler = None

    def play_card(self, game_states):

        self.crawler = MCTSCrawler(self.states["idx"])

        if len(self.states["hand"]) == 1:
            chosen_move = self.states["hand"][0]
        else:
            for n in range(self.num_limit):
                self.crawler.states = self.copy_states()

                bots = [
                    Random(i, states={"whitelist": game_states["whitelists"][i].copy()})
                    for i in range(4) if i != self.states["idx"]
                ]
                bots.insert(self.states["idx"], self.crawler)
                game = core.Game(bots, states=self.copy_states(game_states))
                self.crawler.gst.recursive_update(game.play_game()[self.states["idx"] % 2])

            chosen_move = self.crawler.gst.state_transition()
            assert chosen_move in self.legal_moves(game_states)

        self.states["hand"].pop(self.states["hand"].index(chosen_move))

        return chosen_move


class MCTSCrawler(core.Player):

    def __init__(self, idx):
        super().__init__(idx)
        self.gst = GameStateTree()

        self.gst.root = GameState(None, None)
        self.gst.selected = self.gst.root

    def play_card(self, game_states):

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
        best_move = max(self.root.next_states.values(), key=lambda x: x.avg_points).prev_move

        self.root = GameState(None, None)
        self.selected = self.root
        return best_move

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

    trnmt = core.Tournament(iters=300)
    trnmt.showdown([MCTS, Random, Random, Random], show_stats=True, render=False)
