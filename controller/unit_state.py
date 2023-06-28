import collections
import enum
import random

from controller.map_object_state import MapObjectState
from shared.common import Coordinate, CellType
from shared.map_init import UnitInitState
from shared.player_map import MoveType


class UnitState(MapObjectState):
    """
        Class storing unit information and providing unit actions such as move or attack.
    """
    class UnitType(enum.Enum):
        UNKNOWN = enum.auto()
        MOB = enum.auto()
        PLAYER = enum.auto()

    class UnitData(MapObjectState.MapObjectData):
        def __init__(self, game_map, unit: UnitInitState):
            super().__init__(unit)
            self.map = game_map
            self.unit_type = UnitState.UnitType.UNKNOWN
            self.fight_stats = unit.fight_stats

    def __init__(self, game_map, unit, game_interactor):
        self.data = UnitState.UnitData(game_map, unit)
        self.game_interactor = game_interactor

    move_deltas = {
        MoveType.DOWN: Coordinate(1, 0),
        MoveType.UP: Coordinate(-1, 0),
        MoveType.RIGHT: Coordinate(0, 1),
        MoveType.LEFT: Coordinate(0, -1),
        MoveType.NO: Coordinate(0, 0),
    }

    def change_state(self, state_change):
        new_coordinate = self.data.coordinate + UnitState.move_deltas[state_change.change.move_type]
        if self.data.map.get_cell(new_coordinate.x, new_coordinate.y) \
                in [CellType.DOOR, CellType.ROOM_SPACE, CellType.PATH]:
            context = self.game_interactor.get_context(self)
            for unit_view in context.player_views + context.mob_views:
                if new_coordinate == unit_view.coordinate:
                    self.game_interactor.attack(self,
                                                UnitState.UnitAttack(unit_view.id,
                                                                     self.data.fight_stats.get_strength()))
                    return
            self.data.coordinate = new_coordinate

    def get_visible_area(self):
        queue = collections.deque([self.data.coordinate])
        mask = [[0 for _ in range(self.data.map.width)] for _ in range(self.data.map.height)]
        mask[self.data.coordinate.x][self.data.coordinate.y] = 1

        deltas = [Coordinate(0, 1),
                  Coordinate(0, -1),
                  Coordinate(1, 0),
                  Coordinate(-1, 0)]

        while queue:
            coordinate = queue.pop()
            for delta in deltas:
                new_coordinate = coordinate + delta
                new_cell = self.data.map.get_cell(new_coordinate.x, new_coordinate.y)

                if new_cell in [CellType.ERROR, CellType.EMPTY_SPACE]:
                    continue
                if new_cell is CellType.ROOM_SPACE and mask[new_coordinate.x][new_coordinate.y] == 0:
                    queue.appendleft(new_coordinate)
                mask[new_coordinate.x][new_coordinate.y] = 1
        return mask

    class UnitAttack:
        def __init__(self, target, damage):
            self.target = target
            self.damage = damage
            self.confusion = random.randint(0, 1)

    def attack(self, unit_attack):
        self.game_interactor(self, unit_attack, self.data.fight_stats.strength)

    def get_damaged(self, unit_attack):
        self.data.fight_stats.get_damaged(unit_attack.damage)