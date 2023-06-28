import random

from shared.common import CellType, Map, Coordinate, Bonus, Armor
from shared.map_init import GeneratedMap, PlayerInitState, FightStats, MobInitState, ModMode, ItemInitState


MIN_WIDTH = 4
MIN_HEIGHT = 4
MAX_WIDTH = 8
MAX_HEIGHT = 8

MAX_HEALTH = 100
MAX_STRENGTH = 20


class Room:
    """
        Creates a room inside the map.
    """
    def __init__(self, cornerx, cornery, width, height):
        self.cornerx = cornerx
        self.cornery = cornery
        self.width = width
        self.height = height
        self.neighbours = []

    """
        Returns right border of the room.
    """
    def get_right_border(self):
        return self.cornerx + self.width

    """
        Returns bottom border position of the room.
    """
    def get_bottom_border(self):
        return self.cornery + self.height


"""
    generate_map generates a map by configuration, containing width and height of the field
"""
def generate_map(config):
    field = [[CellType.EMPTY_SPACE] * config.width for i in range(config.height)]
    graph = _generate_rooms_graph(config.width - 1, config.height - 1)
    field = _draw_rooms_graph(graph, field)
    field = _draw_paths(graph, field)
    person = PlayerInitState(Coordinate(graph.cornery + graph.height // 2, graph.cornerx + graph.width // 2),
                             FightStats(MAX_HEALTH, random.randint(0, MAX_STRENGTH)))
    used = set()
    used.add((graph.cornery + graph.height // 2, graph.cornerx + graph.width // 2))
    used, mobs = _generate_mobs(field, used)
    used, clothes = _generate_clothes(field, used)
    result = Map(config.height, config.width, field)
    return GeneratedMap(result, person, mobs, clothes)


def _generate_mobs(field, used):
    mobs = [0] * random.randint(3, 6)
    for i in range(len(mobs)):
        while True:
            x = random.randint(0, len(field[0]) - 1)
            y = random.randint(0, len(field) - 1)
            if field[y][x] != CellType.ROOM_SPACE or (y, x) in used:
                continue
            used.add((y, x))
            mobs[i] = MobInitState(Coordinate(y, x), FightStats(MAX_HEALTH, random.randint(0, MAX_STRENGTH)),
                                   random.choice(list(ModMode)))
            break
    return used, mobs


def _generate_clothes(field, used):
    clothes = [0] * random.randint(3, 6)
    for i in range(len(clothes)):
        while True:
            x = random.randint(0, len(field[0]) - 1)
            y = random.randint(0, len(field) - 1)
            if field[y][x] != CellType.ROOM_SPACE or (y, x) in used:
                continue
            used.add((y, x))
            strength_bonus = random.randint(0, MAX_STRENGTH)
            health_bonus = random.randint(0, MAX_HEALTH)
            clothes[i] = ItemInitState(
                Coordinate(y, x),
                Armor(Bonus(strength_bonus, health_bonus), "Magical armor +{} +{}".format(strength_bonus,
                                                                                          health_bonus)))
            break
    return used, clothes


def _draw_paths(graph, field):
    for child in graph.neighbours:
        if child is not None:
            field = _draw_path_between_two_rooms(field, child, graph)
            field = _draw_paths(child, field)
    return field


def _draw_path_between_two_rooms(field, room1, room2):
    if room1.cornerx > room2.cornerx:
        room1, room2 = room2, room1
    if abs(room1.cornery - room2.cornery) <= room1.height and abs(room1.cornery - room2.cornery) <= room2.height:
        return _draw_single_path(field, room1.get_right_border(), room1.cornery + room1.height // 2, room2.cornerx,
                                 room2.cornery + room2.height // 2)
    if room1.cornery < room2.cornery:
        return _draw_single_path(field, room1.cornerx + room1.width // 2, room1.get_bottom_border(),
                                 room2.cornerx + room2.width // 2, room2.cornery)
    return _draw_single_path(field, room1.cornerx + room1.width // 2, room1.cornery, room2.cornerx + room2.width // 2,
                             room2.get_bottom_border())


def _draw_single_path(field, x1, y1, x2, y2):
    field[y1][x1] = CellType.DOOR
    field[y2][x2] = CellType.DOOR
    if abs(x1 - x2) + abs(y1 - y2) == 1:
        return field
    cx = x1
    cy = y1
    while abs(cx - x2) + abs(cy - y2) > 1:
        if random.randint(0, abs(cx - x2) + abs(cy - y2) - 1) < abs(cx - x2):
            cx += (x2 - cx) // abs(x2 - cx)
        else:
            cy += (y2 - cy) // abs(y2 - cy)
        if field[cy][cx] == CellType.VERTICAL_WALL or field[cy][cx] == CellType.HORIZONTAL_WALL:
            field[cy][cx] = CellType.DOOR
        elif field[cy][cx] == CellType.EMPTY_SPACE or field[cy][cx] == CellType.PATH:
            field[cy][cx] = CellType.PATH
        else:
            return field
    return field


def _draw_rooms_graph(root, field):
    if root is None:
        return field
    field = _draw_single_room(field, root)
    for r in root.neighbours:
        field = _draw_rooms_graph(r, field)
    return field


def _generate_rooms_graph(width, height, addx=0, addy=0):
    if width <= MIN_WIDTH or height <= MIN_HEIGHT:
        return None
    room_width = random.randint(MIN_WIDTH, min(MAX_WIDTH, width - 1))
    room_height = random.randint(MIN_HEIGHT, min(MAX_HEIGHT, height - 1))
    room_x = random.randint(0, width - room_width)
    room_y = random.randint(0, height - room_height)
    room = Room(room_x, room_y, room_width, room_height)
    room.cornerx += addx
    room.cornery += addy
    left = _generate_rooms_graph(room_x - 1, room_y + room_height - 1, addx, addy)
    right = _generate_rooms_graph(width - room_width - room_x - 1, height - room_y - 1, addx + room_x + room_width + 1,
                                  addy + room_y + 1)
    up = _generate_rooms_graph(width - room_x - 1, room_y - 1, addx + room_x + 1, addy)
    down = _generate_rooms_graph(room_x + room_width - 1, height - room_y - room_height - 1, addx,
                                 addy + room_y + room_height + 1)
    room.neighbours = [left, right, up, down]
    return room


def _draw_single_room(field, room):
    for j in range(room.height + 1):
        field[room.cornery + j][room.cornerx] = CellType.VERTICAL_WALL
        field[room.cornery + j][room.cornerx + room.width] = CellType.VERTICAL_WALL
    for i in range(room.width + 1):
        field[room.cornery][room.cornerx + i] = CellType.HORIZONTAL_WALL
        field[room.cornery + room.height][room.cornerx + i] = CellType.HORIZONTAL_WALL
    for i in range(1, room.width):
        for j in range(1, room.height):
            field[room.cornery + j][room.cornerx + i] = CellType.ROOM_SPACE
    return field


def _print_field(field):
    for line in field:
        for it in line:
            print(it.value, end="")
        print()
