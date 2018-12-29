class CardNode(object):

    def __init__(self, cards, deal_config=None, parent=None):
        self.children = []
        self.cards = cards
        self.deal_config = deal_config
        self.parent = parent
        self.tried_cards = []


class CardConfigTree(object):

    def __init__(self, cards, players):

        self.players = [(i, player) for i, player in enumerate(players) if not player.states["hand"]]

        prioritized_cards = sorted(
            cards,
            key=lambda x: sum([1 for player in self.players if x in player[1].states["whitelist"]]),
            reverse=False
        )

        self.root = CardNode(prioritized_cards[:], [[] for player in players if not player.states["hand"]], None)
        self.selected = self.root

        self.hand_card_num = len(cards) // len(self.players)

    def next(self):
        dealt = False
        for j, (i, player) in enumerate(self.players):

            if (self.selected.cards[0] in player.states["whitelist"]
                    and i not in self.selected.tried_cards
                    and len(self.selected.deal_config[j]) < self.hand_card_num):

                new_deal_config = [config[:] for config in self.selected.deal_config]
                new_deal_config[j].append(self.selected.cards[0])

                self.selected.children.append(CardNode(self.selected.cards[1:], new_deal_config, self.selected))
                self.selected.tried_cards.append(i)
                self.selected = self.selected.children[-1]
                dealt = True
                break

        if not dealt:
            if self.selected is self.root:
                assert False
            self.selected = self.selected.parent

        if self.selected.cards:
            return True

        return False


if __name__ == "__main__":

    from engine.core import Player

    players = [Player(i, {"whitelist": set(range(27))}) for i in range(3)]
    players[1].states["whitelist"] = {3, 7, 22, 9, 17, 12, 16, 19, 25}
    cct = CardConfigTree(list(range(27)), players)

    try:
        while cct.next():
            pass
    except AssertionError:
        print("Soulution not found...")

    print(cct.selected.deal_config)
    print([player.states["whitelist"] for player in players])
