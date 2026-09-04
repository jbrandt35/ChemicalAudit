from datetime import datetime
from os import path

class New_Report:

    def __init__(self):

        now = datetime.now()

        formatted_time = now.strftime("%Y-%m-%d-%H:%M:%S")

        self.name = "report_" + formatted_time + ".txt"

        self.path = path.join("Reports", self.name)

        self.content = ""

    def add_list(self, title, item_list):

        self.content += "*" * 5 + " " + title + " " + "*" * 5 + "\n"

        for item in item_list:

            self.content += str(item) + "\n"

    def add_section(self, title):

        self.content += "*" * 5 + " " + title + " " + "*" * 5 + "\n"

    def add_subsection(self, title):

        self.content += "-" * 5 + " " + title + " " + "-" * 5 + "\n"


    def publish(self):
        with open(self.path, "w") as file:
            file.write(self.content)





    