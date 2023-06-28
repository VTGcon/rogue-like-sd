import enum
from abc import ABC

"""
    Classes for interaction between UI and Controller
"""


# Player state request
# UI -> (pulls get map method) -> Controller
# Controller -> (PlayerMap) -> UI

class Inventory:
    """
        Class storing items carried or wore by player.
    """

    def __init__(self, items=None):
        """
        :param items: starting hero items.
        """
        if items is None:
            items = {}
        self.active_helmet = None
        self.active_shirt = None
        self.active_weapon = None

        self.items = {item.id: item for item in items}


from shared.common import Coordinate, Item, Bonus


class PlayerToken:
    """
        Token unique for each player.
    """

    def __init__(self, name: str):
        """
        :param name: player username.
        """
        self.name = name

    def __eq__(self, other):
        return self.name == self.name

    def __hash__(self):
        return self.name.__hash__()


class CurrentFightStats:
    """
        Class holding player's current total stats.
    """
    def __init__(self, health, strength):
        """
        :param health: init health.
        :param strength: init strength
        """
        self.__current_bonus = Bonus()
        self.__damage = 0
        self.__base_health = health
        self.__strength = strength

    def get_health(self):
        """
        :return: counts current health based on initial health and damage suffered.
        """
        return max(self.__base_health - self.__damage, 0)

    def get_strength(self):
        """
        :return: current strength including bonuses.
        """
        return self.__strength + self.__current_bonus.strength_bonus

    def update_bonus(self, bonus: Bonus):
        """
        Replaces current bonus with a new one.
        :param bonus: new fight bonus.
        """
        self.__current_bonus = bonus

    def get_damaged(self, damage: int):
        """
        Reduces health according to the damage dealt with stamina bonus taken into account.
        :param damage: damage to be dealt to health.
        """
        self.__damage += max(0, damage - self.__current_bonus.health_bonus)


class Player:
    """
        Class storing player state on the map.
    """

    def __init__(self,
                 coordinate: Coordinate,
                 player_token: PlayerToken,
                 fight_stats: CurrentFightStats):
        """
        :param coordinate: position on the map.
        :param player_token: player identifier.
        :param fight_stats: player fight stats.
        """
        self.coordinate = coordinate
        self.token = player_token
        self.fight_stats = fight_stats


class Mob:
    """
        Class storing mob state on the map.
    """
    def __init__(self, coordinate: Coordinate, mob_mode, fight_stats: CurrentFightStats):
        """
        :param coordinate: mob coordinate
        :param mob_mode: mode in which mob operates
        :param fight_stats: mob fight stats
        """
        self.coordinate = coordinate
        self.mob_mode = mob_mode
        self.fight_stats = fight_stats


class PlayerMap:
    """
        Class storing a full player knowledge about the game.
    """

    def __init__(self, player_map, player: Player, status_message: str):
        """
        :param player_map: 2-dimensional array of characters describing the map layout visible to player.
        :param player: player class defining hero state on the map.
        :param status_message: game information about last actions happened to player.
        """
        self.status_message = status_message
        self.map = player_map
        self.player = player


# Change player state requests
# UI -> (pulls the state change method) -> Controller -> Ok!

class MoveType(enum.Enum):
    """
        Types of the moves that hero may make.
    """
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4
    NO = 0


class ItemActionType(enum.Enum):
    """
        Types of items actions
    """
    DROP = 1
    USE = 2
    WEAR = 3
    REMOVE_FROM_SLOT = 4


class Change(ABC):
    """
        Abstract class for player change.
    """
    pass


class ItemAction(Change):
    """
        Wrapper for the item action.
    """

    def __init__(self, action_type: ItemActionType, item: Item):
        """
        :param action_type: type of action to be done with item.
        :param item: item to do action with.
        """
        self.action_type = action_type
        self.item = item


class PlayerMove(Change):
    """
        Wrapper for the move type. (In case if some complex moves will appear).
    """

    def __init__(self, move_type: MoveType):
        self.move_type = move_type


class StateChange:
    """
        Describes the player's state change.
    """

    def __init__(self, change: Change):
        """
        :param change: change that player made.
        """
        self.change = change


# Create new game

class GameSettings:
    """
        Describes new game settings.
    """

    def __init__(self, map_heigh, map_width):
        self.map_height = map_heigh
        self.map_width = map_width
