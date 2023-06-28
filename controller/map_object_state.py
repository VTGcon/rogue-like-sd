import uuid
from abc import ABC

from shared.map_init import MapObjectInitState


class MapObjectState(ABC):
    """
        Class storing a map object location.
    """
    class MapObjectData:
        def __init__(self, obj: MapObjectInitState):
            self.id = uuid.uuid4()
            self.coordinate = obj.coordinate