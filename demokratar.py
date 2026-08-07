from games.demokratar.menu import Menu
from games.demokratar.democratic_country import DemocraticCountry

try:
    seed = int(input("Wpisz ziarno, lub zostaw puste, aby otrzymać losowe: "))
except ValueError:
    seed = None

try:
    elections_every = int(input("Co ile tur wybory? (domyślnie 20): "))
except ValueError:
    elections_every = 20

country = DemocraticCountry(seed, elections_every)
menu = Menu(country)

while country.in_power:
    menu.activate_option(menu.input())

print("\nKoniec gry — Twoja partia straciła władzę.")
