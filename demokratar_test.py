from games.demokratar.menu import Menu
from games.demokratar.democratic_country import DemocraticCountry

country = DemocraticCountry()
menu = Menu(country)

country.stats()
print('\n\n\n\n\n')

for i in range(100):
    menu.activate_option(menu.input())

country.stats()
