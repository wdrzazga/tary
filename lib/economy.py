class Economy:
    def __init__(self, industry, agriculture, services, employment, govdebt):
        self.industry = industry
        self.agriculture = agriculture
        self.services = services
        self.gdp = industry + agriculture + services
        self.employment = employment
        self.govdebt = govdebt
        self.budget = 0
    def update(self):
        self.gdp = self.industry + self.agriculture + self.services