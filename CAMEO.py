import sqlite3 as sql
import pandas as pd

def is_peroxide_former(chemical):

    with sql.connect("cameo.sqlite") as database:

        cursor = database.cursor()

        clean_cas = chemical.cas.replace("-", "").strip()

        sql_query = """
        SELECT chemicals.special_hazards
        FROM chemical_cas
        JOIN chemicals ON chemical_cas.chem_id = chemicals.id
        WHERE chemical_cas.cas_nodash = ?
        LIMIT 1
        """

        cursor.execute(sql_query, (clean_cas,))

        result = cursor.fetchall()

        try:
            return "Peroxidizable Compound" in result[0][0]
        except (TypeError, IndexError):
            return False
