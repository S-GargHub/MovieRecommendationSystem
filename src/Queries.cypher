//Users who rated or tagged this movie:

MATCH (m:Movie {title: "Inception"})-[:RATED]-(u)
RETURN m, u LIMIT 25

//Movies targeted user likes, then find users who also liked that movies, and recommend movies that other users liked but which our user haven’t seen (rated), sorted by the number of “paths” that led to a particular recommendation. 

MATCH (u:User{id:'10'})-[r1:RATED]->(m:Movie)<-[r2:RATED]-(other:User)-[r3:RATED]->(m2:Movie)
WHERE r1.rating > '3.0' AND r2.rating > '3.0' AND r3.rating > '3.0' AND NOT (u)-[:RATED]->(m2)
RETURN distinct m2 AS recommended_movie, count(*) AS score
ORDER BY score DESC
LIMIT 15

MATCH (u:User{id:'10'})-[r:RATED]-(m)
WITH u, avg(toFloat(r.rating)) AS average
MATCH (u)-[r1:RATED]->(m:Movie)<-[r2:RATED]-(other:User)-[r3:RATED]->(m2:Movie)
WHERE r1.rating > toString(average) AND r2.rating > toString(average) AND r3.rating > toString(average) AND NOT (u)-[:RATED]->(m2)
RETURN distinct average, m2, other, u, m AS recommended_movie, count(m2) AS score
ORDER BY score DESC
LIMIT 20

/Actors on movies which our user liked sorted by the number of time particular actor appears in such movies: 
MATCH (me:User{id:'350'})-[r:RATED]-(m:Movie)
WITH me, avg(toFloat(r.rating)) AS average
MATCH (me)-[r:RATED]->(m:Movie)-[:ACTED_IN]-(p:Talent)
WHERE r.rating > toString(average)
RETURN  p as actor, me, r, m, COUNT(*) AS score 
ORDER BY score DESC LIMIT 10



