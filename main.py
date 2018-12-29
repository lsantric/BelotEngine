from engine.core import Tournament

from engine.agents.lib import Random
from engine.agents.mcts import MCTS

trnmt = Tournament(iters=100)
trnmt.showdown([MCTS, Random, MCTS, Random], show_stats=True, render=False, workers=8)
