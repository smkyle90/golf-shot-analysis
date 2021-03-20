import numpy as np
import utm

from lib.course_data import get_course_transform


def test_get_course_transform(course_points):
    tournament = "003"
    ax, ay, bx, by, __ = get_course_transform(course_points.get(tournament))

    # TPC Scottsdale 16 green.
    test = (33.63747839023742, -111.91320836247203)
    test_utm = utm.from_latlon(*test)
    actual = (ax * test_utm[0] + ay, bx * test_utm[1] + by)
    expected = (10851, 8858)
    print("Expected Coordinates:", expected)
    print("Actual Coordinates:", actual)
