import json
import os

ROOT_DIR = os.getenv("ROOT_DATA_DIR", "./third_party/pga-golf-data/data/")


def get_tournament_list():
    with open(ROOT_DIR + "tourney-lookup.json") as f:
        tournaments = json.loads(f.read())
    return list(tournaments.values())


def get_season_list():
    return [2015, 2016, 2017, "all"]
