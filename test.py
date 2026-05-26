from games.komunistar.menu import Menu
from games.komunistar.communist_country import CommunistCountry

ussr = CommunistCountry()
menu = Menu(ussr)

ussr.stats()
print('\n\n\n\n\n')

for i in range(100):
    menu.activate_option(5) #tura

ussr.stats()

