########################### DO NOT MODIFY THIS SECTION ##########################
#################################################################################
import sqlite3
from sqlite3 import Error, Connection
import csv
from typing import Any
#################################################################################

## Change to False to disable Sample
SHOW = False

############### SAMPLE CLASS AND SQL QUERY ###########################
######################################################################
class Sample():
    def sample(self):
        try:
            connection = sqlite3.connect("sample")
            connection.text_factory = str
        except Error as e:
            print("Error occurred: " + str(e))
        print('\033[32m' + "Sample: " + '\033[m')
        
        # Sample Drop table
        connection.execute("DROP TABLE IF EXISTS sample;")
        # Sample Create
        connection.execute("CREATE TABLE sample(id integer, name text);")
        # Sample Insert
        connection.execute("INSERT INTO sample VALUES (?,?)",("1","test_name"))
        connection.commit()
        # Sample Select
        cursor = connection.execute("SELECT * FROM sample;")
        print(cursor.fetchall())

######################################################################

############### DO NOT MODIFY THIS SECTION ###########################
######################################################################
def create_connection(path: str) -> Connection:
    connection = None
    try:
        connection = sqlite3.connect(path)
        connection.text_factory = str
    except Error as e:
        print("Error occurred: " + str(e))

    return connection


def execute_query(connection: Connection, query: str) -> str:
    cursor = connection.cursor()
    try:
        if query == "":
            return "Query Blank"
        else:
            cursor.execute(query)
            connection.commit()
            return "Query executed successfully"
    except Error as e:
        return "Error occurred: " + str(e)


def execute_query_and_get_result(connection: Connection, query: str) -> Any:
    cursor = connection.execute(query)
    return cursor.fetchall()
######################################################################
######################################################################


def GTusername() -> str:
    gt_username = "sghaderi6"
    return gt_username


def part_1_a_i() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        CREATE TABLE incidents (
            report_id TEXT,
            category TEXT,
            date TEXT
        );
    """
    ######################################################################
    return query


def part_1_a_ii() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        CREATE TABLE details (
            report_id TEXT,
            subject TEXT,
            transport_mode TEXT,
            detection TEXT
        );
    """
    ######################################################################
    return query


def part_1_a_iii() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        CREATE TABLE outcomes (
            report_id TEXT,
            outcome TEXT,
            num_ppl_fined INTEGER,
            fine REAL,
            num_ppl_arrested INTEGER,
            prison_time REAL,
            prison_time_unit TEXT
        );
    """
    ######################################################################
    return query


def part_1_b_i(connection: Connection, path: str) -> None:
    ############### CREATE IMPORT CODE BELOW ############################
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        for row in reader:
            connection.execute(
                "INSERT INTO incidents (report_id, category, date) VALUES (?, ?, ?);",
                (row[0], row[1], row[2])
            )
    connection.commit()
    ######################################################################


def part_1_b_ii(connection: Connection, path: str) -> None:
    ############### CREATE IMPORT CODE BELOW ############################
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        for row in reader:
            connection.execute(
                "INSERT INTO details (report_id, subject, transport_mode, detection) VALUES (?, ?, ?, ?);",
                (row[0], row[1], row[2], row[3])
            )
    connection.commit()
    ######################################################################


def part_1_b_iii(connection: Connection, path: str) -> None:
    ############### CREATE IMPORT CODE BELOW ############################
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        for row in reader:
            connection.execute(
                """INSERT INTO outcomes (report_id, outcome, num_ppl_fined, fine,
                                         num_ppl_arrested, prison_time, prison_time_unit)
                   VALUES (?, ?, ?, ?, ?, ?, ?);""",
                (row[0], row[1],
                 int(row[2]) if row[2] else None,
                 float(row[3]) if row[3] else None,
                 int(row[4]) if row[4] else None,
                 float(row[5]) if row[5] else None,
                 row[6])
            )
    connection.commit()
    ######################################################################


def part_2_a() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        CREATE INDEX incident_index ON incidents (report_id);
    """
    ######################################################################
    return query


def part_2_b() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        CREATE INDEX detail_index ON details (report_id);
    """
    ######################################################################
    return query


def part_2_c() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        CREATE INDEX outcome_index ON outcomes (report_id);
    """
    ######################################################################
    return query


def part_3() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        SELECT ROUND(100.0 * SUM(CASE WHEN date BETWEEN '2018-01-01' AND '2020-12-31'
                                     THEN 1 ELSE 0 END) / COUNT(*), 2)
        FROM incidents;
    """
    ######################################################################
    return query


def part_4() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        SELECT transport_mode, COUNT(*) AS count
        FROM details
        WHERE detection = 'Intelligence'
          AND transport_mode IS NOT NULL
          AND transport_mode != ''
        GROUP BY transport_mode
        ORDER BY count DESC
        LIMIT 3;
    """
    ######################################################################
    return query


def part_5() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        SELECT details.detection, COUNT(*) AS count,
               ROUND(AVG(outcomes.num_ppl_arrested), 2) AS avg_ppl_arrested
        FROM details
        INNER JOIN outcomes ON details.report_id = outcomes.report_id
        WHERE outcomes.num_ppl_arrested >= 1
        GROUP BY details.detection
        HAVING COUNT(*) >= 100
        ORDER BY avg_ppl_arrested DESC
        LIMIT 3;
    """
    ######################################################################
    return query


def part_6() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        SELECT incidents.category, COUNT(*) AS count,
               ROUND(AVG(CASE outcomes.prison_time_unit
                         WHEN 'Years'  THEN outcomes.prison_time * 365
                         WHEN 'Months' THEN outcomes.prison_time * 30
                         WHEN 'Weeks'  THEN outcomes.prison_time * 7
                         WHEN 'Days'   THEN outcomes.prison_time
                         ELSE 0 END), 2) AS avg_prison_time_days
        FROM incidents
        INNER JOIN outcomes ON incidents.report_id = outcomes.report_id
        GROUP BY incidents.category
        HAVING COUNT(*) > 50
        ORDER BY avg_prison_time_days DESC;
    """
    ######################################################################
    return query


def part_7_a() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        CREATE VIEW fines AS
        SELECT incidents.report_id, incidents.date, outcomes.num_ppl_fined, outcomes.fine
        FROM incidents
        INNER JOIN outcomes ON incidents.report_id = outcomes.report_id
        WHERE outcomes.num_ppl_fined >= 1;
    """
    ######################################################################
    return query


def part_7_b() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        SELECT substr(date, 1, 4) AS year,
               SUM(num_ppl_fined) AS total_ppl_fined,
               ROUND(SUM(fine), 2) AS total_fine_amount
        FROM fines
        GROUP BY year
        ORDER BY total_fine_amount DESC
        LIMIT 3;
    """
    ######################################################################
    return query


def part_8_a() -> str:
    ############### EDIT SQL STATEMENT ###################################
    query = """
        CREATE VIRTUAL TABLE incident_overviews USING fts5(report_id, subject);
    """
    ######################################################################
    return query


def part_8_b() -> str:
    ############### EDIT SQL STATEMENT ############################
    query = """
        INSERT INTO incident_overviews (report_id, subject)
        SELECT report_id, subject FROM details;
    """
    ######################################################################
    return query

    
def part_8_c():
    ############### EDIT SQL STATEMENT ###################################
    query = """
        SELECT COUNT(*)
        FROM incident_overviews
        WHERE incident_overviews MATCH 'NEAR("dead" "pangolin", 2)';
    """
    ######################################################################
    return query


if __name__ == "__main__":
    
    ########################### DO NOT MODIFY THIS SECTION ##########################
    #################################################################################
    if SHOW:
        sample = Sample()
        sample.sample()

    print('\033[32m' + "Q2 Output: " + '\033[m')
    try:
        conn = create_connection("Q2")
    except Exception as e:
        print("Database Creation Error:", e)

    try:
        conn.execute("DROP TABLE IF EXISTS incidents;")
        conn.execute("DROP TABLE IF EXISTS details;")
        conn.execute("DROP TABLE IF EXISTS outcomes;")
        conn.execute("DROP VIEW IF EXISTS fines;")
        conn.execute("DROP TABLE IF EXISTS incident_overviews;")
    except Exception as e:
        print("Error in Table Drops:", e)

    try:
        print('\033[32m' + "part 1.a.i: " + '\033[m' + execute_query(conn, part_1_a_i()))
        print('\033[32m' + "part 1.a.ii: " + '\033[m' + execute_query(conn, part_1_a_ii()))
        print('\033[32m' + "part 1.a.iii: " + '\033[m' + execute_query(conn, part_1_a_iii()))
    except Exception as e:
         print("Error in part 1.a:", e)

    try:
        part_1_b_i(conn,"data/incidents.csv")
        print('\033[32m' + "Row count for Incidents Table: " + '\033[m' + str(execute_query_and_get_result(conn, "select count(*) from incidents")[0][0]))
        part_1_b_ii(conn, "data/details.csv")
        print('\033[32m' + "Row count for Details Table: " + '\033[m' + str(execute_query_and_get_result(conn,"select count(*) from details")[0][0]))
        part_1_b_iii(conn, "data/outcomes.csv")
        print('\033[32m' + "Row count for Outcomes Table: " + '\033[m' + str(execute_query_and_get_result(conn,"select count(*) from outcomes")[0][0]))
    except Exception as e:
        print("Error in part 1.b:", e)

    try:
        print('\033[32m' + "part 2.a: " + '\033[m' + execute_query(conn, part_2_a()))
        print('\033[32m' + "part 2.b: " + '\033[m' + execute_query(conn, part_2_b()))
        print('\033[32m' + "part 2.c: " + '\033[m' + execute_query(conn, part_2_c()))
    except Exception as e:
        print("Error in part 2:", e)

    try:
        print('\033[32m' + "part 3: " + '\033[m' + str(execute_query_and_get_result(conn, part_3())[0][0]))
    except Exception as e:
        print("Error in part 3:", e)

    try:
        print('\033[32m' + "part 4: " + '\033[m')
        for line in execute_query_and_get_result(conn, part_4()):
            print(line[0],line[1])
    except Exception as e:
        print("Error in part 4:", e)

    try:
        print('\033[32m' + "part 5: " + '\033[m')
        for line in execute_query_and_get_result(conn, part_5()):
            print(line[0],line[1],line[2])
    except Exception as e:
        print("Error in part 5:", e)

    try:
        print('\033[32m' + "part 6: " + '\033[m')
        for line in execute_query_and_get_result(conn, part_6()):
            print(line[0],line[1],line[2])
    except Exception as e:
        print("Error in part 6:", e)
    
    try:
        execute_query(conn, part_7_a())
        print('\033[32m' + "part 7.a: " + '\033[m' + str(execute_query_and_get_result(conn,"select count(*) from fines")[0][0]))
        print('\033[32m' + "part 7.b: " + '\033[m')
        for line in execute_query_and_get_result(conn, part_7_b()):
            print(line[0],line[1], line[2])
    except Exception as e:
        print("Error in part 7:", e)

    try:   
        print('\033[32m' + "part 8.a: " + '\033[m'+ execute_query(conn, part_8_a()))
        execute_query(conn, part_8_b())
        print('\033[32m' + "part 8.b: " + '\033[m' + str(execute_query_and_get_result(conn, "select count(*) from incident_overviews")[0][0]))
        print('\033[32m' + "part 8.c: " + '\033[m' + str(execute_query_and_get_result(conn, part_8_c())[0][0]))
    except Exception as e:
        print("Error in part 8:", e)

    conn.close()
    #################################################################################
    #################################################################################
  