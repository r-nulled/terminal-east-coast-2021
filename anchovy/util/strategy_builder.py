from gamelib import GameState, GameMap, GameUnit

from .utilities import Utilities

class StrategyBuilder:
    OP_DEFAULTS = {
            "builds" : {
                "turrets" : [], # list or function returning list
                "supports" : [],
                "walls" : []
            },
            "spawns" : {
                "scouts": [],
                "demolishers" : [],
                "interceptors" : []
            },
            "upgrades" : [],
            "removes" : [],
            "repair" : False,
        }

    def __init__(self, config):
        self.functions = {}
        self.game_state = None
        self.util = Utilities()

        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]



    
    def compile(self, plan):
        for func_name, spec in plan.items():
            self._create_function(func_name, spec)
        
        return self.functions

    def _run(self, game_state, spec):
        self.game_state = game_state
        self._repair(spec["repair"])
        self._remove(spec["removes"])
        self._upgrade(spec["upgrades"])
        self._build(spec["builds"])
        self._spawn(spec["spawns"])

    def _create_function(self, func_name, spec):
        spec = dict(self.OP_DEFAULTS, **spec)
        # todo
        self.functions[func_name] = (lambda game_state : self._run(game_state, spec))
        return
    
    def _build(self, build_dict):
        ref = {
            "turrets" : TURRET,
            "supports" : SUPPORT,
            "walls" : WALL,
        }

        for key, val in build_dict.items():
            unit = ref[key]

            if isinstance(val, list):
                loc = val
            else:
                loc = val(self.game_state)
            
            if not loc:
                continue

            for loc in loc:
                    self.game_state.attempt_spawn(unit, loc)
        return
        
    def _spawn(self, spawn_dict):
        ref = {
            "scouts": SCOUT,
            "demolishers" : DEMOLISHER,
            "interceptors" : INTERCEPTOR
        }

        for key, val in spawn_dict.items():
            unit = ref[key]
            # val can either be list or func taking game_map and returning list 
            if isinstance(val, list):
                loc = val
            else:
                loc = val(self.game_state)
            if not loc:
                continue
            for loc, num in loc:
                    self.game_state.attempt_spawn(unit, loc, num)
        
        return
    
    def _upgrade(self, locations):
        if not locations:
            return
        if isinstance(locations, list):
            self.game_state.attempt_upgrade(locations)
        else:
            self.game_state.attempt_upgrade(locations(self.game_state.game_map))

    def _remove(self, locations):
        if not locations:
            return
        if isinstance(locations, list):
            self.game_state.attempt_remove(locations)
            self.util.remove_from_repair(locations)
        else:
            locs = locations(self.game_state)
            self.game_state.attempt_remove(locs)
            self.util.remove_from_repair(locs)

    def _repair(self, repair_bool):
        if repair_bool:
            self.util.repair(self.game_state)

    def lr_pair(cls, location):
        x, y = tuple(location)
        if x > 13.5:
            d = x - 13.5
            return [[int(13.5 - d), y], [x, y]]
        else:
            d = 13.5 - x
            return [[x, y], [int(13.5 + d), y]]