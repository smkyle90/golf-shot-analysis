#!/bin/python3

import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.stats as st
import utm
from matplotlib import cm

from .course_data import get_course_transform
from .Shot import Shot

ROOT_DIR = os.getenv("ROOT_DATA_DIR", "./third_party/pga-golf-data/data/")


def inch_to_yard(inches):
    return inches / (3 * 12)


class ShotDistribution:
    def __init__(self):
        self.__score_dist = {}
        self.__blank_data()
        self.__course_par = {}
        self.__transform = ()
        self.lat_lon = ()

    def __blank_data(self):
        self.__score_dist = {
            "t_round": [],
            "hole": [],
            "stroke": [],
            "score": [],
            "x": [],
            "y": [],
            "lat": [],
            "lon": [],
            "prox": [],
        }

    def generate_distribution(self, tournament, year=None):
        self.__blank_data()
        with open(ROOT_DIR + "tourney-lookup.json") as f:
            tournaments = json.loads(f.read())

        if str(tournament) in tournaments:
            tourn_id = str(tournament)
        else:
            tourn_id = [k for k, v in tournaments.items() if v == tournament][0]

        # get coordinate transform
        self.__transform = get_course_transform(tourn_id)

        tourn_dir = ROOT_DIR + "/tournaments/{}/".format(tourn_id)

        if year is None:
            add_year = []
            for file in os.listdir(tourn_dir):
                add_year.append(int(file))
        else:
            add_year = [int(year)]

        for year in add_year:
            base_dir = "{}{}/".format(tourn_dir, year)
            scard_dir = "{}{}/".format(base_dir, "scorecards/")
            course_dir = "{}{}/".format(base_dir, "course/")

            for file in os.listdir(course_dir):
                if "json" not in file:
                    continue

                # print("Getting course information...")
                with open(course_dir + file) as f:
                    course = json.loads(f.read())

            self.__course_par[year] = {
                int(hole["number"]): int(hole["parValue"])
                for hole in course["courses"][0]["holes"]
            }

            for file in os.listdir(scard_dir):
                # print("Adding player shot information...")
                if "json" not in file:
                    continue

                with open(scard_dir + file) as f:
                    shot_data = json.loads(f.read())

                for rnd in shot_data["p"]["rnds"]:
                    for hole in rnd["holes"]:
                        hole_no = int(hole["cNum"])
                        hole_data = []
                        for curr_shot in hole["shots"]:
                            shot_num = int(curr_shot["n"])
                            if float(curr_shot["x"]) and float(curr_shot["y"]):
                                hole_data.append(
                                    Shot(
                                        int(rnd["n"]),
                                        hole_no,
                                        shot_num,
                                        float(curr_shot["x"]),
                                        float(curr_shot["y"]),
                                        inch_to_yard(float(curr_shot["left"])),
                                        0,
                                    )
                                )
                        if not hole_data:
                            continue

                        for all_shots in hole_data:
                            all_shots.score = shot_num
                            self.__add_score(all_shots)

    def __add_score(self, score):
        self.__score_dist["t_round"].append(score.t_round)
        self.__score_dist["hole"].append(score.hole)
        self.__score_dist["stroke"].append(score.stroke)
        self.__score_dist["score"].append(score.score)
        self.__score_dist["x"].append(score.x)
        self.__score_dist["y"].append(score.y)
        self.__score_dist["prox"].append(score.prox)

        utm_x = (score.x - self.__transform[1]) / self.__transform[0]
        utm_y = (score.y - self.__transform[3]) / self.__transform[2]
        lat, lon = utm.to_latlon(utm_x, utm_y, *self.__transform[-1])

        self.__score_dist["lat"].append(lat)
        self.__score_dist["lon"].append(lon)

    def as_df(self, hole=None, t_round=None):

        # Check the values we want to filter by
        # ROUND
        if (t_round is None) or (
            (isinstance(t_round, str)) and (t_round.lower() == "all")
        ):
            all_rounds = set(self.__score_dist["t_round"])
        elif isinstance(t_round, int):
            all_rounds = [t_round]
        else:
            raise TypeError("Round must be None, 'all', or a specific int value.")

        # HOLE
        if (hole is None) or ((isinstance(hole, str)) and (hole.lower() == "all")):
            all_holes = set(self.__score_dist["hole"])
        elif isinstance(hole, int):
            all_holes = [hole]
        else:
            raise TypeError("Hole must be None, 'all', or a specific int value.")

        # Generate the dataframe from the dictionary
        df = pd.DataFrame(self.__score_dist)

        # Filtered DataFrame
        return df[df.hole.isin(all_holes) & (df.t_round.isin(all_rounds))]

    def get_hole_par(self, hole):
        return list(self.__course_par.values())[0].get(hole)

    def get_stroke_list(self, hole, stroke):
        par = self.get_hole_par(hole)
        if isinstance(stroke, int):
            stroke = [stroke]
        elif isinstance(stroke, str):
            if (stroke.lower() == "drive") or (stroke.lower() == "d"):
                stroke = [1]
            elif (stroke.lower() == "approach") or (stroke.lower() == "a"):
                if par < 5:
                    stroke = [par - 2]
                else:
                    stroke = [par - 3, par - 2]
            elif stroke.lower() == "all":
                stroke = [i for i in range(1, 2 * par)]
            else:
                raise ValueError("Must specify 'drive' ('d') or 'approach' ('a').")

        else:
            raise TypeError(
                "Stroke value must be a specific integer value, or 'drive' or 'approach'."
            )

        return stroke

    def get_score_list(self, hole, score):
        par = self.get_hole_par(hole)

        if score is None:
            return [i for i in range(1, 2 * par)]

        if isinstance(score, str):
            if score.lower() == "sub":
                score = [i for i in range(1, par)]
            elif score.lower() == "par":
                score = [par]
            elif score.lower() == "over":
                score = [i for i in range(par + 1, 2 * par)]
            elif score.lower() == "all":
                score = [i for i in range(1, 2 * par)]
            else:
                raise ValueError("Score string must be all/sub/par/over.")
        elif isinstance(score, int):
            score = [score]
        else:
            raise ValueError("Score must be an integer or string of sub/par/over.")

        return score

    def hole_distribution(self, hole, stroke, score, t_round=None, N=100, lat_lon=True):
        """Get the distribution of shots for a hole for a specific score
        on a hole. This shows the areas where certain scores are made,
        but can also be lumped in sub-, even-, or over-par scores.

        Returns a KDE (2d-gaussian) of the geospatial distribution.

        For example, for the 5th hole, tee shot (stroke=1), and we want to see
        the distribution of shots that lead to a certain score. The result is the ideal
        position to leave a shot, that maximizes the chance of making that score.

        """
        par = self.get_hole_par(hole)
        stroke = self.get_stroke_list(hole, stroke)
        score = self.get_score_list(hole, score)

        # Generate dataframe
        score_df = self.as_df(hole, t_round)

        # Filter the dataframe as per our conditions
        df_filt = score_df[
            (score_df.score.isin(score)) & (score_df.stroke.isin(stroke))
        ]

        if len(df_filt) < 3:
            return None, None, None

        if lat_lon:
            x_vec = df_filt.lat
            y_vec = df_filt.lon
        else:
            x_vec = df_filt.x
            y_vec = df_filt.y

        x_min = x_vec.min()
        x_max = x_vec.max()

        y_min = y_vec.min()
        y_max = y_vec.max()

        dx = (x_max - x_min) / N
        dy = (y_max - y_min) / N

        x_range = np.arange(x_min - 10 * dx, x_max + 10 * dx, dx)
        y_range = np.arange(y_min - 10 * dy, y_max + 10 * dy, dy)

        X, Y = np.meshgrid(x_range, y_range)
        pos_grid = np.vstack([X.ravel(), Y.ravel()])
        shot_pos = np.vstack([x_vec, y_vec])
        kernel = st.gaussian_kde(shot_pos)
        f = np.reshape(kernel(pos_grid).T, X.shape)

        return X, Y, f

    def shot_distribution(self, hole, stroke, score, t_round=None, lat_lon=True):
        """Get the mean and covariance of a specific stroke on a hole
        that leads to a specific score.
        """
        score_df = self.as_df(hole, t_round)

        score = self.get_score_list(hole, score)
        stroke = self.get_stroke_list(hole, stroke)

        df_filt = score_df[
            (score_df.score.isin(score)) & (score_df.stroke.isin(stroke))
        ]

        if lat_lon:
            x_vec = df_filt.lat
            y_vec = df_filt.lon
        else:
            x_vec = df_filt.x
            y_vec = df_filt.y

        if not len(df_filt):
            return None
        else:
            pos = np.vstack((x_vec, y_vec)).T
            mu = np.mean(pos, axis=0)

            if len(df_filt) < 2:
                cov = np.eye(2)
            else:
                v = (np.array(pos) - mu) / (len(pos) - 1)
                cov = v.T @ v

        e_val, e_vec = np.linalg.eig(cov)

        return (mu, cov, e_val, e_vec)

    def hole_data(self, hole, stroke, score, t_round=None):

        stroke = self.get_stroke_list(hole, stroke)
        score = self.get_score_list(hole, score)

        score_df = self.as_df(hole=hole, t_round=t_round)
        score_df = score_df[
            (score_df.stroke.isin(stroke)) & (score_df.stroke.isin(score))
        ]

        return score_df

    def plot_hole(self, ax, hole, stroke, score, t_round=None, plotly=True):
        """if hole is None, we plot all. Else we just plot the specific hole
        we care about.
        """
        par = list(self.__course_par.values())[0].get(hole)

        score_df = self.hole_data(hole, stroke, score, t_round=t_round)

        all_scores = score_df.score.unique()
        all_rounds = score_df.t_round.unique()

        # hole_cols = cm.rainbow(np.linspace(0, 1, 18))
        round_cols = cm.rainbow(np.linspace(0, 1, 4))

        for score in all_scores:
            c = self.color_palette(int(score), par)
            for t_round in all_rounds:
                r = round_cols[t_round - 1][:-1]
                df_filt = score_df[
                    (score_df.score == score) & (score_df.t_round == t_round)
                ]
                if plotly:
                    ax.add_trace(
                        go.Scattermapbox(
                            lat=df_filt.lat,
                            lon=df_filt.lon,
                            marker=go.scattermapbox.Marker(
                                size=10, color=c["plotly"].lower()[:-1], opacity=0.7
                            ),
                            showlegend=False,
                        )
                    )
                else:
                    ax.plot(
                        df_filt.x, df_filt.y, "o", color=r, alpha=0.05, markersize=10
                    )
                    ax.plot(df_filt.x, df_filt.y, ".", color=c["col"], alpha=0.3)

        if plotly:
            ax.layout.mapbox.center["lat"] = score_df.lat.mean()
            ax.layout.mapbox.center["lon"] = score_df.lon.mean()

        return ax

    def plot_hole_distribution(
        self, ax, hole, stroke, score, t_round=None, N=100, plotly=True
    ):

        par = list(self.__course_par.values())[0].get(hole)

        color_map = self.color_palette(score, par)

        X, Y, f = self.hole_distribution(hole, stroke, score, t_round, N, plotly)
        if f is not None:
            if plotly:
                ax.add_trace(
                    go.Densitymapbox(
                        lat=X.ravel(),
                        lon=Y.ravel(),
                        z=f.ravel(),
                        colorscale=color_map["plotly"],
                        radius=20,
                        showlegend=False,
                        showscale=False,
                    )
                )
            else:
                ax.contour(X, Y, f, alpha=0.5, cmap=color_map["cmap"])

        return ax

    def plot_shot_distribution(
        self, ax, hole, stroke, score, t_round=None, plotly=True
    ):

        par = list(self.__course_par.values())[0].get(hole)

        color_map = self.color_palette(score, par)

        shot_dist_out = self.shot_distribution(hole, stroke, score, t_round, plotly)

        if shot_dist_out is None:
            return ax

        mu, cov, e_val, e_vec = shot_dist_out

        for (val, vec) in zip(e_val, e_vec):
            for i in [-1, 1]:
                x0 = [mu[0], (mu[0] + 3 * i * np.sqrt(val) * vec[0])]
                y0 = [mu[1], (mu[1] + 3 * i * np.sqrt(val) * vec[1])]
                if plotly:
                    ax.add_trace(
                        go.Scattermapbox(
                            lat=x0,
                            lon=y0,
                            mode="lines",
                            line=dict(color=color_map["plotly"].lower()[:-1], width=2,),
                            showlegend=False,
                        )
                    )
                else:
                    ax.plot(x0, y0, color_map["col"], alpha=0.5)

        return ax

    def color_palette(self, score, par):
        if (isinstance(score, str) and (score.lower() == "sub")) or (
            isinstance(score, int) and (score < par)
        ):
            color_map = {"cmap": cm.Greens, "col": "g", "plotly": "Greens"}
        elif (isinstance(score, str) and (score.lower() == "par")) or (
            isinstance(score, int) and (score == par)
        ):
            color_map = {"cmap": cm.Blues, "col": "b", "plotly": "Blues"}
        elif (isinstance(score, str) and (score.lower() == "over")) or (
            isinstance(score, int) and (score > par)
        ):
            color_map = {"cmap": cm.Reds, "col": "r", "plotly": "Reds"}
        else:
            color_map = {"cmap": cm.Greys, "col": "k", "plotly": "Greys"}

        return color_map
