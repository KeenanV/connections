import json

from neo4j import GraphDatabase, Driver, Transaction


def test_connection():
    uri = 'bolt://localhost:7687'
    db_driver = GraphDatabase.driver(uri, auth=("neo4j", "dltbgyd!"))

    # create_person_and_company(db_driver, "Yatharth", "Codified")
    # find_people_by_company(db_driver, "Codified")

    # add_first_deg_connections_from_json(db_driver, "1st-deg-conns/11.json")
    add_second_deg_connections_from_json(db_driver, '2nd-deg-conns/consolidated_clean2.json')

    db_driver.close()


def add_first_deg_connections_from_json(db_driver: Driver, json_path):
    with db_driver.session() as session:
        with open(json_path, 'r') as ff:
            ii = 1
            for line in ff.readlines():
                print(f'User {ii}')
                ii += 1
                usr = json.loads(line)
                if 'works_at' in usr and 'worked_at' in usr:
                    session.execute_write(_add_connection_tx, usr['usr'], usr['name'], '1st',
                                          usr['works_at'],
                                          usr['worked_at'],
                                          None)
                elif 'works_at' in usr:
                    session.execute_write(_add_connection_tx, usr['usr'], usr['name'], '1st', usr['works_at'], None,
                                          None)
                elif 'worked_at' in usr:
                    session.execute_write(_add_connection_tx, usr['usr'], usr['name'], '1st', None, usr['worked_at'],
                                          None)
                else:
                    session.execute_write(_add_connection_tx, usr['usr'], usr['name'], '1st', None, None, None)


def add_second_deg_connections_from_json(db_driver: Driver, json_path):
    with db_driver.session() as session:
        with open(json_path, 'r') as ff:
            ii = 1
            for line in ff.readlines():
                print(f'User {ii}')
                ii += 1
                usr = json.loads(line)
                if 'name' not in usr:
                    continue
                if 'works_at' in usr and 'worked_at' in usr:
                    session.execute_write(_add_connection_tx, usr['usr'], usr['name'], '2nd',
                                          usr['works_at'],
                                          usr['worked_at'],
                                          usr['first_deg'])
                elif 'works_at' in usr:
                    session.execute_write(_add_connection_tx, usr['usr'], usr['name'], '2nd', usr['works_at'], None,
                                          usr['first_deg'])
                elif 'worked_at' in usr:
                    session.execute_write(_add_connection_tx, usr['usr'], usr['name'], '2nd', None, usr['worked_at'],
                                          usr['first_deg'])
                else:
                    session.execute_write(_add_connection_tx, usr['usr'], usr['name'], '2nd', None, None,
                                          usr['first_deg'])


def _add_connection_tx(tx, uid, name, deg, present: list[str] | None, past: list[str] | None,
                       connections: list[str] | None):
    if deg == '1st':
        node_type = 'First'
    else:
        node_type = 'Second'

    query = f"MERGE (p:{node_type} {{uid: $uid, name: $name}})"
    tx.run(query, uid=uid, name=name, deg=deg)

    if present is not None:
        for company in present:
            query = (
                f"MATCH (p:{node_type} {{uid: $uid}})"
                "MERGE (c:Company {name: $company}) "
                "MERGE (p)-[r:WORKS_AT]->(c)"
            )
            tx.run(query, uid=uid, company=company)
    if past is not None:
        for company in past:
            query = (
                f"MATCH (p:{node_type} {{uid: $uid}})"
                "MERGE (c:Company {name: $company}) "
                "MERGE (p)-[r:WORKED_AT]->(c)"
            )
            tx.run(query, uid=uid, company=company)
    if connections is not None:
        for person in connections:
            query = (
                "MATCH (fc:First {uid: $first}) "
                "MATCH (sc:Second {uid: $second}) "
                "MERGE (fc)-[:CONNECTED]-(sc)"
            )
            tx.run(query, first=person, second=uid)


def create_person_and_company(db_driver: Driver, person_name, company_name):
    with db_driver.session() as session:
        session.execute_write(_create_person_and_company_tx, person_name, company_name)


def _create_person_and_company_tx(tx_id, person_name, company_name):
    query = (
        f"CREATE (p:Person {{name: '{person_name}'}}) "
        f"CREATE (c:Company {{name: '{company_name}'}}) "
        f"CREATE (p)-[:WORKS_AT]->(c)"
    )
    tx_id.run(query)


def find_people_by_company(db_driver: Driver, company_name):
    with db_driver.session() as session:
        result = session.execute_read(_find_people_by_company_tx, company_name)
        for person in result:
            print(person['personName'])


def _find_people_by_company_tx(tx_id, company_name):
    query = (
        f"MATCH (p:Person)-[:WORKS_AT]->(c:Company {{name: '{company_name}'}}) "
        f"RETURN p.name AS personName"
    )
    result = tx_id.run(query)
    return list(result)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test_connection()
