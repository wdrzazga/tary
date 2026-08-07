from games.demokratar.democratic_country import DemocraticCountry


class Menu:
    def __init__(self, country: DemocraticCountry):
        self.country = country
        self.menu = 'main'
        self.actions = 0
        self.menus = {
            "main": ('Zarządzaj prawem', 'Zobacz statystyki', 'Kampania wyborcza', 'Wydawanie budżetu', 'Zakończ turę'),
            "laws": ('Podatki', 'Wolność słowa', 'Wydatki socjalne', 'Regulacja rynku', 'Wróć'),
            "campaign": ('Wiec wyborczy', 'Kampania reklamowa', 'Wróć'),
            "spend": ('Zainwestuj w gospodarkę', 'Program socjalny', 'Wróć'),
        }

    def input(self):
        print()
        options = self.menus[self.menu]
        for i in range(len(options)):
            print(f"{i + 1}. {options[i]}")
        return self.read_option("Wybierz opcję: ", len(options))

    def read_option(self, prompt, max_option):
        while True:
            try:
                choice = int(input(prompt))
            except ValueError:
                print("Niepoprawna opcja, wpisz liczbę.")
                continue
            if 1 <= choice <= max_option:
                return choice
            print(f"Niepoprawna opcja, wybierz od 1 do {max_option}.")

    def read_amount(self, prompt):
        try:
            return int(input(prompt))
        except ValueError:
            print("Niepoprawna kwota, wpisz liczbę.")
            return None

    def activate_option(self, option):
        if self.menu == 'main':
            print(f"Akcje wykonane w turze: {self.actions}/2")
            if option == 1:
                self.menu = 'laws'
            elif option == 2:
                self.country.stats()
            elif option == 3:
                self.menu = 'campaign'
            elif option == 4:
                self.menu = 'spend'
            elif option == 5:
                for message in self.country.end_turn():
                    print(message)
                self.actions = 0
        elif self.menu == 'campaign':
            print(f"Poparcie partii: {int(self.country.party_support * 100)}%")
            if option == 1:
                print(self.country.hold_rally())
            elif option == 2:
                print(self.country.ad_campaign())
            elif option == 3:
                self.menu = 'main'
        elif self.menu == 'laws':
            print("Obecne prawa:", ', '.join(str(x) for x in self.country.laws_active))
            print(f"Twoje miejsca w parlamencie: {int(self.country.seats * 100)}%")
            if option == len(self.menus['laws']):
                self.menu = 'main'
            else:
                law = list(self.country.laws.values())[option - 1]
                for i in range(len(law.options)):
                    print(f"{i + 1}. {law.options[i]} {law.descriptions[i]}")
                new_law_option = self.read_option("Wybierz opcję do zmiany prawa: ", len(law.options))
                print(self.country.propose_law(option - 1, new_law_option - 1))
        elif self.menu == 'spend':
            if option == 1:
                amount = self.read_amount("\nPodaj ilość pieniędzy do zainwestowania: ")
                if amount is not None:
                    self.country.invest(amount)
            elif option == 2:
                amount = self.read_amount("\nPodaj budżet programu socjalnego: ")
                if amount is not None:
                    self.country.social_program(amount)
            elif option == 3:
                self.menu = 'main'
