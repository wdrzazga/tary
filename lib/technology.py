import random

class Technology:
    def __init__(self, seed):
        random.seed(seed)
        self.medicine = round(random.uniform(0.01, 0.6), 2)
        self.military = round(random.uniform(0.01, 0.6), 2)
        self.automation = round(random.uniform(0.01, 0.6))