#!/bin/python3


class Shot:
    def __init__(self, t_round, hole, stroke, x, y, prox, score=0):
        """Defines a shot from ShotLink data.

        Args:
            t_round (int): tournament round the shot is in
            hole (int): hole the shot is on
            stroke (int): stroke number
            x (float): finaal x-coordinate of shot
            y (float): final y-coordinate of shot
            prox (float): proximity remaining to hole
            score (int): final score on hole (for categorization)

        """
        self.t_round = int(t_round)
        self.hole = int(hole)
        self.stroke = int(stroke)
        self.x = float(x)
        self.y = float(y)
        self.prox = float(prox)
        self.score = int(score)
