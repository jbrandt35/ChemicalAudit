import sqlite3 as sql

def search_database(query, input):

     with sql.connect("cameo.sqlite") as database:
    
            cursor = database.cursor()
    
            cursor.execute(query, (input,))
    
            result = cursor.fetchall()

            cursor.close()
    
            return result


def is_peroxide_former(chemical):

    if chemical.cas == "None":
        return False

    sql_query = """
    SELECT chemicals.special_hazards
    FROM chemical_cas
    JOIN chemicals ON chemical_cas.chem_id = chemicals.id
    WHERE chemical_cas.cas_id = ?
    LIMIT 1
    """

    result = search_database(sql_query, chemical.cas)

    try:
        return "Peroxidizable Compound" in result[0][0]
    except (TypeError, IndexError):
        return False


def get_reactive_groups(chemical):

    if chemical.cas == "None":
        return ["Insufficient Information for Classification"]

    sql_query = """
    SELECT r.name
    FROM chemical_cas cc
    JOIN chemicals c 
        ON cc.chem_id = c.id
    JOIN mm_chemical_react mcr 
        ON c.id = mcr.chem_id
    JOIN reacts r 
        ON mcr.react_id = r.id
    WHERE cc.cas_id = ?;
    """

    result = search_database(sql_query, chemical.cas)
    
    reactive_groups = [row[0] for row in result]

    return reactive_groups