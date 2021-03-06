from typing import overload, Any
import numpy as np
from numpy.linalg import norm

from gamelib import GameUnit, GameMap


class Predictor:
    _ENEMY_BOARD = [(a, b + 14) for b in range(14) for a in range(b, 28 - b)]

    def __init__(self, config):
        self.config = config
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        self._UNIT_INDEX = {WALL : 1,SUPPORT : 2,TURRET : 3,}
        self._INDEX_UNIT = {1 : WALL,2 : SUPPORT,3 : TURRET}

        self._past_boards_dict = {}
        self._last_turn_removals = None

        self.turns_processed = -1

    
    def predict_map(self) -> tuple[GameMap, float]:
        # returns None if no good prediction
        max_sim, map_prediction = 0, None
        max_sim = self._cos_sim([0] * (28 * 14), self._last_turn_removals)
        for removals, game_map in self._past_boards_dict.items():
            cos_sim = self._cos_sim(list(removals), self._last_turn_removals)
            if cos_sim > max_sim:
                max_sim = cos_sim
                map_prediction = game_map
        if map_prediction:
            return (self._deserialize_game_map(map_prediction), max_sim)
        return (None, max_sim)

    def update(self, state) -> None:
        if state["turnInfo"][2] < 0:
            return
        if state["turnInfo"][1] == (self.turns_processed):
            return
        else:
            self.turns_processed += 1


        if self._last_turn_removals:
            max_sim = zero_sim = self._cos_sim([0] * (28 * 14), self._last_turn_removals)
            best_key = self._last_turn_removals
            for removals, game_map in self._past_boards_dict.items():
                cos_sim = self._cos_sim(list(removals), self._last_turn_removals)
                if cos_sim > max_sim and cos_sim > zero_sim:
                    max_sim = cos_sim
                    best_key = removals
             

            serialized_state = self._serialize_json_p2Units(state["p2Units"])
            self._past_boards_dict[tuple(best_key)] = serialized_state
        
        current_removals = self._removals(state["p2Units"][6])
        self._last_turn_removals = self._serialize_tuple_set(current_removals)
        return
    
    
    def _removals(self, board: GameMap) -> set[tuple[int, int]]:
        def _pending_removal(loc: tuple[int, int]) -> bool:
            x, y = loc
            if board[x,y] and board[x,y][0].stationary:
                return board[x,y].pending_removal
            return False
        
        return set(tup for tup in filter(_pending_removal, self._ENEMY_BOARD))

    @overload
    def _removals(self, removals: list[list[Any]]) -> set[tuple[int, int]]:
        removal_loc = [(x[0], x[1]) for x in removals]
        return set(removal_loc)

    # deprecated
    def _builds(self, past: GameMap, current: GameMap) -> set[tuple[tuple[int, int], GameUnit]]:
        demos = self._demolishes(past)
        
        def _recently_built(loc: tuple[int, int]) -> bool:
            x, y = loc
            if current[x,y] and current[x,y][0].stationary:
                if past[x,y] and past[x,y][0].stationary:
                    return (x,y) in demos
                elif not past[x,y]:
                    return True
            return False

        just_built = filter(_recently_built, self._ENEMY_BOARD)

        return set((x,y, self._UNIT_INDEX[current[x,y][0].unit_type]) for x, y in just_built)
    
    def _serialize_tuple_set(self, tuple_set: set[tuple[int, int]]) -> np.ndarray:
        if not tuple_set:
            return []
        new_array = [0] * (28 * 14)
        if len(tuple_set[0]) > 2:
            for x, y, z in tuple_set:
                new_array[28 * x + 14 * y] = z + 1
        else:
            for x, y in tuple_set:
                new_array[28 * x + 14 * y] = 1

        return new_array
    
    def _serialize_json_p2Units(self, json):
        upgrades = set([(x, y) for x, y in json[7][:2]])
        array = [0] * (28 * 14)
        for ind, unit_array in enumerate(json[:3]):
            for x, y in unit_array[:2]:
                if (x, y) in upgrades:
                    val = 0 - ind - 1
                else:
                    val = ind + 1
                array[28 * y + x] = val
        return array

    def _serialize_game_map(self, game_map):
        def serialization_map(loc):
            if game_map[loc] and game_map[loc][0].stationary:
                num = self._UNIT_INDEX[game_map[loc][0].unit_type]
                if game_map[loc][0].upgraded:
                    return 0 - num
                else:
                    return num
            else:
                return 0
                
        return [x for x in map(serialization_map, self._ENEMY_BOARD)]

    def _deserialize_game_map(self, serialized_game_map):
        game_map = GameMap(self.config)
        for x in range(28):
            for y in range(14):
                val = serialized_game_map[28 * y + x]
                if val:
                    upgraded = val < 0
                    val = abs(val)
                    unit_type = self._INDEX_UNIT[val]
                    game_map.add_unit(unit_type, (x, y), upgraded)
        return game_map

    def _cos_sim(self, A, B):
        a = np.array(A)
        b = np.array(B)
        return (a @ b.T) / (norm(a) * norm(b))