"""Test the Shot Object
"""

import pytest


@pytest.mark.objects
def test_Shot():
    from lib import Shot

    t_round = 1
    hole = 1
    stroke = 2
    x = 15.243
    y = 2342.123
    prox = 32.5
    score = 1

    s = Shot(t_round, hole, stroke, x, y, prox)

    assert s.t_round == t_round
    assert s.hole == hole
    assert s.stroke == stroke
    assert s.x == x
    assert s.y == y
    assert s.prox == prox
    assert not s.score

    s = Shot(t_round, hole, stroke, x, y, prox, score)
    assert s.score == score
