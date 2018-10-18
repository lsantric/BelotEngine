import cv2
import numpy as np

from gui.layout import hand_cards, table_cards


class Renderer(object):

    def __init__(self):
        background = cv2.imread("../gui/assets/table.jpg", cv2.IMREAD_ANYCOLOR)

        card_width = int(background.shape[1] * (hand_cards[0][2] - hand_cards[0][0]))
        card_height = int(background.shape[1] * (hand_cards[0][2] - hand_cards[0][0]) / 0.655)

        self.resources = {
            i: cv2.resize(cv2.imread("../gui/assets/{}.jpg".format(i), cv2.IMREAD_ANYCOLOR),
                          (card_width, card_height),
                          interpolation=cv2.INTER_CUBIC)
            for i in range(36)
        }

        self.resources["background"] = background

        self.card_width = card_width
        self.card_height = card_height

    def render(self, game_states, player_states):

        canvas = self.resources["background"].copy()

        for i, card in enumerate(game_states["on_table"]):
            y1 = int(table_cards[i][1] * self.resources["background"].shape[0])
            y2 = int(table_cards[i][1] * self.resources["background"].shape[0]) + self.card_height
            x1 = int(table_cards[i][0] * self.resources["background"].shape[1])
            x2 = int(table_cards[i][0] * self.resources["background"].shape[1]) + self.card_width
            canvas[y1: y2, x1: x2] = self.resources[card]

        for i, card in enumerate(player_states["hand"],):
            y1 = int(hand_cards[i][1] * self.resources["background"].shape[0])
            y2 = int(hand_cards[i][1] * self.resources["background"].shape[0]) + self.card_height
            x1 = int(hand_cards[i][0] * self.resources["background"].shape[1])
            x2 = int(hand_cards[i][0] * self.resources["background"].shape[1]) + self.card_width
            canvas[y1: y2, x1: x2] = self.resources[card]

        cv2.imshow("BelotENGINE", canvas)
        cv2.waitKey(0)


if __name__ == "__main__":
    rnd = Renderer()
    rnd.render({
        "on_table": np.array([0, 0, 0, 0])
    },{
        "hand": list(range(8))
    })