from loguru import logger
from Neo4jDBDriver import Neo4jDBDriver
    
uri = "bolt://localhost:7687"  # or your Neo4j server URI
user = "neo4j" #disabled auth
password = "your_password"

def main():
    logger.info("Get Driver to GraphDB")
    driver = Neo4jDBDriver(uri, user, password)

    try:
        # Connect to the Neo4j server
        driver.connect()

        # Create nodes and relationships
        driver.create_database()

    finally:
        # Close the connection when done
        driver.close()

if __name__ == "__main__":
    main()



