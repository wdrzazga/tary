#from lib.economy import Economy

from lib.economy import Economy


class CommunistEconomy(Economy):
    def __init__(self, industry, agriculture, services):
        super().__init__(industry, agriculture, services, 1.0, 0)