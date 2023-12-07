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
        
        flag = True
        while flag :
            val = input("Enter 1 for DB creation, 2 for Db deletion and 3 for movie recommnedations\n") 
            if val=='1':
                # Create nodes and relationships
                driver.create_database()
            elif val=='2':
                # Delete nodes and relationships
                driver.delete_database()
            elif val=='3':
                # Get Recommendations
                driver.get_recommendation()
            f= input("Press Y/y to continue else any key to abort\n")
            if f=='Y' or f=='y':
                flag=True
            else :
                flag=False

    finally:
        # Close the connection when done
        driver.close()

if __name__ == "__main__":
    main()



