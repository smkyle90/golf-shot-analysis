#!/bin/python3

import numpy as np
import utm


def get_course_transform(course_points):
    b = []
    Ax = []
    Ay = []
    for _hole, data in course_points.items():
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

    return cx[0], cx[1], cy[0], cy[1], utm_coord[-2:]
