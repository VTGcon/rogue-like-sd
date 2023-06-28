import enum
import uuid
from abc import ABC


class Coordinate:
    """
        Class storing a position on the map.
    """

    def __init__(self, x: int, y: int):
        """
        :param x: height coordinate.
        :param y: width coordinate.
        """
        self.x = x
        self.y = y

    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Bonus:
    """
        Class representing hero stats bonuses: health bonus and strength bonus.
    """

    def __init__(self, health_bonus=0, strength_bonus=0):
        self.health_bonus = health_bonus
        self.strength_bonus = strength_bonus

    def __add__(self, other):
        return Bonus(self.health_bonus + other.health_bonus, self.strength_bonus + other.strength_bonus)

    def __eq__(self, other):
        return self.health_bonus == other.health_bonus and self.strength_bonus == other.strength_bonus


class ItemType(enum.Enum):
    UNKNOWN = 0,
    WEAPON = 1,
    POTION = 2,
    CLOTH = 3,


class Item(ABC):
    """
        Class re presenting an item held by a hero to provide him with bonus.
    """

    def __init__(self, bonus: Bonus, name: str):
        self.id = uuid.uuid4()
        self.bonus = bonus
        self.name = name
        self.item_type = ItemType.UNKNOWN


"""
    General game elements shared between all components.
"""


class Map:
    """
        Class storing map layout. Includes only elements listed in the CellType enum below.
    """

    def __init__(self, height: int, width: int, map_array):
        """
        :param height: height of the map.
        :param width: width of the map.
        :param map_array: list of height lists each containing exactly width CellType items.
        """

        self.width = width
        self.height = height
        self.map_array = map_array

    def get_cell(self, height: int, width: int):
        """
        Cell content getter.

        :param height: height coordinate of the required cell.
        :param width: width coordinate of the required cell.
        :return: content of the cell if it existed. Otherwise returns CellType.ERROR value.
        """
        return self.map_array[height][
            width] if 0 <= height < self.height and 0 <= width < self.width else CellType.ERROR


class CellType(enum.Enum):
    """
        Class describing possible map cell content.
    """
    EMPTY_SPACE = ' '
    ROOM_SPACE = '.'
    MOB = '%'
    VERTICAL_WALL = '|'
    HORIZONTAL_WALL = '-'
    DOOR = '*'
    PATH = '#'
    HERO = '@'
    ITEM = '!'
    ERROR = 'ERROR'


from shared.player_map import Inventory

"""
    Classes describing possible Item types and their properties.
"""


class Usable(Item, ABC):
    """
        Item that can be used once after which it will disappear.
    """


class Wearable(Item, ABC):
    """
        Item that can be put into player slot (weapon or cloth)
    """

    def wear(self, inventory):
        """
        Puts item on hero if required slot is empty.
        :param inventory: inventory to depict an item on.
        :return: true if put on successfully, false if required slot was not empty.
        """
        raise NotImplementedError()

    def take_off(self, inventory):
        """
        Takes an item off the hero if it matches with the current item. Puts item back to given inventory.
        :param inventory: place to put item back to.
        :return: true if taken off successfully, false otherwise.
        """
        raise NotImplementedError()


class Armor(Wearable, ABC):
    """
        Wearable item that can be put into the shirt slot
    """
    def __init__(self, bonus: Bonus, name: str):
        super().__init__(bonus, name)

    def wear(self, inventory: Inventory):
        if inventory.active_shirt is not None or self.id not in inventory.items:
            return False
        del inventory.items[self.id]
        inventory.active_shirt = self
        return True

    def take_off(self, inventory: Inventory):
        if inventory.active_shirt is self:
            inventory.items[self.id] = self
            inventory.active_shirt = None
            return True
        return False

