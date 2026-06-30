import random

class Event:
    def __init__(self, effects):
        self.effects = effects
    def __call__(self, country):
        for effect in self.effects:
            exec(effect)

rebelion = Event(['country.rebelions += 1'])
famine = Event(['population_loss = random.randint(int(country.population // 1000), int(country.population // 5 + 1))',
'economy_loss = population_loss * (country.gdp / country.population) / 2)',
'country.population -= population_loss',
'country.economy.agriculture -= economy_loss // 2',
'country.economy.services -= economy_loss // 4',
'country.economy.update()'])
#rm - raw materials
rm_discovery = Event(['country.economy.industry += country.economy.industry * 0.05'])
science_discovery = Event(['field = random.choice(["medicine", "military", "automation"])',
f'country.tech.{field} += 0.05'])