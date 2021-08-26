# database_functions.py

from configparser import ConfigParser
import psycopg2


def config(FILENAME='database.ini', SECTION='postgresql'):
    """ Create the connection parameters object """
    parser = ConfigParser()  # create a parser
    parser.read(FILENAME)  # read config file
    db = {}  # get section, default to postgresql

    if parser.has_section(SECTION):
        params = parser.items(SECTION)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {SECTION} not found in the {FILENAME} file')
    return db


def execute_sql(mode, sql_statement):
    """ Define either read or write mode and include the sql statement """
    conn = None

    try:
        params = config()  # read connection parameters
        conn = psycopg2.connect(**params)  # connect to the PostgreSQL server
        cur = conn.cursor()  # create a cursor

        # Create options for read or write mode.
        if mode == "read":
            cur.execute(sql_statement)
            result = cur.fetchall()
            return result
        elif mode == "write":
            cur.execute(sql_statement)
            conn.commit()
        else:
            print("Please define read or write mode")
        cur.close()  # Close the connection to the PostgreSQL server.

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


# SQL statements.

# Select a random IP from the database.
SELECT = """SELECT * FROM network_numbers WHERE (scanned_status = false) OFFSET floor(random() * 
(SELECT COUNT(1) FROM network_numbers)) LIMIT 1;"""

# Insert found open port to the database.
INSERT = """INSERT INTO ss_port_data (ip_address, port) VALUES ('{}', '{}');"""  # Add .format when called.

# Update the scanned IP range.
UPDATE = """UPDATE network_numbers SET scanned_status = true, completed_scans = completed_scans+1, WHERE network_number = '{}';"""  # Add .format when called.
