import pygame

from shared.command import SaveGame, LoadGame
from shared.player_map import MoveType


class KeyHandler:
    ACTION_DROP = 1
    ACTION_USE = 2
    ACTION_WEAR = 3
    ACTION_REMOVE_FROM_SLOT = 4

    @staticmethod
    def handle_move_key(event):
        """
        convert key code into move
        :param key:
        :return:
        """
        for event in event:
            if event.key == pygame.K_UP:
                return MoveType.UP
            elif event.key == pygame.K_DOWN:
                return MoveType.DOWN
            elif event.key == pygame.K_LEFT:
                return MoveType.LEFT
            elif event.key == pygame.K_RIGHT:
                return MoveType.RIGHT
            else:
                return None

    @staticmethod
    def handle_inventory_position(events):
        """
        convert key code into inventory number
        :param key:
        :return:
        """
        for event in events:
            if event.key in range(pygame.K_1, pygame.K_9 + 1):
                return event.key - pygame.K_1 + 1

    @staticmethod
    def handle_clothes(key, inventory):
        """
        convert key code into clothes inventory choose
        :param key:
        :param inventory:
        :return:
        """
        if key.key == pygame.K_i and inventory.active_helmet:
            return True, False, False
        if key.key == pygame.K_o and inventory.active_shirt:
            return False, True, False
        if key.key == pygame.K_o and inventory.active_weapon:
            return False, False, True

    @staticmethod
    def handle_game_state(key):
        """
        convert key code into game command
        :param key:
        :return:
        """
        if key.key == pygame.K_s:
            return SaveGame()
        elif key.key == pygame.K_l:
            return LoadGame()
        else:
            return None

    @staticmethod
    def handle_act(key):
        """
        convert key code into action
        :param key:
        :return:
        """
        if key.key == pygame.K_q:
            return KeyHandler.ACTION_DROP
        elif key.key == pygame.K_w:
            return KeyHandler.ACTION_USE
        elif key.key == pygame.K_e:
            return KeyHandler.ACTION_WEAR
        elif key.key == pygame.K_r:
            return KeyHandler.ACTION_REMOVE_FROM_SLOT
        else:
            return None
