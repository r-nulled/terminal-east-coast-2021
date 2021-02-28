from gamelib import game_state
from gamelib import GameState, GameMap, GameUnit

from util.strategy_builder import StrategyBuilder


class Anchovy(object):
    def __init__(self, config):
        init_turrets = [[24,12], [3,12], [11,10], [16,10], [7,10], [20,10]]
        init_walls = [[0,13], [27,13], [1,13], [26,13], [2,13], [25,13], [3,13], [24,13]]
        secondary_turrets = init_turrets + [[4,11], [23,11], [6,10], [21,10]]
        above_turret_walls = init_walls + [[4,12], [23,12], [13,11], [14,11], [12,11], [15,11], [11,11], [16,11],
                                           [10,11], [17,11], [9,11], [18,11], [8,11], [19,11], [7,11], [20,11],
                                           [6,11], [21,11]]
        supports = [[6,9], [7,9], [8,9], [9,9], [10,9], [11,9]]

        base = {
            "builds" : {
                "turrets" : init_turrets, # list or function returning list
                "supports" : [],
                "walls" : init_walls,
            },
            "spawns" : {
                "scouts": [],
                "demolishers" : [],
                "interceptors" : []
            },
            "upgrades" : init_turrets,
            "removes" : [],
            "repair" : False,
        }

        def demo_func(game_state: GameState):
            op_mp, my_mp = game_state.get_resources()
            if my_mp > 9:
                return [([3, 10], 999)]
            else:
                return []


        block_2_1 = {
            "builds" : {
                "turrets" : secondary_turrets, # list or function returning list
                "supports" : supports,
                "walls" : above_turret_walls,
            },
            "spawns" : {
                "scouts": [],
                "demolishers" : demo_func,
                "interceptors" : []
            },
            "upgrades" : secondary_turrets + supports + [[4,12], [23,12]],
            "removes" : [],
            "repair" : True,
        }

        

        # can add more functions
        # etc 

        spec = {
            "base" : base,
            "block_2_1" : block_2_1
        }

        self.strategy = StrategyBuilder(config).compile(spec)

    def turn(self, game_state: GameState):
        # define state machine
        # call function "self.strategy["base"](game_state)
        if game_state.turn_number < 3:
            self.strategy["base"](game_state)
        else:
            self.strategy["block_2_1"](game_state)

