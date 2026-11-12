from datetime import datetime
from os import path
from objects import ChemInventory
import pandas as pd
from openpyxl import Workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont

class EHS_Annual_Chemical_Report:

    def __init__(self):

        now = datetime.now()

        self.time = now.strftime("%Y-%m-%d")

        self.name = "annual_chemical_report.xlsx"

        self.path = path.join("Reports", self.name)

        self.department = "Mechanical Engineering"

        self.PI = "Mathias Kolle"

        self.chemical_reporter = "Joshua Brandt"

        self.rooms = "5-012"

        self.chemicals = self.compile_chemicals()

        table_of_chemicals = self.generate_table()

        self.build_spreadsheet(table_of_chemicals)


    @staticmethod
    def compile_chemicals():

        inventory = ChemInventory.get_all_chemicals()

        chemical_worksheet = pd.read_excel("dhs_sara_worksheet.xlsx", skiprows = [0,1,2,3,4])

        reporting_names = chemical_worksheet["Chemical Name"].to_list()
        reporting_cas_numbers = chemical_worksheet["CAS Number"].to_list()

        chemicals = [chemical for chemical in inventory if chemical.name in reporting_names or chemical.cas in reporting_cas_numbers]

        return chemicals


    
    def generate_table(self):

        table = pd.DataFrame(columns = ["Chemical Name", "CAS Number", "Quan", "Unit", "Room #", "Changes"])

        for chemical in self.chemicals:

            row = [chemical.name, chemical.cas, chemical.size, chemical.unit, self.rooms, ""]

            table.loc[len(table)] = row

        return table

        
    def build_spreadsheet(self, table):

        bold = InlineFont(b = True)
        regular = InlineFont(b = False)

        with pd.ExcelWriter(self.path, engine = "openpyxl") as writer:

            table.to_excel(writer, sheet_name = "Sheet1", startrow = 5, index = False)

            ws = writer.sheets["Sheet1"]

            ws["A1"] = CellRichText([TextBlock(bold, "Department: "), TextBlock(regular, self.department)])
            ws["A2"] = CellRichText([TextBlock(bold, "PI/Supervisor: "), TextBlock(regular, self.PI)])
            ws["A3"] = CellRichText([TextBlock(bold, "Chemical Reporter: "), TextBlock(regular, self.chemical_reporter)])
            ws["A4"] = CellRichText([TextBlock(bold, "Rooms: "), TextBlock(regular, self.rooms)])
            ws["A5"] = CellRichText([TextBlock(bold, "Submission Date: "), TextBlock(regular, self.time)])


new_report = EHS_Annual_Chemical_Report()