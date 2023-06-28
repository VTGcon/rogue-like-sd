from shared.common import Coordinate


class MapView:
    """
        Class restricting seen information to position/id metadata.
    """
    class MapObjectView:
        def __init__(self, id, coordinate: Coordinate):
            self.id = id
            self.coordinate = coordinate

    class MobView(MapObjectView):
        pass

    class PlayerView(MapObjectView):
        pass

    def __init__(self, mobs, players):
        self.mob_views = mobs
        self.player_views = players