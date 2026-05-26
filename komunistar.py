from games.komunistar.menu import Menu
from games.komunistar.communist_country import CommunistCountry
import random

try:
    seed = int(input("Wpisz ziarno, lub zostaw puste, aby otrzymać losowe: "))
except ValueError:
    seed = None

country = CommunistCountry(seed)
menu = Menu(country)

while True: #While True jest fajne
    menu.activate_option(menu.input())