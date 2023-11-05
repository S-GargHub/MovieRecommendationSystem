//Delete all
MATCH (n)
DETACH DELETE n

//Delete node
MATCH (n:Person)
DETACH DELETE n

//Delete relationship
MATCH (u:User)-[r:Rated]->()
DELETE r