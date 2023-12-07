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
WHERE toFloat(r.rating) > average
RETURN  p as actor, me, r, m, COUNT(*) AS score 
ORDER BY score DESC LIMIT 10


//Find movies of users that he has rated more than his avg rating an having the same genre as as user's liked genre
MATCH (u:User {id: '14'})-[r:RATED]->(m:Movie)
WITH u, avg(toFloat(r.rating)) AS mean
MATCH (u)-[r:RATED]->(m:Movie)
       -[:HAS_GENRE]->(g:Genre)
WHERE toFloat(r.rating) > mean
WITH u, g, COUNT(*) AS score
MATCH (g)<-[:HAS_GENRE]-(rec:Movie)
WHERE NOT EXISTS { (u)-[:RATED]->(rec) }
RETURN rec.title AS recommendation, rec.year AS year,
       sum(score) AS sscore,
       collect(DISTINCT g.genre) AS genres
ORDER BY sscore DESC LIMIT 100


//Recommend movies similar to those the user has already watched(based on genre)
MATCH (u:User {id: '14'})-[r:RATED]->(m:Movie),
      (m)-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(rec:Movie)
WHERE NOT EXISTS{ (u)-[:RATED]->(rec) }
WITH rec, g.genre as genre, count(*) AS count
WITH rec, collect([genre, count]) AS scoreComponents
RETURN rec.title AS recommendation, rec.year AS year, scoreComponents,
       reduce(s=0,x in scoreComponents | s+x[1]) AS score
ORDER BY score DESC LIMIT 10


//Compute a weighted sum based on the number and types of overlapping traits. Let’s use a weighted sum to score the recommendations based on the number of actors (3x), genres (5x) and directors (4x) they have in common to boost the score

MATCH (u:User {id: '14'})-[r:RATED]->(m:Movie),
 (m)-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(rec:Movie)
WHERE NOT EXISTS{ (u)-[:RATED]->(rec) }
WITH m, rec, count(*) AS gs
OPTIONAL MATCH (m)<-[:ACTED_IN]-(a)-[:ACTED_IN]->(rec)
WITH m, rec, gs, count(a) AS as
OPTIONAL MATCH (m)<-[:DIRECTED]-(d)-[:DIRECTED]->(rec)
WITH m, rec, gs, as, count(d) AS ds
RETURN rec.title AS recommendation,
       (5*gs)+(3*as)+(4*ds) AS score
ORDER BY score DESC LIMIT 25


//We can calculate the Jaccard index for sets of movie genres to determine how similar two movies are.
MATCH (u:User {id: '14'})-[r:RATED]->(m:Movie),
(m)-[:HAS_GENRE]->
      (g:Genre)<-[:HAS_GENRE]-(other:Movie)
       WHERE NOT EXISTS{ (u)-[:RATED]->(other) }
WITH m, other, count(g) AS intersection, collect(g.genre) as common
WITH m,other, intersection, common,
     [(m)-[:HAS_GENRE]->(mg) | mg.genre] AS set1,
     [(other)-[:HAS_GENRE]->(og) | og.genre] AS set2
WITH m,other,intersection, common, set1, set2,
     set1+[x IN set2 WHERE NOT x IN set1] AS union
RETURN m.title, other.title, common, set1,set2,
       ((1.0*intersection)/size(union)) AS jaccard
ORDER BY jaccard DESC
 LIMIT 25

//looking at movies being rated similarly, and then picking highly rated movies and using their rating and frequency to sort the results.
MATCH (u:User {id: '14'})-[r1:RATED]->
      (:Movie)<-[r2:RATED]-(peer:User)
WHERE abs(toFloat(r1.rating)-toFloat(r2.rating)) < 1 // similarly rated
WITH distinct u, peer
MATCH (peer)-[r3:RATED]->(rec:Movie)
WHERE toFloat(r3.rating) > 6
  AND NOT EXISTS { (u)-[:RATED]->(rec) }
WITH rec, count(*) as freq, avg(toFloat(r3.rating)) as rating
RETURN rec.title, rec.year, rating, freq
ORDER BY rating DESC, freq DESC
LIMIT 25
