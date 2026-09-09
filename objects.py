from pandas import read_json
from requests import post 
import CAMEO
import os


try:
    api_access_info = read_json("api_access_data.json", typ = "series")
    access_token = api_access_info["api_token"]
    inventory_id = api_access_info["inventory_id"]
except FileNotFoundError:
    access_token = os.environ.get("API_key")
    inventory_id = os.environ.get("inventory_id")


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

        # Get existing data from ChemInventory and populate class attributes

        self.detailed_data = ChemInventory.get_detailed_data(self)

        self.populate_attributes()

        self.update_description()

    def __str__(self):

        return self.name
    

    def set_tag_attribute(self, chem_inventory_tag_id, attribute_name):

        try:
            chem_inventory_tags = self.detailed_data[f"cf-{chem_inventory_tag_id}"]
            designations = set(chem_inventory_tags.strip("|").split("|"))
        except KeyError:
            designations = set()

        setattr(self, attribute_name, designations)


    def populate_attributes(self):

        my_GHS_codes = set()

        GHS_data = self.detailed_data["ghs"]

        for source in GHS_data:

            hazard_statements = source["hazardstatements"].split("|")

            my_GHS_codes.update([GHS_code for GHS_code in hazard_statements if GHS_code != "None"])

        self.GHS_codes = set(my_GHS_codes)

        self.set_tag_attribute(11399, "special_hazards")

        self.set_tag_attribute(11411, "reactive_groups")


    def update_special_hazard_class(self, hazard):

        self.special_hazards.add(hazard)

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

        chemical_reactive_groups = set(CAMEO.get_reactive_groups(self))

        flammable_GHS_codes = read_flammable_GHS_codes()

        if any(GHS_code in flammable_GHS_codes for GHS_code in self.GHS_codes):

            chemical_reactive_groups.add("Flammable")

        self.reactive_groups.update(chemical_reactive_groups)

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