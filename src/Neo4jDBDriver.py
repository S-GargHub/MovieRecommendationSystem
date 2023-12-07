from neo4j import GraphDatabase
from tqdm import tqdm
import RecommendationGenerator 
import pandas as pd

movie_dataset = pd.read_csv("data/movie.csv")
user_dataset = pd.read_csv("data/users.csv")
rating_dataset = pd.read_csv("data/user_movie.csv")

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
    
def create_nodes(tx, label1, label2=None, label3=None, r1=None, r2=None, r3=None, properties=None):
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
                cypher_query += f"{key}: k}}) MERGE (m)-[:{r1}]->(g)"
        cypher_query += ") "
        for key, value in properties.items():
            if key == 'director':
                cypher_query += f"MERGE (d:{label3} {{"
                cypher_query += f"name: '{value}', "
                cypher_query += f"role: '{key}'}}) MERGE (d)-[:{r2}]->(m)"
        for key, value in properties.items():
            if key == 'stars':
                cypher_query += f" FOREACH (k in split('{value}', ',') | MERGE (a:{label3} {{"
                cypher_query += f"name: k , "
                cypher_query += f"role: 'actor'}}) MERGE (a)-[:{r3}]->(m)"
        cypher_query += ")"
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

    def create_table(self, session, dataset, label1, label2=None, label3 = None, r1=None, r2=None, r3=None):
        print("Creating",  label1, label2, label3,  "and corresponding relationships...")
        for row in dataset.to_dict(orient='records'):
            session.execute_write(create_nodes, label1, label2, label3, r1, r2, r3, row)
        
    def create_user(self, session, dataset, label):
        print("Creating",  label, "...")
        for row in dataset.to_dict(orient='records'):
            session.execute_write(create_user_node, label, row)
    
    def create_relationships(self, session, dataset, label1, relationship, label2):
        print("Creating Relationships for", label1, "...")
        for row in dataset.to_dict(orient='records'):
            session.execute_write(create_relationship, label1, relationship, label2, row)
    
    def delete_index(self, index_name):
        self._driver.execute_query(
            "DROP INDEX "+index_name+" IF EXISTS"
        )
    
    def create_index(self, index_name, field, table=None):
        self.delete_index(index_name)

        if(table!=None):
            self._driver.execute_query(
                "CREATE INDEX "+index_name+" FOR (m:"+table+") ON (m."+field+")"
            )
        else:
            self._driver.execute_query(
                "CREATE INDEX "+index_name+" ON "+field+")"
            )

    def create_database(self):
        # Create a Session for the  database
        session = self._driver.session() #database="movie-recommendation"
        self.delete_database()
        self.create_table(session, movie_dataset, "Movie", "Genre", "Talent", "HAS_GENRE", "DIRECTED", "ACTED")
        self.create_user(session, user_dataset, "User")
        session.execute_write(delete_relationship, "User", "RATED")
        self.create_relationships(session, rating_dataset, "User", "RATED", "Movie")
    
    def delete_database(self):
        # Create a Session for the  database
        session = self._driver.session() #database="movie-recommendation"
        self.delete_table(session, "Movie")
        self.delete_table(session, "Genre")
        self.delete_table(session, "Talent")
        self.delete_table(session, "User")

    def get_recommendation(self):
        userID = input("Enter UserID\n")
        val = input("Which type of recommendation do you want? \n 1. Based on Movies you liked  \n 2. Based on other users' with similar taste\n")
        if val=='1':
            # Content based Recommendations
            RecommendationGenerator.get_cb_recommendations(self, userID)
        elif val=='2':
            # Collaborative Filtering based Recommendations
            RecommendationGenerator.get_cf_recommendations(self, userID)

