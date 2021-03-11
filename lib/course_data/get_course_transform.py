import numpy as np
import utm

from .course_coords import course_points


def get_course_transform(course_id):
    b = []
    Ax = []
    Ay = []
    for hole, data in course_points[course_id].items():
        utm_coord = utm.from_latlon(*data["ll"])

        b.append(data["gc"])
        Ax.append([utm_coord[0], 1])
        Ay.append([utm_coord[1], 1])

    bx = np.array(b)[:, 0]
    by = np.array(b)[:, 1]

    Ax = np.array(Ax)
    Ay = np.array(Ay)

    cx = np.linalg.inv(Ax.T @ Ax) @ Ax.T @ bx
    cy = np.linalg.inv(Ay.T @ Ay) @ Ay.T @ by

    # # 16 green
    # test = (33.63747839023742, -111.91320836247203)
    # expected = (10851, 8858)
    # test_utm = utm.from_latlon(*test)
    # actual = (cx[0]*test_utm[0] + cx[1], cy[0]*test_utm[1] + cy[1])
    # print(expected)
    # print(actual)

    return cx[0], cx[1], cy[0], cy[1], utm_coord[-2:]
