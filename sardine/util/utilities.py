from gamelib import GameState, GameUnit, GameMap

class Utilities:
    _P2_POINTS = [(a, b + 14) for b in range(14) for a in range(b, 28 - b)]
    _P1_POINTS = [(a, b) for b in range(14) for a in range(13 - b, 15 + b)]

    def __init__(self):
        self.memory = { "repair" : { "builds" : [] }}

    def repair(self, game_state: GameState):
        game_map = self.game_state.game_map
        for x, y in self._P1_POINTS:
            if game_map[x, y] and game_map[x,y][0].stationary: 
                if not game_map[x,y][0].pending_removal:
                    unit = game_map[x,y][0]
                    upgrade = unit.upgraded
                    repair = (unit.health / unit.max_health) > (0.9 if upgrade else 0.97)
                    if repair:
                        self.game_state.attempt_remove()
        
        game_map
        



