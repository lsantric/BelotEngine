import cv2

class Renderer(object):

    def __init__(self):
        pass

    def render(self, game_states):
        canvas = cv2.imread("gui/assets/background.jpg")
        cv2.imshow("Belot", canvas)
        cv2.waitKey(0)