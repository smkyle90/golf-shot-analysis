"""Test the ShotDistribution Object
"""

import pytest


@pytest.mark.objects
def test_ShotDistribution(course_points):
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go

    from lib import ShotDistribution

    s = ShotDistribution()

    tournament = "003"  # WM Phoenix
    year = 2015
    # With no course data, i.e., to perform calibration
    s.generate_distribution("Waste Management Phoenix Open")

    # Check it generates a dataframe
    print(s.as_df().head())

    # Use tournament name
    s.generate_distribution("Waste Management Phoenix Open", course_points)
    # Use tournement ID
    s.generate_distribution(tournament, course_points, year)

    # Check it generates a dataframe
    print(s.as_df().head())

    # Specify the hole we want the dataframe for
    print(s.as_df(hole=5).head())

    # Specify the hole and round we want the dataframe for
    print(s.as_df(hole=5, t_round=1).head())

    fig = plt.figure()
    for use_plotly, ax in enumerate([fig.add_subplot(111), go.Figure()]):
        hole = 1
        ax = s.plot_flag_loc(ax, hole, plotly=use_plotly)

        ax = s.plot_hole(ax, hole, "all", "all", flag_loc=1, plotly=use_plotly)
        ax = s.plot_hole(ax, hole, "all", "all", flag_loc=2, plotly=use_plotly)
        ax = s.plot_hole(ax, hole, "all", "all", flag_loc=3, plotly=use_plotly)

        ax = s.plot_hole(ax, hole, 2, 5, plotly=use_plotly)

        t_round = 1
        ax = s.plot_hole(ax, hole, 1, None, t_round, flag_loc=None, plotly=use_plotly)

        # check the first shot for all scores
        stroke = 1
        par = 4
        # check first shot for birides
        ax = s.plot_hole_distribution(
            ax, hole, stroke, par - 1, t_round, flag_loc=None, plotly=use_plotly
        )
        # for pars
        ax = s.plot_hole_distribution(
            ax, hole, stroke, par, t_round, flag_loc=None, plotly=use_plotly
        )
        # for bogeys
        ax = s.plot_hole_distribution(
            ax, hole, stroke, par + 1, t_round, flag_loc=None, plotly=use_plotly
        )

        ax = s.plot_hole_distribution(
            ax, hole, stroke, "sub", t_round, flag_loc=None, plotly=use_plotly
        )
        ax = s.plot_hole_distribution(
            ax, hole, stroke, "over", t_round, flag_loc=None, plotly=use_plotly
        )

        # all 3rd shots that lead to a par on the second hole
        par = 4
        ax = s.plot_hole_distribution(
            ax, 2, 3, par, t_round, flag_loc=None, plotly=use_plotly
        )

        # Plot the mean and variance of the tee shot on the third hole for birdie, par and bogey
        par = 5
        ax = s.plot_shot_distribution(
            ax, 3, stroke, par - 1, t_round, flag_loc=None, plotly=use_plotly
        )
        ax = s.plot_shot_proximity(
            ax, 3, stroke, par - 1, t_round, flag_loc=None, plotly=use_plotly
        )
        ax = s.plot_shot_distribution(
            ax, 3, stroke, par, t_round, flag_loc=None, plotly=use_plotly
        )
        ax = s.plot_shot_distribution(
            ax, 3, stroke, par + 1, t_round, flag_loc=None, plotly=use_plotly
        )

        # all approach shots on the fourth hole
        par = 3
        ax = s.plot_hole_distribution(
            ax, 4, "approach", "sub", t_round, flag_loc=None, plotly=use_plotly
        )
        ax = s.plot_hole_distribution(
            ax, 4, "approach", "over", t_round, flag_loc=None, plotly=use_plotly
        )

        # all drives shots on the fifth hole
        par = 4
        ax = s.plot_hole_distribution(
            ax, 5, "drive", "sub", t_round, "all", plotly=use_plotly
        )
        ax = s.plot_hole_distribution(
            ax, 5, "drive", "over", t_round, flag_loc=None, plotly=use_plotly
        )

        par = 5
        ax = s.plot_hole_distribution(
            ax, 15, "approach", "par", t_round, 1, plotly=use_plotly
        )

        ax = s.plot_hole_distribution(ax, 16, 1, 0, t_round, "all", plotly=use_plotly)
        ax = s.plot_hole_distribution(
            ax, 17, 0, 1, t_round, flag_loc=None, plotly=use_plotly
        )

        ax = s.plot_shot_distribution(ax, 18, 0, 4, t_round, "all", plotly=use_plotly)
        ax = s.plot_shot_distribution(
            ax, 18, 2, 1, t_round, flag_loc=None, plotly=use_plotly
        )
        hole = 6
        flag_loc = "all"
        s.set_base_df(hole, flag_loc)
        ax = s.plot_shot_distribution(
            ax, hole, 2, 1, t_round, flag_loc=flag_loc, plotly=use_plotly
        )
