//Create movie-actor
LOAD CSV WITH HEADERS FROM "http://localhost:11001/project-97461daa-f436-4a1d-944a-8a9161c626f4/movie_actor.csv" as line
MATCH (m:Movie) WHERE m.id = toInteger(line.m_id)
MATCH (a:Talent) WHERE a.id = toInteger(line.a_id)
CREATE (a)-[:ACTED_IN]->(m)

//Create movie-director
LOAD CSV WITH HEADERS FROM "http://localhost:11001/project-97461daa-f436-4a1d-944a-8a9161c626f4/movie_director.csv" as line
MATCH (m:Movie) WHERE m.id = toInteger(line.m_id)
MATCH (g:Talent) WHERE g.id = toInteger(line.p_id)
CREATE (g)-[:DIRECTED]->(m)

//Create movie-genre
LOAD CSV WITH HEADERS FROM "http://localhost:11001/project-97461daa-f436-4a1d-944a-8a9161c626f4/movie_genres.csv" as line
MATCH (m:Movie) WHERE m.id = toInteger(line.m_id)
MATCH (g:Genre) WHERE g.id = toInteger(line.g_id)
CREATE (m)-[:HAS_GENRE]->(g)

//Create user-movie
LOAD CSV WITH HEADERS FROM "http://localhost:11001/project-97461daa-f436-4a1d-944a-8a9161c626f4/user_movie.csv" as line
MATCH (u:User) WHERE u.id = toInteger(line.u_id)
MATCH (m:Movie) WHERE m.id = toInteger(line.m_id)
CREATE (u)-[:RATED {rating: toFloat(line.rating)}]->(m)