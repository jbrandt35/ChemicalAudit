from objects import *
import CAMEO
import report

output_file = report.New_Report()

PHS_GHS_codes = read_PHS_GHS_codes()

print("Importing Inventory...")

all_chemicals = ChemInventory.get_all_chemicals()

# Check for peroxide formers and PHS

print("Checking for peroxide formers and PHS...")

peroxide_formers = []
PHS = []

for chemical in all_chemicals:

    chemical.update_reactive_groups()

    if CAMEO.is_peroxide_former(chemical):

        peroxide_formers.append(chemical)

        chemical.update_special_hazard_class("Peroxide Former")

    if any(GHS_code in chemical.GHS_codes for GHS_code in PHS_GHS_codes):
    
        PHS.append(chemical)

        chemical.update_special_hazard_class("Particularly Hazardous Substance")


output_file.add_list_to_report("Peroxide Formers", peroxide_formers)

output_file.add_list_to_report("Particularly Hazardous Substances", PHS)

print("Compiling Report...")

output_file.publish_report()
