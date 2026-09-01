import objects
import CAMEO

# Check for peroxide formers

print("Checking for peroxide formers...")

inventory = objects.ChemInventory()

all_chemicals = inventory.get_all_chemicals()

for chemical in all_chemicals:

    if chemical.cas != "N/A":

        if CAMEO.is_peroxide_former(chemical):

            print(f"{chemical} is a peroxide former!")

