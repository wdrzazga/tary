from lib.economy import Economy


class MarketEconomy(Economy):
    """Gospodarka rynkowa liberalnej demokracji: dominują usługi,
    a wzrost napędza zatrudnienie (inaczej niż w gospodarce planowej)."""

    def __init__(self, industry, agriculture, services, employment=0.6):
        super().__init__(industry, agriculture, services, employment, 0)

    def grow(self, growth):
        employment_factor = 0.5 + self.employment  # wysokie zatrudnienie wzmacnia wzrost
        self.services += self.services * growth * 0.5 * employment_factor
        self.industry += self.industry * growth * 0.3 * employment_factor
        self.agriculture += self.agriculture * growth * 0.2 * employment_factor
        self.update()
