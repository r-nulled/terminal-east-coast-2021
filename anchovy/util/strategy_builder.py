from gamelib import GameState, GameMap, GameUnit

Coord = list[int, int]

class StrategyBuilder(object):
    def __init__(self, plan):
        planprint = {}

        op_defaults = {
            "builds" : {
                "turrets" : [],
                "supports" : [],
                "walls" : []
            },
            "spawns" : {
                "scouts": [],
                "demolishers" : [],
                "interceptors" : []
            },
            "removes" : [],
            "repair" : True,
        }

        for func_name, ops in plan.items():
            # repair if repair
            # remove removes
            # build builds
            # spawn spawns
            continue

    def lr_pair(location: Coord) -> list[Coord, Coord]:
        x, y = tuple(location)
        if x > 13.5:
            d = x - 13.5
            return [[int(13.5 - d), y], [x, y]]
        else:
            d = 13.5 - x
            return [[x, y], [int(13.5 + d), y]]