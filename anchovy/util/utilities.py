from gamelib import GameState, GameUnit, GameMap

class Utilities(object):
    _P2_POINTS = [(a, b + 14) for b in range(14) for a in range(b, 28 - b)]
    _P1_POINTS = [(a, b) for b in range(14) for a in range(13 - b, 15 + b)]

    def __init__(self):
        self.memory = { "repair" : { "to_build" : set() }}

    def repair(self, game_state: GameState, base=0.9, upgraded=0.97, locations=None):
        game_map = game_state.game_map

        to_build = self.memory["repair"]["to_build"]
        for unit in list(to_build):
            game_state.attempt_spawn(unit.unit_type, [unit.x, unit.y])
            if game_state.attempt_upgrade([unit.x, unit.y]):
                to_build.remove(unit)

        potentially_in_progress = set([(unit.x, unit.y) for unit in to_build])
        for x, y in locations or self._P1_POINTS:
            if game_map[x, y] and game_map[x,y][0].stationary: 
                if not game_map[x,y][0].pending_removal:
                    unit = game_map[x,y][0]
                    repair = (unit.health / unit.max_health) < (base if unit.upgraded else upgraded)
                    if repair and (unit.x, unit.y) not in potentially_in_progress:
                        if self.game_state.attempt_remove([x,y]):
                            to_build.add(unit)
        
        self.memory["repair"]["to_build"] = to_build


            
                

                

        