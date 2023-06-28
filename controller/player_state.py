from controller.unit_state import UnitState
from shared.common import Item, Usable, Wearable, Bonus
from shared.map_init import PlayerInitState
from shared.player_map import Inventory, PlayerMove, ItemAction, ItemActionType


class InventoryController:
    """
        Class providing basic actions with player's inventory.
    """
    def __init__(self, inventory: Inventory):
        self.inventory = inventory
        self.active_bonuses = {}

    def add_item(self, item: Item):
        self.inventory.items[item.id] = item
        return True

    def remove_item(self, item: Item):
        if item.id in self.inventory.items:
            del self.inventory.items[item.id]
            return True
        return False

    def use_item(self, item: Usable):
        result = self.remove_item(item)
        if result:
            self.active_bonuses[item.id] = item.bonus
        return result

    def wear_item(self, item: Wearable):
        result = item.wear(self.inventory)
        if result:
            self.active_bonuses[item.id] = item.bonus
        return result

    def take_off_item(self, item: Wearable):
        result = item.take_off(self.inventory)
        if result:
            del self.active_bonuses[item.id]
        return result

    def get_bonus(self):
        return sum(self.active_bonuses.values(), Bonus(0, 0))


class PlayerState(UnitState):
    """
        Class providing player-specific unit actions as item/inventory interactions and state updates.
    """
    class PlayerData(UnitState.UnitData):
        def __init__(self, game_map, player: PlayerInitState):
            super().__init__(game_map, player)
            self.inventory = Inventory()

    def __init__(self, game_map, player, game_interactor):
        super().__init__(game_map, player, game_interactor)
        self.data = PlayerState.PlayerData(game_map, player)
        self.data.unit_type = UnitState.UnitType.PLAYER
        self.token = player.token
        self.inventory_controller = InventoryController(self.data.inventory)
        self.status = ""
        self.mask = [[0 for _ in range(game_map.width)] for _ in range(game_map.height)]
        self.update_visible_area(self.get_visible_area())

    def update_visible_area(self, another_mask):
        self.mask = [[another_mask[i][j] or self.mask[i][j]
                      for j in range(self.data.map.width)]
                     for i in range(self.data.map.height)]

    def __update(self):
        self.data.fight_stats.update_bonus(self.inventory_controller.get_bonus())

    def change_state(self, state_change):
        if isinstance(state_change.change, PlayerMove):
            super().change_state(state_change)
            self.update_visible_area(self.get_visible_area())
            self.game_interactor.pick_items(self)

        if isinstance(state_change.change, ItemAction):
            item_action: ItemAction = state_change.change
            action_message = {
                ItemActionType.DROP: lambda: "" if self.game_interactor.drop_item(item_action.item,
                                                                                  self) else "Unable to drop item.",
                ItemActionType.REMOVE_FROM_SLOT: lambda: "" if self.inventory_controller.take_off_item(
                    item_action.item) else "Can't take item off.",
                ItemActionType.USE: lambda: "" if self.inventory_controller.use_item(
                    item_action.item) else "Can't use item.",
                ItemActionType.WEAR: lambda: "" if self.inventory_controller.wear_item(
                    item_action.item) else "Can't put item on.",
            }[item_action.action_type]()
            self.status += action_message + " "
        self.__update()


class DeadPlayer(PlayerState):
    """
        Decorator for the player whose health is 0.
    """
    def __init__(self, player_state: PlayerState):
        self.mask = None
        self.token = player_state.token
        self.data = player_state.data
        self.status = "You are dead"

    def update_visible_area(self, another_mask):
        return

    def change_state(self, state_change):
        return

    def get_visible_area(self):
        return None

    def get_damaged(self, unit_attack):
        return