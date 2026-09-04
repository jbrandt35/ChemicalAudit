from pandas import read_json
from requests import post 
import CAMEO

api_access_info = read_json("api_access_data.json", typ = "series")

access_token = api_access_info["api_token"]

inventory_id = api_access_info["inventory_id"]

api_url = "https://app.cheminventory.net/api"


def read_PHS_GHS_codes():
    with open("PHS_GHS_Codes.txt", "r") as file:
        return file.read().splitlines()

def read_flammable_GHS_codes():
        with open("Flammable_GHS_Codes.txt", "r") as file:
            return file.read().splitlines()



class Chemical:

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.detailed_data = ChemInventory.get_detailed_data(self)

        self.populate_attributes()

    def __str__(self):

        return self.name
    

    def set_tag_attribute(self, chem_inventory_tag_id, attribute_name):

        try:
            chem_inventory_tags = self.detailed_data[f"cf-{chem_inventory_tag_id}"]
            designations = chem_inventory_tags.strip("|").split("|")
        except KeyError:
            designations = []

        setattr(self, attribute_name, designations)


    def populate_attributes(self):

        my_GHS_codes = []

        GHS_data = self.detailed_data["ghs"]

        for source in GHS_data:

            hazard_statements = source["hazardstatements"].split("|")

            for GHS_code in hazard_statements:

                if GHS_code not in my_GHS_codes and GHS_code != "None":

                    my_GHS_codes.append(GHS_code)

        self.GHS_codes = my_GHS_codes

        self.set_tag_attribute(11399, "special_hazards")

        self.set_tag_attribute(11411, "reactive_groups")

        self.update_description()


    def update_special_hazard_class(self, hazard):

        if hazard not in self.special_hazards:

            self.special_hazards.append(hazard)

            payload = {
                "containerid": self.id,
                "field": "cf-11399",
                "newvalue": ChemInventory.format_tags(self.special_hazards)
                }

            ChemInventory.post_to_api(payload, "/container/information/save")


    def update_description(self):

        description = CAMEO.get_description(self)

        payload = {
                "containerid": self.id,
                "field": "cf-11415",
                "newvalue": description
                }

        ChemInventory.post_to_api(payload, "/container/information/save")



    def is_in_reactive_category(self, list_of_hazards):

        return any(i in list_of_hazards for i in self.reactive_groups)

    
    def update_reactive_groups(self):

        chemical_reactive_groups = CAMEO.get_reactive_groups(self)

        chem_inventory_needs_an_update = False

        flammable_GHS_codes = read_flammable_GHS_codes()

        if any(GHS_code in flammable_GHS_codes for GHS_code in self.GHS_codes):

            chemical_reactive_groups.append("Flammable")

        for reactive_group in chemical_reactive_groups:

            if reactive_group not in self.reactive_groups:

                self.reactive_groups.append(reactive_group)

                chem_inventory_needs_an_update = True


        if chem_inventory_needs_an_update:

            payload = {
                "containerid": self.id,
                "field": "cf-11411",
                "newvalue": ChemInventory.format_tags(self.reactive_groups)
                }

            ChemInventory.post_to_api(payload, "/container/information/save")



class ChemInventory:

    @staticmethod
    def get_all_chemicals():

        payload = {
            "inventory": inventory_id,
            "type": "name",               
            "contents": "%"     
        }

        response = ChemInventory.post_to_api(payload, "/search/execute")

        chemicals = response["data"]["containers"]

        chemical_objects = []

        for chemical in chemicals:

            chemical_object = Chemical(**chemical)

            chemical_objects.append(chemical_object)

        return chemical_objects
    

    @staticmethod
    def parse_location(location, location_data):

        if location["parent"] == 0:
            return location["name"]
        else:
            parent_location = next((loc for loc in location_data if loc.get("id") == location["parent"]), None)
            return ChemInventory.parse_location(parent_location, location_data) + " > " + location["name"]


    @staticmethod
    def locationid_to_locationname():

        response = ChemInventory.post_to_api(dict(), "/location/load")

        map = dict()

        for location in response["data"]:

            location_has_children = next((loc for loc in response["data"] if loc.get("parent") == location["id"]), False)

            if not location_has_children:

                map[location["id"]] = ChemInventory.parse_location(location, response["data"])

        return map


    @staticmethod
    def get_detailed_data(chemical):
        
        payload = {"containerid": chemical.id}

        response = ChemInventory.post_to_api(payload, "/container/information/load")
        
        data = response["data"]

        return data

    @staticmethod
    def format_tags(list_of_tags):
        return "|" + "|".join(list_of_tags) + "|"

    @staticmethod
    def post_to_api(payload, endpoint):

        api_destination = api_url + endpoint

        payload["authtoken"] = access_token

        return post(api_destination, json = payload).json()