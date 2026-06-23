import random
from games.komunistar.law import Law
from games.komunistar.economy import CommunistEconomy

class CommunistCountry:
    def __init__(self, seed=None):
        self.budget = 0
        if seed is None:
            seed = random.randint(0, 100000)
        self.seed = seed
        random.seed(self.seed)

        self.rebelions = 0
        self.mil = round(random.uniform(0.01, 0.1), 2) #Procent populacji, która jest w milicji i wojsku
        self.population = random.randint(10_000, 100_000_000)

        gdp = round((self.population * (random.randint(1000, 80_000)) / 1_000_000), 4) #PKB w milionach, ekonomia per capita między 0.001, a 0.08
        agr_pr = random.randint(1, 100)
        ind_pr = random.randint(1, 100 - agr_pr)
        ser_pr = random.randint(1, 100 - agr_pr - ind_pr)
        agr = gdp * agr_pr // 100
        ind = gdp * ind_pr // 100
        ser = gdp * ser_pr // 100

        self.economy = CommunistEconomy(ind, agr, ser)
        self.laws = { #Brak opisów, kiedy nazwa mówi o wszystkim
            "birth_law": Law(["Podatek bezdzietności", "brak", "Prawo dwóch dzieci", "Prawo jednego dziecka"], ['Dodatkowy podatek za nie posiadanie dzieci', '', 'Kary za posiadanie więcej niż 2 dzieci', 'Kary za posiadanie więcej niż 1 dziecko'], [-0.05, 0.1, -0.1, -0.15]),
            "freedom_of_speech": Law(["tak", "nie"], ['', ''], [0.1, -0.1]),
            "federalisation_level": Law(['1', '2', '3', '4', '5'], ["Całkowita centralizacja", '', '', '', "Konfederacja"], [-0.15, -0.07, 0, 0.07, 0.15]), #Federalizacja zwiększa szczęście, ale zmniejsza kontrolę
            "private_companies": Law(["tak", "nie"], ['', ''], [0, 0])
        }
        self.laws_active = [0, 1, 1, 0] #Indeksy aktywnych praw. Domyślnie ustawione, ale gracz może zmienić
        self.happiness = 0.8 + round(random.uniform(-0.1, 0.1), 2)

        self.control = self.calculate_control()
        random.seed()

    def random_event(self):
        eco_per_capita = self.economy.gdp / self.population
        rebelion_range = (0.0, (((1 - self.happiness) - self.mil)) / 5) if self.laws_active[1] == 0 else (0.0, ((1 - self.happiness / 2) - self.mil * 2) / 5)
        famine_range = (rebelion_range[1] + 0.001, rebelion_range[1] + max(0.001, round((1 - eco_per_capita) / 5)))
        r = round(random.random(), 2)
        if rebelion_range[0] <= r <= rebelion_range[1]:
            self.rebelions += 1
            return "Rebelia"
        elif famine_range[0] <= r <= famine_range[1]:
            population_loss = random.randint(int(self.population // 1000), int(self.population // 5 + 1))
            economy_loss = population_loss * (eco_per_capita / 2)
            self.population -= population_loss
            self.economy.agriculture -= economy_loss // 2
            self.economy.industry -= economy_loss // 4
            self.economy.services -= economy_loss // 4
            return f"Głód, stracono {population_loss} ludzi i {economy_loss} milionów w gospodarce"
        else:
            return False
        
    def calculate_control(self):
        result = 0.7
        result += ((4 - self.laws_active[2]) - 2) * 0.3
        result -= self.rebelions * 0.1
        result += self.mil
        result = min(result, 1.0)
        return result
    
    def update_stats(self):
        population_growth = 0.01
        birth_law_effect = [0.005, 0.0, -0.005, -0.01] #Wpływ prawa na wzrost populacji
        self.population += birth_law_effect[self.laws_active[0]]
        population_growth += random.uniform(-0.005, 0.005)
        self.population += int(self.population * population_growth)

        economy_growth = (0.01 + 0.01 * self.laws_active[3]) - self.mil / 15
        economy_growth += random.uniform(-0.005, 0.005)
        self.economy.grow(economy_growth)

        self.control = self.calculate_control()
        self.budget += (self.population // 10_000) * max(0, min(1, 1 - (1 - self.control) * 3))
        self.budget += self.economy.gdp // (250 - 50 * self.laws_active[3]) #Prywatne firmy zmniejszają wpływ gospodarki na budżet, ale zwiększają wzrost gospodarczy
        self.budget -= self.mil * self.population // 200

    def change_law(self, law_index, option_index):
        self.happiness += self.laws[law_index].effects[self.laws_active[law_index]] + self.laws[law_index].effects[option_index]
        self.laws_active[law_index] = option_index
        self.budget -= self.population // 100_000

    def attack_rebels(self):
        mil_loss = random.randint(0, 3) / 100
        self.mil = max(0.0, self.mil - mil_loss)
        self.population -= int(self.population * (mil_loss * 3))
        self.budget -= (mil_loss * self.population) // 100
        if self.rebelions > 0:
            success_chance = min(0.2, self.mil * 10)
            if random.random() < success_chance:
                self.rebelions -= 1
                return "Atak udany, rebelia stłumiona"
            else:
                self.happiness -= 0.02
                return "Atak nieudany"
        else:
            return "Nie masz rebelii"
        
    def agree_with_rebels(self):
        if self.rebelions > 0:
            self.rebelions -= 1
            population_loss = random.randint(self.population // 100, self.population // 5) #Część terenów się oddziela od państwa
            economy_loss = population_loss * ((self.economy.gdp / self.population) * random.uniform(0.7, 1.3)) #Mógł się oddzielić bogaty lub biedny teren
            return f"Zgodziłeś się na żądania rebeliantów, rebelia zakończona, oddzielony region ma {population_loss} ludzi i {economy_loss} milionów w gospodarce"
        else:
            return "Nie masz rebelii"

    def stats(self):
        print("\n\n")
        print("Populacja: ", self.population)
        print("PKB (w milionach): ", self.economy.gdp)
        print("PKB na osobę (w milionach): ", round(self.economy.gdp / self.population, 2))
        print("Populacja w wojsku i milicji: ", int(self.mil * 100), "%")
        print("Szczęście: ", int(self.happiness * 100), "%")
        print("Kontrola:", int(self.control*100), "%")
        print("Rebelie: ", self.rebelions)
        print("Skarbiec: ", self.budget)
     