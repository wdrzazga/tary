class Party:
    """Partia w parlamencie: ma własne poparcie, miejsca oraz preferowaną
    opcję dla każdego prawa (indeks opcji w danym prawie)."""

    def __init__(self, name, support, preferences, is_player=False):
        self.name = name
        self.support = support
        self.seats = support  # miejsca z ostatnich wyborów; na starcie = poparcie
        self.preferences = preferences  # klucz prawa -> preferowany indeks opcji
        self.is_player = is_player

    def approves(self, law_key, current_option, proposed_option):
        """Partia popiera zmianę, która przybliża prawo do jej preferencji
        (a odrzuca taką, która od niej oddala) — decyzja nie jest losowa."""
        preferred = self.preferences[law_key]
        return abs(proposed_option - preferred) < abs(current_option - preferred)
