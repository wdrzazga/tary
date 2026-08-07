import random
from games.demokratar.law import Law
from games.demokratar.economy import MarketEconomy
from games.demokratar.party import Party
from lib.technology import Technology


class DemocraticCountry:
    def __init__(self, seed=None, elections_every=20):
        # wybory domyślnie co 20 tur, można zmienić (wartość <= 0 nie miałaby sensu)
        self.elections_every = elections_every if elections_every > 0 else 20
        self.turn = 0
        self.in_power = True
        self.budget = 0

        if seed is None:
            seed = random.randint(0, 100000)
        self.seed = seed
        random.seed(self.seed)

        self.population = random.randint(10_000, 100_000_000)

        gdp = round((self.population * random.randint(1000, 80_000) / 1_000_000), 4)  # PKB w milionach
        ser_pr = random.randint(40, 70)  # gospodarka rynkowa: dominują usługi
        ind_pr = random.randint(1, 100 - ser_pr)
        agr_pr = 100 - ser_pr - ind_pr
        services = gdp * ser_pr // 100
        industry = gdp * ind_pr // 100
        agriculture = gdp * agr_pr // 100
        employment = round(random.uniform(0.55, 0.75), 2)
        self.economy = MarketEconomy(industry, agriculture, services, employment)

        self.laws = {
            "taxation": Law(("Niskie", "Średnie", "Wysokie"),
                            ("Mniejsze wpływy, większe szczęście", "", "Większe wpływy, mniejsze szczęście"),
                            (0.1, 0.0, -0.1)),
            "freedom_of_speech": Law(("Pełna", "Ograniczona"),
                                     ("", "Cenzura mediów"),
                                     (0.1, -0.15)),
            "welfare": Law(("Minimalne", "Umiarkowane", "Rozbudowane"),
                           ("Tanie, ale niepopularne", "", "Drogie, ale popularne"),
                           (-0.05, 0.05, 0.1)),
            "market_regulation": Law(("Wolny rynek", "Regulowany"),
                                     ("Szybszy wzrost, większe nierówności", "Wolniejszy wzrost, stabilność"),
                                     (0.0, 0.05)),
        }
        # Indeksy aktywnych praw: podatki, wolność słowa, socjal, regulacja rynku
        self.laws_active = [1, 0, 1, 0]

        self.happiness = 0.6 + round(random.uniform(-0.1, 0.1), 2)

        player_support = 0.2 + round(random.uniform(-0.1, 0.1), 2)
        self.parties = self.create_parties(player_support)
        self.player_party = self.parties[0]

        self.tech = Technology(seed)
        random.seed()

    # Poparcie i miejsca gracza to poparcie i miejsca jego partii —
    # właściwości pozwalają reszcie kodu (kampanie, wydarzenia, statystyki)
    # działać bez zmian.
    @property
    def party_support(self):
        return self.player_party.support

    @party_support.setter
    def party_support(self, value):
        self.player_party.support = value

    @property
    def seats(self):
        return self.player_party.seats

    @seats.setter
    def seats(self, value):
        self.player_party.seats = value

    def create_parties(self, player_support):
        law_keys = list(self.laws.keys())
        # Preferencje gracza = jego program (obecne ustawienia praw)
        player_prefs = {key: self.laws_active[i] for i, key in enumerate(law_keys)}
        player = Party("Twoja partia", player_support, player_prefs, is_player=True)

        opposition_names = ("Liberałowie", "Konserwatyści", "Socjaldemokraci")
        parties = [player]
        weights = []
        for name in opposition_names:
            prefs = {key: random.randrange(len(self.laws[key].options)) for key in law_keys}
            weights.append(random.uniform(0.5, 1.5))
            parties.append(Party(name, 0.0, prefs))

        # Reszta elektoratu dzielona między opozycję proporcjonalnie do wag
        remaining = max(0.0, 1.0 - player_support)
        total = sum(weights)
        for party, weight in zip(parties[1:], weights):
            party.support = weight / total * remaining
            party.seats = party.support
        return parties

    def normalize_support(self):
        """Poparcia wszystkich partii sumują się do 100%: partie opozycji
        dzielą między siebie elektorat, którego nie ma partia gracza."""
        others = [party for party in self.parties if not party.is_player]
        remaining = max(0.0, 1.0 - self.player_party.support)
        total = sum(party.support for party in others)
        if total > 0:
            for party in others:
                party.support = party.support / total * remaining
        else:
            for party in others:
                party.support = remaining / len(others)

    def end_turn(self):
        self.turn += 1
        self.update_stats()
        messages = []
        event = self.random_event()
        if event:
            messages.append(event)
        if self.turn % self.elections_every == 0:
            messages.append(self.hold_election())
        return messages

    def update_stats(self):
        population_growth = 0.01 + random.uniform(-0.005, 0.005)
        self.population += int(self.population * population_growth)

        tax_level = self.laws_active[0]
        regulation = self.laws_active[3]
        economy_growth = 0.02 - 0.005 * tax_level - 0.005 * regulation
        economy_growth += random.uniform(-0.01, 0.01)
        self.economy.grow(economy_growth)

        tax_rate = (0.1, 0.2, 0.3)[tax_level]                  # podatek: 10–30% PKB
        welfare_rate = (0.05, 0.12, 0.20)[self.laws_active[2]]  # koszt socjalu: 5–20% PKB
        self.budget += self.economy.gdp * tax_rate
        self.budget -= self.economy.gdp * welfare_rate

        self.update_support(economy_growth)
        self.apply_debt_penalty()
        self.normalize_support()

    def update_support(self, economy_growth):
        delta = economy_growth * 2
        delta += (self.happiness - 0.5) * 0.1
        delta += random.uniform(-0.03, 0.03)
        self.party_support = max(0.0, min(1.0, self.party_support + delta))

    def apply_debt_penalty(self):
        """Deficyt budżetowy uderza w rządzącą (Twoją) partię: im głębszy dług
        względem PKB, tym większy spadek szczęścia i poparcia (do 5% na turę)."""
        if self.budget >= 0:
            return
        debt_ratio = min(1.0, -self.budget / (self.economy.gdp + 1))
        penalty = round(0.01 + 0.04 * debt_ratio, 3)  # 1%–5% na turę zależnie od skali długu
        self.happiness = max(0.0, self.happiness - penalty)
        self.party_support = max(0.0, self.party_support - penalty)

    def random_event(self):
        r = random.random()
        if r < 0.1:
            loss = round(random.uniform(0.05, 0.15), 2)
            self.party_support = max(0.0, self.party_support - loss)
            return f"Skandal polityczny! Poparcie partii spadło o {int(loss * 100)}%"
        elif r < 0.2:
            self.happiness = min(1.0, self.happiness + 0.05)
            return "Boom gospodarczy! Szczęście obywateli rośnie."
        elif r < 0.3:
            self.happiness = max(0.0, self.happiness - 0.05)
            return "Protesty uliczne. Szczęście obywateli spada."
        else:
            return False

    def hold_election(self):
        self.normalize_support()
        for party in self.parties:
            party.seats = party.support  # nowy podział miejsc według poparcia z wyborów
        winner = max(self.parties, key=lambda party: party.support)  # przy remisie wygrywa gracz (jest pierwszy)
        if winner is self.player_party:
            self.happiness = min(1.0, self.happiness + 0.05)
            return (f"WYBORY: wygrana! Poparcie {int(self.player_party.support * 100)}%, "
                    f"miejsca w parlamencie {int(self.player_party.seats * 100)}%.")
        self.in_power = False
        return (f"WYBORY: przegrana. Wygrywa {winner.name} "
                f"({int(winner.support * 100)}% poparcia) — tracisz władzę.")

    def propose_law(self, law_index, option_index):
        """Decyzję podejmuje parlament. Twoja partia głosuje za, a każda partia
        opozycji popiera zmianę tylko wtedy, gdy przybliża prawo do jej
        preferencji. Ustawa przechodzi przy ponad 50% miejsc za."""
        law_key = list(self.laws.keys())[law_index]
        law = self.laws[law_key]
        current = self.laws_active[law_index]
        if option_index == current:
            return "To prawo już obowiązuje."

        votes_for = 0.0
        supporters = []
        for party in self.parties:
            if party.is_player or party.approves(law_key, current, option_index):
                votes_for += party.seats
                supporters.append(party.name)

        if votes_for > 0.5:
            delta = law.happiness_effects[option_index] - law.happiness_effects[current]
            self.happiness = max(0.0, min(1.0, self.happiness + delta))
            self.laws_active[law_index] = option_index
            self.budget -= self.population // 100_000
            return f"Ustawa przyjęta ({int(votes_for * 100)}% miejsc za). Za: {', '.join(supporters)}."
        return (f"Ustawa odrzucona ({int(votes_for * 100)}% miejsc za). "
                f"Potrzeba ponad 50% miejsc w parlamencie.")

    def hold_rally(self):
        cost = self.population // 1000
        if self.budget >= cost:
            self.budget -= cost
            gain = round(random.uniform(0.02, 0.06), 2)
            self.party_support = min(1.0, self.party_support + gain)
            self.normalize_support()
            return f"Wiec wyborczy! Poparcie wzrosło o {int(gain * 100)}%"
        return f"Za mało pieniędzy w skarbcu. Koszt wiecu: {cost}"

    def ad_campaign(self):
        cost = self.population // 500
        if self.budget >= cost:
            self.budget -= cost
            change = round(random.uniform(-0.01, 0.1), 2)
            self.party_support = max(0.0, min(1.0, self.party_support + change))
            self.normalize_support()
            return f"Kampania reklamowa. Zmiana poparcia: {int(change * 100)}%"
        return f"Za mało pieniędzy w skarbcu. Koszt kampanii: {cost}"

    def invest(self, amount):
        self.budget -= amount
        self.economy.gdp += round(random.uniform(-0.05, 0.3), 2) * 3 * amount

    def social_program(self, amount):
        self.budget -= amount
        boost = min(0.1, amount / (self.population + 1))
        self.happiness = min(1.0, self.happiness + boost)
        self.party_support = min(1.0, self.party_support + boost / 2)
        self.normalize_support()

    def stats(self):
        print("\n\n")
        print("Tura: ", self.turn)
        print("Populacja: ", self.population)
        print("PKB (w milionach): ", self.economy.gdp)
        print("PKB na osobę (w milionach): ", round(self.economy.gdp / self.population, 2))
        print("Zatrudnienie: ", int(self.economy.employment * 100), "%")
        print("Szczęście: ", int(self.happiness * 100), "%")
        print("Poparcie partii: ", int(self.party_support * 100), "%")
        print("Miejsca w parlamencie: ", int(self.seats * 100), "%")
        print("Skarbiec: ", self.budget)
        print("Następne wybory za: ", self.elections_every - (self.turn % self.elections_every), "tur")
        print("Parlament:")
        for party in self.parties:
            marker = " (Ty)" if party.is_player else ""
            print(f"  {party.name}{marker}: {int(party.support * 100)}% poparcia, "
                  f"{int(party.seats * 100)}% miejsc")
