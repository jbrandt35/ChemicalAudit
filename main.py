from objects import *
import CAMEO
import report
import json
import copy

peroxide_formers = []
PHS = []

locations = dict()
location_mapping = ChemInventory.locationid_to_locationname()

output_file = report.New_Report()

PHS_GHS_codes = read_PHS_GHS_codes()

with open("incompatible_groups.txt", "r") as f:
    incompatability_settings = json.load(f)


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

        for group in incompatability_settings:

            categories = group.keys()

            location_lookup = dict(zip(categories, []))

            for category in categories:

                chemicals_in_category = []

                for chemical in chemical_list:

                    if chemical.is_in_reactive_category(group[category]):
                        chemicals_in_category.append(chemical)
                    
                location_lookup[category] = copy.deepcopy(chemicals_in_category)

            if sum(len(i) > 0 for i in location_lookup.values()) >= 2:

                subsection_title = f"Incompatibilities in {location_mapping[location_id]}: {' and '.join(categories)}"

                output_file.add_subsection(subsection_title)

                for (category, lst) in location_lookup.items():

                     output_file.add_list(f"{category}s:", lst)



print("Importing Inventory...")

all_chemicals = ChemInventory.get_all_chemicals()

# Check for peroxide formers and PHS

print("Checking for peroxide formers and PHS...")

for chemical in all_chemicals:

    check_for_particularly_hazardous_substance(chemical)

    check_for_peroxide_former(chemical)

    chemical.update_reactive_groups()

    if chemical.location in locations:
        locations[chemical.location].append(chemical)
    else:
        locations[chemical.location] = [chemical]

output_file.add_list("Peroxide Formers", peroxide_formers)

output_file.add_list("Particularly Hazardous Substances", PHS)

print("Checking location compatabilities...")
output_file.add_section("Location Incompatibility")

check_location_compatibilities()

print("Compiling Report...")

output_file.publish()
