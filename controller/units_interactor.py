from controller.player_state import DeadPlayer
from controller.item_state import ItemState
from controller.mob_state import MobState
from controller.map_view import MapView
from controller.unit_state import UnitState
from controller.session_content import SessionContent
from shared.common import Item
from shared.map_init import ItemInitState


class UnitsInteractor:
    """
        Class providing interface for interaction between player, mobs and items.

        The main intention was to hide the whole information and data controls of the map from
        units and provide them only with accessible information.
    """
    def __init__(self, game_content: SessionContent):
        self.__game_content = game_content

    def attack(self, attacker, attack):
        unit = None
        if attack.target in self.__game_content.mobs:
            unit = self.__game_content.mobs[attack.target]
        elif attack.target in self.__game_content.players_by_id:
            unit = self.__game_content.players_by_id[attack.target]
        assert unit is not None
        unit.get_damaged(attack)
        if attack.confusion and unit is MobState:
            unit.confuse()
        if unit.data.fight_stats.get_health() <= 0:
            if unit.data.unit_type is UnitState.UnitType.MOB:
                del self.__game_content.mobs[unit.data.id]
            elif unit.data.unit_type is UnitState.UnitType.PLAYER:
                self.__game_content.players_by_id[unit.data.id] = DeadPlayer(
                    self.__game_content.players_by_id[unit.data.id])
                self.__game_content.players_by_token[unit.token] = DeadPlayer(
                    self.__game_content.players_by_token[unit.token])

    def get_context(self, unit):
        mask = unit.get_visible_area()

        return MapView([MapView.MobView(mob.data.id, mob.data.coordinate)
                        for mob in self.__game_content.mobs.values()
                        if mask[mob.data.coordinate.x][mob.data.coordinate.y]],
                       [MapView.PlayerView(player.data.id, player.data.coordinate)
                        for player in self.__game_content.players_by_id.values()
                        if mask[player.data.coordinate.x][player.data.coordinate.y]])

    def drop_item(self, item: Item, player):
        if player.inventory_controller.remove_item(item):
            self.__game_content.add_item(ItemState(ItemInitState(player.data.coordinate, item)))
            return True
        return False

    def pick_items(self, player):
        picked_items = list(
            filter(lambda x: x.data.coordinate == player.data.coordinate, self.__game_content.items.values()))
        self.__game_content.items = {x.data.id: x for x in
                                     filter(lambda x: not x.data.coordinate == player.data.coordinate,
                                            self.__game_content.items.values())}
        for item in picked_items:
            player.inventory_controller.add_item(item.data.item)