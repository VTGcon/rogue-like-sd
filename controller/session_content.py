class SessionContent:
    """
        Class storing game content including players' states, mobs and items.
    """

    def __init__(self, game_map):
        self.players_by_token = {}
        self.players_by_id = {}
        self.mobs = {}
        self.items = {}
        self.game_map = game_map

    def add_player(self, player):
        self.players_by_token[player.token] = player
        self.players_by_id[player.data.id] = player

    def add_mob(self, mob):
        self.mobs[mob.data.id] = mob

    def add_item(self, item):
        self.items[item.data.id] = item