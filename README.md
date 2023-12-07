# MovieRecommendationSystem using Graph Database - Neo4j

In this project, we built a graph-based real-time movie recommender system using cypher, the query language of Neo4j through python. We generate two kind of recommendations -
1. Content-based recommendations: Based on the user's interactions with the system
2. Collabarative recommendations: Based on the preferences of users that have similar taste as the target user

## Installation
1. Install [Neo4j Desktop] (utm_source=google&utm_medium=PaidSearch&utm_campaign=GDB&utm_content=AMS-X-Conversion-GDB-Text&utm_term=download%20neo4j&gad_source=1&gclid=CjwKCAiA1MCrBhAoEiwAC2d64ep3pvrgaw5wkY_X3WxAYCFbxUnwn3Mj_DX-RXIlC6flzDbWThY0YhoCSqcQAvD_BwE)
2. Install [VSCode] (https://code.visualstudio.com/download)
3. Install python3


## How to run the code
1. Clone the github repository
2. Create a local project in Neo4j Desktop with user "neo4j" and start it.
3. Execute main.py in the src folder
    a. The code must be able to connect to the local project as the authentication has been disabled in the code. To enable it, please add the password.
    b. The script has 3 options:
        1. DB Creation - This function deletes the existing database (nodes and relationships) if present, and create a new database.
        2. DB Deletion - This function deletes the exisiting database.
        3. Movie Recommendations - This function asks for the target UserID and the type of recommendation you want to generate (Content-based or Collabarative) for that user. This function runs the same query twice (with and without indexing) and measures the improvement in execution time.
    c. To get recommendations, queries are present in CypherScripts/Queries.cypher
    d. To get a better visualization, try to run the queries using Newo4j Dekstop.


#Data schema
After proper data population within the graph database there should be visible following schema:






