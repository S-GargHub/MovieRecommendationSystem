// Create genre
LOAD CSV WITH HEADERS FROM "http://localhost:11001/project-97461daa-f436-4a1d-944a-8a9161c626f4/genre.csv" AS csvLine
CREATE (g:Genre {id: toInteger(csvLine[0]), name: csvLine[1]})

// Create movie
LOAD CSV WITH HEADERS FROM "http://localhost:11001/project-97461daa-f436-4a1d-944a-8a9161c626f4/movie.csv" AS csvLine
CREATE (m:Movie {id: toInteger(csvLine[0]), name: csvLine[1], year: toInteger(csvLine[2]), certificate: csvLine[3], rating: toFloat(csvLine[4])})

// Create talent
LOAD CSV WITH HEADERS FROM "http://localhost:11001/project-97461daa-f436-4a1d-944a-8a9161c626f4/talent.csv" AS csvLine
CREATE (t:Talent {id: toInteger(csvLine[0]), name: csvLine[1], role: csvLine[2]})

//Create users
LOAD CSV WITH HEADERS FROM "http://localhost:11001/project-97461daa-f436-4a1d-944a-8a9161c626f4/users.csv" AS csvLine
CREATE (u:User {id: toInteger(csvLine[0]), gender: csvLine[1], age_group: toInteger(csvLine[2])})