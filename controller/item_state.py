from controller.map_object_state import MapObjectState
from shared.map_init import ItemInitState


class ItemState(MapObjectState):
    """
        State of the item lying on a map.
    """
    class ItemData(MapObjectState.MapObjectData):
        def __init__(self, item: ItemInitState):
            super().__init__(item)
            self.item = item.item

    def __init__(self, item: ItemInitState):
        self.data = ItemState.ItemData(item)