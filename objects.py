import pandas as pd
from requests import post 

api_access_info = pd.read_json("api_access_data.json", typ = "series")

access_token = api_access_info["api_token"]

inventory_id = api_access_info["inventory_id"]


class Chemical:

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.add_GHS_codes()

    def __str__(self):

        return self.name

    def add_GHS_codes(self):

        my_GHS_codes = []

        data = ChemInventory.get_GHS_data(self)

        for source in data:

            hazard_statements = source["hazardstatements"].split("|")

            for GHS_code in hazard_statements:

                if GHS_code not in my_GHS_codes and GHS_code != "None":

                    my_GHS_codes.append(GHS_code)

        self.GHS_codes = my_GHS_codes



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
    def get_GHS_data(chemical):
        
        payload = {"authtoken": access_token, "containerid": chemical.id}
        
        response = post("https://app.cheminventory.net/api/container/information/load", json = payload).json()
        
        ghs_data = response["data"]["ghs"]

        return ghs_data
        

def read_PHS_GHS_codes():
    with open("PHS_GHS_Codes.txt", "r") as file:
        return file.read().splitlines()





