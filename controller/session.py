from controller.item_state import ItemState
from controller.mob_state import MobState
from controller.player_state import PlayerState
from controller.session_content import SessionContent
from controller.units_interactor import UnitsInteractor
from shared.common import CellType


class Session:
    """
        Class storing and controlling single game session.
    """

    def __init__(self, players, game_map, mobs=None, items=None):
        if mobs is None:
            mobs = []
        if items is None:
            items = []
        self.game_content = SessionContent(game_map)
        self.units_interactor = UnitsInteractor(self.game_content)

        for player in players:
            self.game_content.add_player(PlayerState(game_map, player, self.units_interactor))

        for mob in mobs:
            self.game_content.add_mob(MobState(game_map, mob, self.units_interactor))

        for item in items:
            self.game_content.add_item(ItemState(item))

    def change_player_state(self, player_token, state_change):
        player = self.game_content.players_by_token[player_token]
        player.change_state(state_change)
        for mob in list(self.game_content.mobs.values()):
            if mob.data.fight_stats.get_health() > 0:
                mob.act()

    def dump_map(self, mask=None):
        result_map = []
        for i in range(self.game_content.game_map.height):
            result_map.append([])
            for j in range(self.game_content.game_map.width):
                result_map[-1].append(
                    (self.game_content.game_map.get_cell(i, j)
                     if mask is None or mask[i][j]
                     else CellType.EMPTY_SPACE).value)
        for item in self.game_content.items.values():
            if mask is None or mask[item.data.coordinate.x][item.data.coordinate.y]:
                result_map[item.data.coordinate.x][item.data.coordinate.y] = CellType.ITEM.value
        for mob in self.game_content.mobs.values():
            if mask is None or mask[mob.data.coordinate.x][mob.data.coordinate.y]:
                result_map[mob.data.coordinate.x][mob.data.coordinate.y] = CellType.MOB.value
        return result_map

    def dump_players_map(self, players_token):
        return self.dump_map(self.game_content.players_by_token[players_token].mask)

    def player_status(self, player_token):
        status = self.game_content.players_by_token[player_token].status
        self.game_content.players_by_token[player_token].status = ""
        return status

