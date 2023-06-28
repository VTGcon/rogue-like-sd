import random
from abc import ABC

from shared import player_map
from shared.common import CellType
from shared.player_map import MoveType


class MobStrategy(ABC):
    """
        Abstract class for mob strategy among all the actions choosing the one with the maximum weight.
    """
    @classmethod
    def act(cls, mob, context):
        direction = None
        best_weight = None

        for delta in mob.move_deltas:
            weight = cls.action_weight(player_map.StateChange(player_map.PlayerMove(delta)), mob, context)
            if weight is None:
                continue
            if (direction is None) or (weight > best_weight):
                direction = delta
                best_weight = weight
        mob.change_state(player_map.StateChange(player_map.PlayerMove(direction)))

    WEIGHT_INFTY = 1000000000

    @classmethod
    def action_weight(cls, state_change, mob, context):
        raise NotImplementedError()


class PlayersDistanceBasedMobStrategy(MobStrategy, ABC):
    """
        Abstract class for wighted mob strategy that depends on the distace from players.
    """
    @classmethod
    def dist_weight(cls, state_change, mob, context):
        if not context.player_views:
            # No players nearby
            return 0 if state_change.change.move_type is MoveType.NO else None

        new_coordinate = mob.data.coordinate + mob.move_deltas[state_change.change.move_type]
        cell = mob.data.map.get_cell(new_coordinate.x, new_coordinate.y)
        if cell not in [CellType.PATH, CellType.DOOR, CellType.ROOM_SPACE]:
            return None
        return min([abs(player.coordinate.x - new_coordinate.x) + abs(player.coordinate.y - new_coordinate.y) + 1
                    for player in context.player_views])


class AggressiveStrategy(PlayersDistanceBasedMobStrategy):
    """
        Mob strategy that chases the nearest visible player.
    """
    @classmethod
    def action_weight(cls, state_change, mob, context):
        weight = super().dist_weight(state_change, mob, context)
        return -weight if weight is not None else None


class PassiveStrategy(MobStrategy):
    """
        Mob strategy that does nothing.
    """
    @classmethod
    def action_weight(cls, state_change, mob, context):
        # Does nothing
        return 0 if state_change.change is MoveType.NO else -1


class FrightenedStrategy(PlayersDistanceBasedMobStrategy):
    """
        Mob strategy that hides from the nearest visible player.
    """
    @classmethod
    def action_weight(cls, state_change, mob, context):
        return super().dist_weight(state_change, mob, context)


class ConfusedStrategy(MobStrategy):
    """
        Mob strategy that goes in a random direction.
    """
    def __init__(self, strategy):
        if strategy is ConfusedStrategy:
            strategy = strategy.strategy
        self.strategy = strategy
        self.counter = random.randint(2, 5)

    def action_weight(self, state_change, mob, context):
        self.counter -= 1
        return random.randint(-10, 10) if self.counter >= 0 else self.strategy.action_weight(state_change, mob, context)