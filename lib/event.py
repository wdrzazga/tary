class Event:
    def __init__(self, effects):
        self.effects = effects
    def __call__(self, country):
        for effect in self.effects:
            exec(effect)

rebelion = Event(['country.rebelions += 1'])
