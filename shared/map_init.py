"""
    Classes for interaction between map generator and controller.
"""

# Map request
# Controller -> (MapConfig) -> MapGenerator
# MapGenerator -> (GeneratedMap) -> Controller

import enum
from abc import ABC

from shared.common import Coordinate, Bonus, Item


class MapConfig:
    """
        Map meta information.
    """

    def __init__(self, height, width):
        """
        :param width: map width
        :param height: map height
        """
        self.width = width
        self.height = height


class GeneratedMap:
    """
        Class storing the map layout and players states on the map.
    """

    def __init__(self, game_map, player_init_states, mobs, items):
        """
        :param game_map: 2-dimensional array of CellType elements of height x width size.
        :param player_init_states: player state at the beginning of the game.
        :param mobs: mobs to be placed on the map
        :param items: items to be places of the map
        """
        self.map = game_map
        self.player_init_states = player_init_states
        self.mobs = mobs
        self.items = items


class FightStats:
    def __init__(self, health, strength):
        """
        :param health: unit init max health
        :param strength: unit init strength
        """
        self.health = health
        self.strength = strength


class MapObjectInitState(ABC):
    """
        Abstract class holding the coordinate on the map. Ancestor to any object place on the map.
    """
    def __init__(self, coordinate: Coordinate):
        self.coordinate = coordinate


class UnitInitState(MapObjectInitState, ABC):
    """
        Abstract class holding the fight stats of the unit. Ancestor to any unit on the map.
    """
    def __init__(self, coordinate: Coordinate, fight_stats: FightStats):
        super().__init__(coordinate)
        self.fight_stats = fight_stats


class PlayerInitState(UnitInitState):
    """
        State of the player at the beginning og the game.
    """

    def __init__(self, coordinate: Coordinate, fight_stats: FightStats):
        """
        :param coordinate: player starting coordinate.
        :param fight_stats: player starting health and strength.
        """
        super().__init__(coordinate, fight_stats)


class ModMode(enum.Enum):
    FRIGHTENED = 1
    AGGRESSIVE = 2
    PASSIVE = 3


class MobInitState(UnitInitState):
    """
        State of the mob at the beginning of the game.
    """

    def __init__(self, coordinate, fight_stats, mob_mode):
        """
        :param coordinate: mob starting coordinate.
        :param fight_stats: mob starting health and strength.
        :param mob_mode: mob actions strategy.
        """
        super().__init__(coordinate, fight_stats)
        self.mob_mode = mob_mode


class ItemInitState(MapObjectInitState):
    """
        State of the item at the beginning od the game.
    """
    def __init__(self, coordinate: Coordinate, item: Item):
        """
        :param coordinate: item starting coordinate.
        :param item: item itself.
        """
        super().__init__(coordinate)
        self.item = item
