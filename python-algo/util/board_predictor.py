import numpy as np
from numpy.linalg import norm

from gamelib import GameState, GameUnit, GameMap


class Predictor:
    _ENEMY_BOARD = locations = [(a, b + 14) for b in range(14) for a in range(b, 28 - b)]

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
        self._pending_removals = None

    
    def predict_builds(self) -> GameMap:
        # returns None if no good prediction
        max_sim, map_prediction = 0, None
        max_sim = self._cos_sim([0] * (28 * 14), self._pending_removals)
        for removals, game_map in self._past_boards_dict.items():
            cos_sim = self._cos_sim(removals, self._pending_removals)
            if cos_sim > max_sim:
                map_prediction = game_map

        return self._deserialize_game_map(map_prediction)

    def end_update(self, state: GameState) -> None:
        if self._pending_removals:
            serialized_state = self._serialize_game_map(state.game_map)
            self._past_boards_dict[self._pending_removals] = serialized_state
        
        current_removals = self._removals(state.game_map)
        self._pending_removals = self._serialize_tuple_set(current_removals)

        return
    
    
    def _removals(self, board: GameMap) -> set[tuple[int, int]]:
        def _pending_removal(loc: tuple[int, int]) -> bool:
            x, y = loc
            if board[x,y] and board[x,y][0].stationary:
                return board[x,y].pending_removal
            return False
        
        return set(tup for tup in filter(_pending_removal, self._ENEMY_BOARD))


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