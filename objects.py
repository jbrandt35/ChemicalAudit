import pandas as pd
from requests import post 

api_access_info = pd.read_json("api_access_data.json", typ = "series")

access_token = api_access_info["api_token"]

inventory_id = api_access_info["inventory_id"]


def read_PHS_GHS_codes():
    with open("PHS_GHS_Codes.txt", "r") as file:
        return file.read().splitlines()



class Chemical:

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.populate_attributes()

    def __str__(self):

        return self.name

    def populate_attributes(self):

        detailed_data = ChemInventory.get_detailed_data(self)

        my_GHS_codes = []

        GHS_data = detailed_data["ghs"]

        for source in GHS_data:

            hazard_statements = source["hazardstatements"].split("|")

            for GHS_code in hazard_statements:

                if GHS_code not in my_GHS_codes and GHS_code != "None":

                    my_GHS_codes.append(GHS_code)

        self.GHS_codes = my_GHS_codes

        try:
            designations = detailed_data["cf-11399"].strip("|").split("|")
            self.special_hazards = designations
        except KeyError:
            self.special_hazards = []


    def update_special_hazard_class(self, hazard):

        if hazard not in self.special_hazards:

            self.special_hazards.append(hazard)

            payload = {
                "authtoken": access_token,
                "containerid": self.id,
                "field": "cf-11399",
                "newvalue": "|" + "|".join(self.special_hazards) + "|"
                }

            post("https://app.cheminventory.net/api/container/information/save", json = payload)



class ChemInventory:

    @staticmethod
    def get_all_chemicals():

        api_url = "https://app.cheminventory.net/api/search/execute"

        payload = {
            "authtoken": access_token,
            "inventory": inventory_id,
            "type": "name",               
            "contents": "%"     
        }

        response = post(api_url, json = payload).json()

        chemicals = response["data"]["containers"]

        chemical_objects = []

        for chemical in chemicals:

            chemical_object = Chemical(**chemical)

            chemical_objects.append(chemical_object)

        return chemical_objects
    

    @staticmethod
    def get_detailed_data(chemical):
        
        payload = {"authtoken": access_token, "containerid": chemical.id}
        
        response = post("https://app.cheminventory.net/api/container/information/load", json = payload).json()
        
        data = response["data"]

        return data





