import pandas as pd
from requests import post 

class Chemical:

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):

        return self.name


class ChemInventory:

    def __init__(self):

        api_access_info = pd.read_json("api_access_data.json", typ = "series")

        self.access_token = api_access_info["api_token"]

        self.inventory_id = api_access_info["inventory_id"]

    

    def get_all_chemicals(self):

        api_url = "https://app.cheminventory.net/api/search/execute"

        payload = {
            "authtoken": self.access_token,
            "inventory": self.inventory_id,
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








