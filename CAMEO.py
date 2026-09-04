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
        SELECT special_hazards
        FROM chemicals
        WHERE id = (
            SELECT chem_id 
            FROM chemical_cas 
            WHERE cas_id = ? 
            GROUP BY chem_id 
            HAVING COUNT(cas_id) = 1 
            LIMIT 1
        );
        """

    result = search_database(sql_query, chemical.cas)

    try:
        return "Peroxidizable Compound" in result[0][0]
    except (TypeError, IndexError):
        return False


def get_reactive_groups(chemical):

    if chemical.cas == "N/A":
        return ["Insufficient Information for Classification"]

    sql_query = """
        SELECT c.name, r.name
        FROM chemicals c
        JOIN mm_chemical_react mcr ON c.id = mcr.chem_id
        JOIN reacts r ON mcr.react_id = r.id
        WHERE c.id = (
            SELECT chem_id 
            FROM chemical_cas 
            WHERE cas_id = ? 
            GROUP BY chem_id 
            HAVING COUNT(cas_id) = 1 
            LIMIT 1
        );
    """

    result = search_database(sql_query, chemical.cas)
    
    reactive_groups = [row[1] for row in result]

    return reactive_groups


def get_description(chemical):

    if chemical.cas == "N/A":
        return "None"

    sql_query = """
    SELECT description
    FROM chemicals
    WHERE id = (
        SELECT chem_id 
        FROM chemical_cas 
        WHERE cas_id = ? 
        GROUP BY chem_id 
        HAVING COUNT(cas_id) = 1 
        LIMIT 1
    );
    """

    result = search_database(sql_query, chemical.cas)

    try:
        description = result[0]
        return description
    except IndexError:
        return "None"
