from bit import Bit
from living import Living
import merc
from tables import off_flags


class Mobile(Living):
    def __init__(self):
        super().__init__()
        self.memory = None
        self.spec_fun = None
        self.mobTemplate = 0
        self.off_flags = Bit(flags=off_flags)
        self.damage = [0, 0, 0]
        self.start_pos = 0
        self.default_pos = 0


