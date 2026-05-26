from games.komunistar.communist_country import CommunistCountry
import random

class Menu:
    menus = {
        "main": ['Zarządzaj prawem', 'Zobacz statystyki', 'Zarządzaj rebeliami', 'Używanie pieniędzy', 'Zakończ turę'],
        "rebels": ['Zaatakuj rebeliantów', 'Zgódź się na warunki rebeliantów', 'Wróć'],
        "laws": ['Prawo dzietności', 'Wolność słowa', 'Poziom federalizacji', 'Prywatne firmy', 'Wróć'],
        "spend": ['Zainwestuj w gospodarkę', 'Rekrutuj milicję i wojsko', 'Wróć']
    }

    def __init__(self, country: CommunistCountry):
        self.country = country
        self.menu = 'main'
        self.actions = 0

    def input(self):
        print()
        for i in range(len(Menu.menus[self.menu])):
            print(f"{i+1}. {Menu.menus[self.menu][i]}")
        return int(input("Wybierz opcję: "))
    
    def activate_option(self, option):
        if self.menu == "main":
            print(f"Akcje wykonane w turze: {str(self.actions)}/2")
            if option == 1:
                self.menu = 'laws'
            elif option == 2:
                self.country.stats()
            elif option == 3:
                self.menu = 'rebels'
            elif option == 4:
                self.menu = 'spend'
            elif option == 5:
                self.country.update_stats()
                print(self.country.random_event())
                self.actions = 0
        elif self.menu == 'rebels':
            print(f"Rebelie: {self.country.rebels}\n'")
            if option == 1:
                print(self.country.attack_rebels())
            elif option == 2:
                print(self.country.agree_with_rebels())
            elif option == 3:
                self.menu = 'main'
        elif self.menu == 'laws':
            print("Obecne prawa:", ', '.join([str(x) for x in self.country.laws_active]))
            if option == len(Menu.menus['laws']):
                self.menu = 'main'
            else:
                law = list(self.country.laws.values())[option-1]
                for i in range(len(law.options)):
                    print(f"{str(i+1)}. {law.options[i]} {law.descriptions[i]}'")
                new_law_option = int(input("Wybierz opcję do zmieny prawa: "))
                self.country.laws_active[option-1] = new_law_option - 1
        elif self.menu == 'spend':
            if option == 1:
                amount = int(input("\nPodaj ilość pieniędzy do zainwestowania: "))
                self.budget -= amount
                self.country.economy += round(random.uniform(-0.05, 0.3), 2) * 3 * amount
            elif option == 2:
                cost = self.country.population * 0.01 // 100
                if self.country.budget >= cost:
                    self.country.budget -= cost
                    self.country.mil += 0.01
                else:
                    print("Nie masz wystarczająco pieniędzy, koszt rekrutacji to", cost)
            elif option == 3:
                self.menu = 'main'