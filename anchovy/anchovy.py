from .gamelib import GameState, GameMap, GameUnit

from .util.strategy_builder import StrategyBuilder

Coord = list[int, int]

class Anchovy(object):
    def __init__(self):
        self.strategy = StrategyBuilder()

        base = {
            "spawns" : {
                "turrets" : [], # list or function returning list
                "supports" : [],
                "walls" : []
            },
            "builds" : {
                "scouts": [],
                "demolishers" : [],
                "interceptors" : []
            },
            "upgrades" : [],
            "removes" : [],
            "repair" : False,
        }

        attack_left = {
            "spawns" : {
                "turrets" : [], # list or function returning list
                "supports" : [],
                "walls" : []
            },
            "builds" : {
                "scouts": [],
                "demolishers" : [],
                "interceptors" : []
            },
            "upgrades" : [],
            "removes" : [],
            "repair" : False,
        }

        attack_right = {
            "spawns" : {
                "turrets" : [], # list or function returning list
                "supports" : [],
                "walls" : []
            },
            "builds" : {
                "scouts": [],
                "demolishers" : [],
                "interceptors" : []
            },
            "upgrades" : [],
            "removes" : [],
            "repair" : False,
        }

        # can add more functions
        # etc 

        spec = {
            "base" : [base],
            "attack_left": [attack_left],
            "attack_right" : [attack_right]
        }

        self.strategy = StrategyBuilder().compile(spec)

    def turn(game_state):
        # define state machine
        # call function "self.strategy["base"](game_state)
        pass

