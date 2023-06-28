import time

import pygame

from UI.KeyHandler import KeyHandler
from shared.command import AskMap, ChangeState, SendMap, SendItemsList, AskItemsList
from shared.common import Item, CellType
from shared.player_map import MoveType, ItemActionType, StateChange, PlayerMove, ItemAction


class UI:
    def __init__(self, commandReceiver, commandSender):
        self.__screen_height = None
        self.__screen_width = None
        self.__clock = None
        self.__screen = None
        self.__commandReceiver = commandReceiver
        self.__commandSender = commandSender
        self.__map = None
        self.__items = []
        self.__selected_item = 0
        self.__inventory = None
        self.__selected_helmet = False
        self.__selected_shirt = False
        self.__selected_weapon = False
        self.__fps = 60
        self.__font = None
        self.__type_to_color = {
            '-': (0, 0, 255),
            '|': (0, 0, 255),
            '*': (0, 255, 0),
            '.': (255, 0, 0),
            '%': (255, 255, 0),
            '#': (255, 0, 255),
            '!': (0, 255, 255),
            ' ': (0, 0, 0),
            '@': (255, 255, 255),
        }

    def start(self):
        """
            Start UI
        """
        pygame.init()
        self.__map = self.__get_map_from_controller().map
        self.__screen_width = len(self.__map.map) + 50
        self.__screen_height = len(self.__map.map[0]) + 20

        self.__screen = pygame.display.set_mode((self.__screen_width * 10, self.__screen_height * 10))
        pygame.display.set_caption("Roguelike")
        self.__clock = pygame.time.Clock()

        self.__font = pygame.font.SysFont("monospace", 24)

        self.__lifecicle()

    def __get_map_from_controller(self):
        self.__ask_map()
        while self.__commandReceiver.is_empty():
            time.sleep(1)
        return self.__commandReceiver.pop()

    def __ask_map(self):
        self.__commandSender.put(AskMap())

    def __ask_items(self):
        self.__commandSender.put(AskItemsList())

    def __send_move(self, move: MoveType):
        self.__commandSender.put(ChangeState(StateChange(PlayerMove(move))))

    def __send_item_action(self, action: ItemActionType, item: Item):
        self.__commandSender.put(ChangeState(StateChange(ItemAction(action, item))))

    def __make_command(self):
        while not self.__commandReceiver.is_empty():
            command = self.__commandReceiver.pop()
            if command.__class__ == SendMap:
                self.__map = command.map
            elif command.__class__ == SendItemsList:
                self.__items = list(command.items.items.values())
                self.__inventory = command.items

    def __lifecicle(self):
        while True:
            self.__screen.fill((0, 0, 0))
            ks = pygame.event.get()
            ks = [x for x in ks if x.type == pygame.KEYDOWN]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
            if not self.__commandReceiver.is_empty():
                self.__make_command()
            self.__write_items(self.__items, self.__map)
            self.__write_inventory()
            self.__draw_map(self.__map.map)
            self.__draw_hero(self.__map.player.coordinate.x, self.__map.player.coordinate.y)
            self.__write_status(self.__map)
            self.__write_health(self.__map)
            action = self.__handle_keys(ks)
            if action is not None:
                self.__send_move(action)
            self.__ask_map()
            self.__ask_items()
            pygame.display.update()
            self.__clock.tick(self.__fps)

        pygame.quit()

    def __handle_keys(self, keys):
        res = KeyHandler.handle_move_key(keys)
        if res is not None:
            return res

        res = KeyHandler.handle_inventory_position(keys)
        if res is not None:
            self.__selected_item = res

        if len(keys) == 0:
            return
        k = keys[0]
        res = KeyHandler.handle_clothes(k, self.__inventory)
        if res is not None:
            self.__selected_helmet, self.__selected_shirt, self.__selected_weapon = res

        res = KeyHandler.handle_act(k)
        if res is not None:
            self.__make_actions(res)

        res = KeyHandler.handle_game_state(k)
        if res is not None:
            self.__commandSender.put(res)

    def __make_actions(self, key):
        action = KeyHandler.handle_act(key)
        if action is None and not (0 < self.__selected_item <= len(self.__items)
                                   or self.__selected_helmet or self.__selected_shirt or self.__selected_weapon):
            return
        if action == KeyHandler.ACTION_DROP:
            self.__make_action(ItemActionType.DROP)
        elif action == KeyHandler.ACTION_WEAR:
            self.__make_action(ItemActionType.WEAR)
        elif action == KeyHandler.ACTION_USE:
            self.__make_action(ItemActionType.USE)
        elif action == KeyHandler.ACTION_REMOVE_FROM_SLOT:
            self.__make_action(ItemActionType.REMOVE_FROM_SLOT)

    def __make_action(self, type):
        if 0 < self.__selected_item <= len(self.__items):
            self.__send_item_action(type, self.__items[self.__selected_item - 1])
        elif self.__selected_helmet:
            self.__send_item_action(type, self.__inventory.active_helmet)
        elif self.__selected_shirt:
            self.__send_item_action(type, self.__inventory.active_shirt)
        elif self.__selected_weapon:
            self.__send_item_action(type, self.__inventory.active_weapon)

    def __draw_map(self, map_array):
        for i in range(len(map_array)):
            for j in range(len(map_array[i])):
                pygame.draw.rect(self.__screen, self.__type_to_color[map_array[i][j]], (j * 10, i * 10, 10, 10))

    def __draw_hero(self, pos_x, pos_y):
        pygame.draw.rect(self.__screen, self.__type_to_color['@'], (pos_y * 10, pos_x * 10, 10, 10))

    def __write_status(self, map):
        status = "STATUS:"
        img = self.__font.render(status + map.status_message, True, (255, 255, 255))
        self.__screen.blit(img, (10, (len(map.map) + 12+6) * 10))

    def __write_health(self, map):
        status = "HEALTH:"
        img = self.__font.render(status + str(map.player.fight_stats.get_health()), True, (255, 255, 255))
        self.__screen.blit(img, (10, (len(map.map) + 12) * 10))

        status = "STRENGTH:"
        img = self.__font.render(status + str(map.player.fight_stats.get_strength()), True, (255, 255, 255))
        self.__screen.blit(img, (10, (len(map.map) + 12+3) * 10))

    def __write_items(self, items, map):
        padding_right = len(map.map) + 10
        padding_top = 0
        for ind, item in enumerate(items):
            if ind + 1 == self.__selected_item:
                self.__write_item(item, padding_right, padding_top, True)
            else:
                self.__write_item(item, padding_right, padding_top)
            padding_top += 1

    def __write_inventory(self):
        if not self.__inventory:
            return
        padding_top = len(self.__map.map) + 16
        if self.__inventory.active_helmet:
            self.__write_item(self.__inventory.active_helmet, 0, padding_top)
        if self.__inventory.active_shirt:
            self.__write_item(self.__inventory.active_shirt, 0, padding_top)
        if self.__inventory.active_weapon:
            self.__write_item(self.__inventory.active_weapon, 0, padding_top)

    def __write_item(self, item, padding_right, padding_top, selected=False):
        txt = item.name
        if selected:
            txt = "* " + txt
            padding_right += 1
        img = self.__font.render(txt, True, (255, 255, 255))
        self.__screen.blit(img, (padding_right * 10, padding_top * 15))
