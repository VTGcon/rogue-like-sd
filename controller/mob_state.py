from controller.mob_strategy import AggressiveStrategy, PassiveStrategy, FrightenedStrategy, ConfusedStrategy
from controller.unit_state import UnitState
from shared.map_init import ModMode


class MobState(UnitState):
    """
        Class for automated unit holding its action course.
    """
    def __init__(self, game_map, mob, game_interactor):
        super().__init__(game_map, mob, game_interactor)
        self.data.unit_type = UnitState.UnitType.MOB
        self.strategy = {
            ModMode.AGGRESSIVE: AggressiveStrategy,
            ModMode.PASSIVE: PassiveStrategy,
            ModMode.FRIGHTENED: FrightenedStrategy
        }[mob.mob_mode]

    def act(self):
        self.strategy.act(self, self.game_interactor.get_context(self))

    def confuse(self):
        self.strategy = ConfusedStrategy(self.strategy)