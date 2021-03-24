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
from sklearn.cluster import KMeans

from .course_data import get_course_transform
from .Shot import Shot

ROOT_DIR = os.getenv("ROOT_DATA_DIR", "./third_party/pga-golf-data/data/")


def inch_to_yard(inches):
    return inches / (3 * 12)


def yard_to_ft(yard):
    return yard * 3


class ShotDistribution:
    def __init__(self):
        self.__score_dist = {}
        self.__course_par = {}
        self.__transform = ()
        self.__pin_locs = {}
        self.name = ""
        self.tid = ""
        self.base_df = {}

        # Ensure everything is initialised appropriately
        self.__blank_data()

    def __blank_data(self):
        self.__score_dist = {
            "year": [],
            "player": [],
            "t_round": [],
            "hole": [],
            "stroke": [],
            "score": [],
            "x": [],
            "y": [],
            "lat": [],
            "lon": [],
            "prox": [],
            "flag_loc": [],
        }
        self.__course_par = {}
        self.__transform = ()
        self.__pin_locs = {}
        self.name = ""
        self.tid = ""
        self.base_df = {}

    def __get_tournament_id(self, id_or_name):
        with open(ROOT_DIR + "tourney-lookup.json") as f:
            tournaments = json.loads(f.read())

        if str(id_or_name) in tournaments:
            tourn_id = str(id_or_name)
        else:
            tourn_id = [k for k, v in tournaments.items() if v == id_or_name][0]

        self.name = tournaments.get(tourn_id, tourn_id)
        self.tid = tourn_id

        return tourn_id

    def get_hole_img_path(self, hole):
        if hole < 10:
            hole = "0{}".format(hole)

        hole_file_name = "{}_full.jpg".format(hole)
        tourn_id = self.tid
        tourn_dir = ROOT_DIR + "tournaments/{}/".format(tourn_id)

        for year in [2015, 2016, 2017]:
            year_dir = tourn_dir + "{}/".format(year)
            course_dir = year_dir + "course/" + tourn_id + "/holes/"
            hole_dir = course_dir + hole_file_name
            if os.path.exists(hole_dir):
                return hole_dir
        return None

    def generate_distribution(self, tournament, course_points=None, year=None):
        self.__blank_data()

        tourn_id = self.__get_tournament_id(tournament)

        # get coordinate transform
        if course_points is not None:
            if course_points.get(tourn_id):
                self.__transform = get_course_transform(course_points.get(tourn_id))
            else:
                raise ValueError("Tournament ID not in Course Points configuration.")

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

                pid = shot_data["p"]["id"]

                for rnd in shot_data["p"]["rnds"]:
                    for hole in rnd["holes"]:
                        hole_no = int(hole["cNum"])
                        hole_data = []
                        for curr_shot in hole["shots"]:
                            shot_num = int(curr_shot["n"])
                            if float(curr_shot["x"]) and float(curr_shot["y"]):
                                hole_data.append(
                                    Shot(
                                        pid,
                                        year,
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

        self.__infer_pin_locations()

    def __infer_pin_locations(self):
        shot_df = self.as_df()

        years = shot_df.year.unique()

        # Number of clusters is number of rounds, i.e., assume there are only this many pin positions
        rounds = shot_df.t_round.unique()
        rounds = [rnd for rnd in rounds if rnd <= 4]

        # Number of holes
        holes = shot_df.hole.unique()

        temp_pin_locs = {
            "year": [],
            "t_round": [],
            "hole": [],
            "x_bar": [],
            "y_bar": [],
        }
        # Assume hole is located at the average of someones second last shot, i.e., score-1.
        # The only thing we know is that a pin is in the same location in the same year and round.
        # So we take the average of this location, for as many rounds as we have then cluster these locations.
        # This is so we don't mis-classify a year-round combination.
        for hole in holes:
            for year in years:
                for rnd in rounds:
                    # Filter by these combinations
                    df_filt = shot_df[
                        (shot_df.hole == hole)
                        & (shot_df.t_round == rnd)
                        & (shot_df.year == year)
                    ]

                    # Get final shot for each hole. Take only values within 20 yards
                    df_flag_loc = df_filt[
                        (df_filt.stroke == (df_filt.score - 1)) & (df_filt.prox < 20)
                    ]

                    if not len(df_flag_loc):
                        continue

                    # Add to pin location history
                    temp_pin_locs["year"].append(year)
                    temp_pin_locs["t_round"].append(rnd)
                    temp_pin_locs["hole"].append(hole)
                    temp_pin_locs["x_bar"].append(df_flag_loc.x.mean())
                    temp_pin_locs["y_bar"].append(df_flag_loc.y.mean())

        # Perform clustering
        loc_df = pd.DataFrame(temp_pin_locs)

        # By hole
        for hole in holes:
            df_filt = loc_df[loc_df.hole == hole]
            # Turn into array
            all_flag_loc = np.vstack((df_filt.x_bar, df_filt.y_bar)).T

            # Perform the clustering
            k_means = KMeans(n_clusters=len(rounds))
            k_means.fit(all_flag_loc)
            loc_label = k_means.predict(all_flag_loc) + 1  # Always greater than zero

            loc_df.loc[(loc_df.hole == hole), "loc_bar"] = loc_label.astype(int)

        # Merge with all shot data based on year, round and hole.

        # Reset flag locs
        shot_df.flag_loc = -1

        # Left merge the data frames
        new_df = pd.merge(
            shot_df,
            loc_df,
            how="left",
            left_on=["year", "t_round", "hole"],
            right_on=["year", "t_round", "hole"],
        )

        # Update loc value
        shot_df["flag_loc"] = new_df["loc_bar"]

        # Reinstantiate pin locations dictionary
        loc_df = loc_df.drop(columns=["year", "t_round"])
        loc_df = loc_df.drop_duplicates(subset=["hole", "loc_bar"])

        if self.__transform:
            lat_vec, lon_vec = [], []
            for x_bar, y_bar in zip(loc_df.x_bar, loc_df.y_bar):
                utm_x = (x_bar - self.__transform[1]) / self.__transform[0]
                utm_y = (y_bar - self.__transform[3]) / self.__transform[2]
                lat, lon = utm.to_latlon(utm_x, utm_y, *self.__transform[-1])
                lat_vec.append(lat)
                lon_vec.append(lon)
            loc_df["lat"] = lat_vec
            loc_df["lon"] = lon_vec
        else:
            loc_df["lat"] = loc_df.x_bar
            loc_df["lon"] = loc_df.y_bar

        # Update dicts
        self.__pin_locs = loc_df.to_dict()
        self.__score_dist = shot_df.to_dict()

    def __add_score(self, score):
        self.__score_dist["player"].append(score.player)
        self.__score_dist["year"].append(score.year)
        self.__score_dist["t_round"].append(score.t_round)
        self.__score_dist["hole"].append(score.hole)
        self.__score_dist["stroke"].append(score.stroke)
        self.__score_dist["score"].append(score.score)
        self.__score_dist["x"].append(score.x)
        self.__score_dist["y"].append(score.y)
        self.__score_dist["prox"].append(score.prox)
        self.__score_dist["flag_loc"].append(-1)

        if self.__transform:
            utm_x = (score.x - self.__transform[1]) / self.__transform[0]
            utm_y = (score.y - self.__transform[3]) / self.__transform[2]
            lat, lon = utm.to_latlon(utm_x, utm_y, *self.__transform[-1])

            self.__score_dist["lat"].append(lat)
            self.__score_dist["lon"].append(lon)
        else:
            self.__score_dist["lat"].append(score.x)
            self.__score_dist["lon"].append(score.y)

    def as_df(self, hole=None, t_round=None, stroke=None, score=None, flag_loc=None):

        # Check the values we want to filter by
        all_holes = self.__get_hole_list(hole)
        all_rounds = self.__get_round_list(t_round)
        flag_loc = self.__get_flag_loc_list(flag_loc)

        # Generate the dataframe from the dictionary
        df = pd.DataFrame(self.__score_dist)

        # First stage filter for holes, round and flag location.
        df = df[
            df.hole.isin(all_holes)
            & (df.t_round.isin(all_rounds))
            & (df.flag_loc.isin(flag_loc))
        ]

        # The base DF is for the hole, round and flag loc. We will
        # use this to filter by stroke and score
        self.base_df = df

        # If we have just one hole, filter by stroke and score
        if len(all_holes) == 1:
            stroke = self.__get_stroke_list(all_holes[0], stroke)
            score = self.__get_score_list(all_holes[0], score)

            df = df[df.stroke.isin(stroke) & (df.score.isin(score))]

        return df

    def set_base_df(self, hole=None, flag_loc=None):
        self.base_df = self.as_df(hole, None, None, None, flag_loc)

    def __get_hole_par(self, hole):
        return list(self.__course_par.values())[0].get(hole)

    def __get_round_list(self, t_round):
        # ROUND
        if (t_round is None) or (
            (isinstance(t_round, str)) and (t_round.lower() == "all")
        ):
            all_rounds = set(self.__score_dist["t_round"])
        elif isinstance(t_round, int):
            all_rounds = [t_round]
        else:
            raise TypeError("Round must be None, 'all', or a specific int value.")

        return list(all_rounds)

    def __get_hole_list(self, hole):
        # HOLE
        if (hole is None) or ((isinstance(hole, str)) and (hole.lower() == "all")):
            all_holes = set(self.__score_dist["hole"])
        elif isinstance(hole, int):
            all_holes = [hole]
        else:
            raise TypeError("Hole must be None, 'all', or a specific int value.")

        return list(all_holes)

    def __get_stroke_list(self, hole, stroke):
        par = self.__get_hole_par(hole)
        if stroke is None:
            stroke = "all"

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

    def __get_flag_loc_list(self, flag_loc):
        if isinstance(flag_loc, int):
            flag_loc = [flag_loc]
        elif isinstance(flag_loc, str):
            if (flag_loc.lower() == "all") or (flag_loc.lower() == "a"):
                flag_loc = [-1, 1, 2, 3, 4]
            else:
                raise ValueError("Must specify 'all' ('a').")
        elif flag_loc is None:
            flag_loc = [-1, 1, 2, 3, 4]
        else:
            raise TypeError(
                "Flag location value must be a specific integer value, or 'all' or None."
            )

        return flag_loc

    def __get_score_list(self, hole, score):
        par = self.__get_hole_par(hole)

        if score is None:
            score = "all"

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

    def hole_distribution(
        self, hole, stroke, score, t_round=None, flag_loc=None, N=100, lat_lon=True
    ):
        """Get the distribution of shots for a hole for a specific score
        on a hole. This shows the areas where certain scores are made,
        but can also be lumped in sub-, even-, or over-par scores.

        Returns a KDE (2d-gaussian) of the geospatial distribution.

        For example, for the 5th hole, tee shot (stroke=1), and we want to see
        the distribution of shots that lead to a certain score. The result is the ideal
        position to leave a shot, that maximizes the chance of making that score.

        """
        if len(self.base_df):
            shot_df = self.base_df
            stroke = self.__get_stroke_list(hole, stroke)
            score = self.__get_score_list(hole, score)
            shot_df = shot_df[
                (shot_df.stroke.isin(stroke)) & (shot_df.score.isin(score))
            ]
        else:
            shot_df = self.as_df(hole, t_round, stroke, score, flag_loc)

        if len(shot_df) < 3:
            return None, None, None

        if lat_lon:
            x_vec = shot_df.lat
            y_vec = shot_df.lon
        else:
            x_vec = shot_df.x
            y_vec = shot_df.y

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

    def shot_distribution(
        self, hole, stroke, score, t_round=None, flag_loc=None, lat_lon=True
    ):
        """Get the mean and covariance of a specific stroke on a hole
        that leads to a specific score.
        """

        if len(self.base_df):
            shot_df = self.base_df
            stroke = self.__get_stroke_list(hole, stroke)
            score = self.__get_score_list(hole, score)
            shot_df = shot_df[
                (shot_df.stroke.isin(stroke)) & (shot_df.score.isin(score))
            ]
        else:
            shot_df = self.as_df(hole, t_round, stroke, score, flag_loc)

        if lat_lon:
            x_vec = shot_df.lat
            y_vec = shot_df.lon
        else:
            x_vec = shot_df.x
            y_vec = shot_df.y

        if not len(shot_df):
            return None
        else:
            pos = np.vstack((x_vec, y_vec)).T
            mu = np.mean(pos, axis=0)

            if len(shot_df) < 2:
                cov = np.eye(2)
            else:
                v = (np.array(pos) - mu) / (len(pos) - 1)
                cov = v.T @ v

        e_val, e_vec = np.linalg.eig(cov)

        return (mu, cov, e_val, e_vec)

    def hole_data(self, hole, stroke, score, t_round=None, flag_loc=None):

        if len(self.base_df):
            shot_df = self.base_df
            stroke = self.__get_stroke_list(hole, stroke)
            score = self.__get_score_list(hole, score)
            shot_df = shot_df[
                (shot_df.stroke.isin(stroke)) & (shot_df.score.isin(score))
            ]
        else:
            shot_df = self.as_df(hole, t_round, stroke, score, flag_loc)

        return shot_df

    def plot_flag_loc(self, ax, hole, plotly=True):

        flag_df = pd.DataFrame(self.__pin_locs)
        hole_df = flag_df[flag_df.hole == hole]

        if plotly:
            ax.add_trace(
                go.Scattermapbox(
                    lat=hole_df.lat,
                    lon=hole_df.lon,
                    marker=go.scattermapbox.Marker(size=10, color="black",),
                    showlegend=False,
                )
            )
        else:
            ax.scatter(
                hole_df.x_bar, hole_df.y_bar, c="k",
            )

            for x, y, loc in zip(hole_df.x_bar, hole_df.y_bar, hole_df.loc_bar):
                ax.text(x + 2, y + 2, "{}".format(int(loc)), c="k")

        return ax

    def plot_hole(
        self, ax, hole, stroke, score, t_round=None, flag_loc=None, plotly=True,
    ):
        """if hole is None, we plot all. Else we just plot the specific hole
        we care about.
        """
        par = list(self.__course_par.values())[0].get(hole)

        shot_df = self.hole_data(
            hole, stroke, score, t_round=t_round, flag_loc=flag_loc
        )

        all_scores = shot_df.score.unique()

        for score in all_scores:
            c = self.color_palette(int(score), par)
            df_filt = shot_df[
                (shot_df.score == score)  # & (shot_df.t_round == t_round)
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
                        hoverinfo="skip",
                    )
                )
            else:
                # ax.plot(
                #     df_filt.x, df_filt.y, "o", color=r, alpha=0.05, markersize=10
                # )
                ax.plot(df_filt.x, df_filt.y, ".", color=c["col"], alpha=0.3)

        if plotly:
            ax.layout.mapbox.center["lat"] = shot_df.lat.mean()
            ax.layout.mapbox.center["lon"] = shot_df.lon.mean()

        return ax

    def plot_hole_distribution(
        self, ax, hole, stroke, score, t_round=None, flag_loc=None, N=100, plotly=True,
    ):

        par = list(self.__course_par.values())[0].get(hole)

        color_map = self.color_palette(score, par)

        X, Y, f = self.hole_distribution(
            hole, stroke, score, t_round, flag_loc, N, plotly
        )
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
                        hoverinfo="skip",
                    )
                )
            else:
                ax.contour(X, Y, f, alpha=0.5, cmap=color_map["cmap"])

        return ax

    def plot_shot_distribution(
        self, ax, hole, stroke, score, t_round=None, flag_loc=None, plotly=True,
    ):

        par = list(self.__course_par.values())[0].get(hole)

        color_map = self.color_palette(score, par)

        shot_dist_out = self.shot_distribution(
            hole, stroke, score, t_round, flag_loc, plotly
        )

        if shot_dist_out is None:
            return ax

        mu, _cov, e_val, e_vec = shot_dist_out

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
                            hoverinfo="skip",
                        )
                    )
                else:
                    ax.plot(x0, y0, color_map["col"], alpha=0.5)

        return ax

    def plot_shot_proximity(
        self, ax, hole, stroke, score, t_round=None, flag_loc=None, plotly=True,
    ):

        par = list(self.__course_par.values())[0].get(hole)

        flag_df = pd.DataFrame(self.__pin_locs)
        flags = self.__get_flag_loc_list(flag_loc)
        hole_df = flag_df[(flag_df.hole == hole) & flag_df.loc_bar.isin(flags)]

        # Hole loc
        x0 = hole_df.x_bar.mean()
        y0 = hole_df.y_bar.mean()

        # Hard code to get all scoring data for hole
        shot_df = self.hole_data(
            hole, stroke, score=None, t_round=t_round, flag_loc=flag_loc
        )
        if not plotly:
            x_lim = ax.get_xlim()
            y_lim = ax.get_ylim()

        for score in ["sub", "par", "over"]:
            col = self.color_palette(score, par)
            score_vals = self.__get_score_list(hole, score)

            df_filt = shot_df[shot_df.score.isin(score_vals)]

            # 95% confidence circle of score within that distance
            num_sigmas = 2
            rad = yard_to_ft(df_filt.prox.mean() + num_sigmas * df_filt.prox.std())

            if plotly:
                return ax
                # TODO: add this
            else:
                circle = plt.Circle(
                    (x0, y0), rad, color=col["col"], fill=False, alpha=0.5
                )
                ax.add_patch(circle)

        if not plotly:
            ax.set_xlim(x_lim)
            ax.set_ylim(y_lim)

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

    def calibrate_green_loc(self, holes):
        green_locs = {}
        pin_df = pd.DataFrame(self.__pin_locs)

        for hole in holes:
            green_locs[hole] = (
                pin_df[pin_df.hole == hole].x_bar.mean(),
                pin_df[pin_df.hole == hole].y_bar.mean(),
            )

        return green_locs
