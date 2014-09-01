import logging

logger = logging.getLogger()

import bit
import tables


class Physical:
    def __init__(self):
        super().__init__()
        self.name = ""
        self.short_descr = ""
        self.long_descr = ""
        self.description = ""
        self.size = 0
        self.material = ""
        self.weight = 0
