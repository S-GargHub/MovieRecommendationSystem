from neo4j import GraphDatabase
import pandas as pd
from tqdm import tqdm

movie_dataset = pd.read_csv("/Users/sakshi/Desktop/MovieRecommendationSystem/Nodes/movie.csv")
user_dataset = pd.read_csv("/Users/sakshi/Desktop/MovieRecommendationSystem/Nodes/users.csv")
rating_dataset = pd.read_csv("/Users/sakshi/Desktop/MovieRecommendationSystem/Relationships/user_movie.csv")

def delete_node(tx, label):
    # Remove all user nodes
    cypher_query = f"MATCH (n:{label}) DETACH DELETE n"
    return tx.run(cypher_query)

def delete_relationship(tx, label, relationship):
    # Remove all user relationship
    cypher_query = f"MATCH ()-[r:{relationship}]->() DELETE r"
    return tx.run(cypher_query)

def create_user_node(tx, label, properties=None):
    cypher_query = f"MERGE (n:{label} {{"
    if properties:
        for key, value in properties.items():
            cypher_query += f"{key}: '{value}', "
            cypher_query = cypher_query[:-1]
        cypher_query = cypher_query[:-1]
        cypher_query += "})"
    return tx.run(cypher_query)
    
def create_nodes(tx, label1, label2, relationship, properties=None):
    cypher_query = f"MERGE (m:{label1} {{"
    if properties:
        for key, value in properties.items():
            if key != 'genre' and key != 'director' and key != 'stars':
                cypher_query += f"{key}: '{value}', "
                cypher_query = cypher_query[:-1]
        cypher_query = cypher_query[:-1]
        cypher_query += "}) "
        for key, value in properties.items():
            if key == 'genre':
                cypher_query += f" FOREACH (k in split('{value}', ',') | MERGE (g:{label2} {{"
                cypher_query += f"{key}: k}}) MERGE (m)-[:{relationship}]->(g)"
        cypher_query += ") "
        for key, value in properties.items():
            if key == 'director':
                cypher_query += f"MERGE (d:{'Talent'} {{"
                cypher_query += f"name: '{value}', "
                cypher_query += f"role: '{key}'}}) MERGE (d)-[:{'DIRECTED'}]->(m)"
        for key, value in properties.items():
            if key == 'stars':
                cypher_query += f" FOREACH (k in split('{value}', ',') | MERGE (a:{'Talent'} {{"
                cypher_query += f"name: k , "
                cypher_query += f"role: 'actor'}}) MERGE (a)-[:{'ACTED_IN'}]->(m)"
        cypher_query += ")"
        #print(cypher_query)
    return tx.run(cypher_query)

def create_relationship(tx, label1, relationship, label2, properties):
    cypher_query = ""
    for key, value in properties.items():
        if key == 'u_id':
            cypher_query += f"MATCH (u:{label1} {{id: '{value}'}}) "
        elif key == 'm_id':
            cypher_query += f"MATCH (m:{label2} {{id: '{value}'}})"
        else:
            cypher_query += f"MERGE (u)-[:{relationship} {{{key}: '{value}'}}]->(m)"
    return tx.run(cypher_query)

class Neo4jDBDriver:
    def __init__(self, uri, user, password):
        self._uri = uri
        self._user = user
        self._password = password
        self._driver = None

    def connect(self):
        self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))

    def close(self):
        if self._driver is not None:
            self._driver.close()

	
    def delete_table(self, session, label):
        print("Deleting", label, "...")
        session.execute_write(delete_node, label)

    def create_table(self, session, dataset, label1, label2=None, relationship=None):
        print("Creating",  label1, label2, "...")
        for row in dataset.to_dict(orient='records'):
            session.execute_write(create_nodes, label1, label2, relationship, row)
        
    def create_tab(self, session, dataset, label):
        print("Creating",  label, "...")
        for row in dataset.to_dict(orient='records'):
            session.execute_write(create_user_node, label, row)
    
    def create_relationships(self, session, dataset, label1, relationship, label2):
        print("Creating Relationship")
        for row in dataset.to_dict(orient='records'):
            session.execute_write(create_relationship, label1, relationship, label2, row)

    def create_database(self):
        # Create a Session for the  database
        session = self._driver.session() #database="movie-recommendation"
        # self.delete_table(session, "Movie")
        # self.delete_table(session, "Genre")
        # self.delete_table(session, "Talent")
        # self.create_table(session, movie_dataset, "Movie", "Genre", "HAS_GENRE")

        # self.delete_table(session, "User")
        # self.create_tab(session, user_dataset, "User")
        records, summary, keys = self._driver.execute_query(
            "MATCH (m:Movie) WHERE m.year >= toInteger(2003) RETURN m"
        )
        print()
        print("The query '{query}' returned {records_count} records in {time} ms.".format(
            query=summary.query, records_count=len(records),
            time=summary.result_available_after,
        ))
        
        self._driver.execute_query(
            "DROP INDEX release_year_index IF EXISTS"
        )

        self._driver.execute_query(
            "CREATE INDEX release_year_index  FOR (m:Movie) ON (m.year)"
        )
        
        records, summary, keys = self._driver.execute_query(
            "MATCH (m:Movie) WHERE m.year >= toInteger(2003) RETURN m"
        )

        print("The query '{query}' returned {records_count} records in {time} ms.".format(
            query=summary.query, records_count=len(records),
            time=summary.result_available_after,
        ))

        # session.execute_write(delete_relationship, "User", "RATED")
        # self.create_relationships(session, rating_dataset, "User", "RATED", "Movie")
