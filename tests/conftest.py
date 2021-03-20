import pytest


@pytest.fixture
def course_points():
    course_points = {
        "003": {
            "hole1_green": {
                "ll": (33.64360260396358, -111.91176851490071),
                "gc": (11297, 11080),
            },
            "hole13_green": {
                "ll": (33.64231012720274, -111.92285216519433),
                "gc": (7918, 10621),
            },
            "hole17_green": {
                "ll": (33.63697793639003, -111.90983361687059),
                "gc": (11882, 8670),
            },
        },
    }
    return course_points
