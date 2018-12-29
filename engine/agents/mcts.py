import numpy as np

from engine.gui.render import Renderer
import matplotlib.pyplot as plt

import engine.core as core
from engine.agents.lib import Random


class MCTS(core.Player):

    def __init__(self, idx, num_limit=400):
        super().__init__(idx)

        self.num_limit = num_limit
        self.crawler = None
        self.renderer = Renderer()

    def play_card(self, game_states):

        self.crawler = MCTSCrawler(self.states["idx"])
        legal_moves = self.legal_moves(game_states)

        if len(legal_moves) == 1:
            chosen_move = legal_moves[0]
        else:
            for n in range(self.num_limit):
                self.crawler.states = self.copy_states()

                bots = [
                    Random(i, states={"whitelist": game_states["whitelists"][i].copy()})
                    for i in range(4) if i != self.states["idx"]
                ]
                bots.insert(self.states["idx"], self.crawler)
                game = core.Game(bots, states=self.copy_states(game_states), render=False)
                self.crawler.gst.recursive_update(game.play_game()[self.states["idx"] % 2])

            #print(self.crawler.gst.selected.next_states.values())
            #for move in self.crawler.gst.selected.next_states.values():
            #    plt.plot(list(range(len(move.avg_history))), move.avg_history)
            #plt.show()

            #self.renderer.render(game_states, self.states, [(cid2simb(state.prev_move), state.avg_points) for state in self.crawler.gst.root.next_states.values()])
            chosen_move = self.crawler.gst.state_transition()
            #print("CHOSEN MOVE: {}".format(chosen_move))

        assert chosen_move in legal_moves

        self.states["hand"].pop(self.states["hand"].index(chosen_move))

        return chosen_move


class MCTSCrawler(core.Player):

    def __init__(self, idx):
        super().__init__(idx)

        self.gst = GameStateTree()
        self.gst.root = GameState(None, None)
        self.gst.selected = self.gst.root

    def play_card(self, game_states):

        legal_moves = self.legal_moves(game_states)
        unvisited_moves = [
            legal_move
            for legal_move in legal_moves
            if legal_move not in self.gst.selected.next_states.keys()
        ]

        me = MoveExplorer("random", self.gst.selected, game_states)

        # Explore unvisited moves or choose play by UCT score
        if unvisited_moves:
            chosen_move = np.random.choice(unvisited_moves)
        else:
            chosen_move = me.choose_move(legal_moves)

        self.states["hand"].pop(self.states["hand"].index(chosen_move))

        # Update game state tree for move statistics
        self.gst.next(chosen_move)

        return chosen_move


class MoveExplorer(object):

    def __init__(self, criterion, selected_state, game_states):
        self.selected_state = selected_state
        self.game_states = game_states
        self.criterion_map = {
            "uct": self.uct,
            "exp3": self.exp3,
            "ts": self.ts,
            "random": self.random
        }
        self.choose_move = self.criterion_map[criterion]

    def uct(self, legal_moves):
        n = {state.prev_move: state.n for state in self.selected_state.next_states.values()}
        avg_points = {state.prev_move: state.avg_points for state in self.selected_state.next_states.values()}
        n_total = sum(n.values())

        chosen_move = max(
            legal_moves,
            key=lambda x: avg_points[x] + (162 - sum(self.game_states["scores"])) * np.sqrt(2 * np.log(n_total) / n[x])
        )

        return chosen_move

    def exp3(self):
        return

    @staticmethod
    def random(legal_moves):
        return np.random.choice(legal_moves)

    def ts(self, x):
        return


class GameStateTree(object):

    def __init__(self):
        self.root = None
        self.selected = None

    def state_transition(self):
        return max(self.root.next_states.values(), key=lambda x: x.avg_points).prev_move

    def recursive_update(self, points):

        while True:
            self.selected.n += 1
            self.selected.points += points
            self.selected.avg_points = self.selected.points / self.selected.n
            self.selected.avg_history.append(self.selected.avg_points)
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
        self.avg_history = []

    def __repr__(self):
        return "\nprev_move: {0}, n: {1}, points: {2}, avg_points: {3}, next_moves: {4}".format(
            self.prev_move,
            self.n,
            self.points,
            self.avg_points,
            str(len(self.next_states))
        )
