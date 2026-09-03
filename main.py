from objects import *
import CAMEO
import report

peroxide_formers = []
PHS = []

locations = dict()
location_mapping = ChemInventory.locationid_to_locationname()

output_file = report.New_Report()

PHS_GHS_codes = read_PHS_GHS_codes()


def check_for_peroxide_former(chemical):

    if CAMEO.is_peroxide_former(chemical):
    
            peroxide_formers.append(chemical)
    
            chemical.update_special_hazard_class("Peroxide Former")

def check_for_particularly_hazardous_substance(chemical):

     if any(GHS_code in chemical.GHS_codes for GHS_code in PHS_GHS_codes):
         
             PHS.append(chemical)
     
             chemical.update_special_hazard_class("Particularly Hazardous Substance")


def check_location_compatibilities():

     for location_id, chemical_list in locations.items():

        acids = []
        bases = []

        for chemical in chemical_list:

             # Change to be marked as Base or Acid during creation, same with oxidizer, flammable, etc

             chemical_is_acid = any("Acids," in reactive_group for reactive_group in chemical.reactive_groups)
             chemical_is_base = any("Base" in reactive_group for reactive_group in chemical.reactive_groups)

             if chemical_is_acid:
                  acids.append(chemical)

             if chemical_is_base:
                  bases.append(chemical)

        if len(acids) > 0 and len(bases) > 0:

            print(f"{location_mapping[location_id]} has both acids and bases.")

            print("Acids: " + "\n")
            for acid in acids:
                  print(str(acid) + "\n")

            print("Bases: " + "\n")
            for base in bases:
                  print(str(base) + "\n")

        else:

             print(f"No location incompatibilities found in {location_mapping[location_id]}")


print("Importing Inventory...")

all_chemicals = ChemInventory.get_all_chemicals()

# Check for peroxide formers and PHS

print("Checking for peroxide formers and PHS...")

for chemical in all_chemicals:

    chemical.update_reactive_groups()

    check_for_particularly_hazardous_substance(chemical)

    check_for_peroxide_former(chemical)

    if chemical.location in locations:
        locations[chemical.location].append(chemical)
    else:
        locations[chemical.location] = [chemical]

output_file.add_list_to_report("Peroxide Formers", peroxide_formers)

output_file.add_list_to_report("Particularly Hazardous Substances", PHS)

print("Checking location compatabilities...")

check_location_compatibilities()

print("Compiling Report...")

output_file.publish_report()
