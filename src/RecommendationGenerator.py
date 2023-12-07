
def get_cb_recommendations(neo4j, userID):

    match_user = "MATCH (u:User {id: \'"
    trait_query="""\'})-[r:RATED]->(m:Movie),
    (m)-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(rec:Movie)
    WHERE NOT EXISTS{ (u)-[:RATED]->(rec) }
    WITH m, rec, count(*) AS gs
    OPTIONAL MATCH (m)<-[:ACTED_IN]-(a)-[:ACTED_IN]->(rec)
    WITH m, rec, gs, count(a) AS as
    OPTIONAL MATCH (m)<-[:DIRECTED]-(d)-[:DIRECTED]->(rec)
    WITH m, rec, gs, as, count(d) AS ds
    RETURN rec.title AS recommendation,
    (5*gs)+(3*as)+(4*ds) AS score
    ORDER BY score DESC LIMIT 25"""

    jaccard_index_query="""\'})-[r:RATED]->(m:Movie),
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
    LIMIT 25"""
    
    print("Looking at movies based on the number and types of overlapping traits of movies watched by user...")
    records_1, summary_1, keys_1  = neo4j._driver.execute_query(
    match_user+userID+trait_query
    )
    print("The query 1 returned {records_count} records in {time} ms.".format(
        query=summary_1.query, records_count=len(records_1),
        time=summary_1.result_available_after,
    ))        
    
    records_2, summary_2, keys_2  = neo4j._driver.execute_query(
    match_user+userID+jaccard_index_query
    )
    
    print()
    print("Looking at movies based on the jaccard index...")
    print("The query 2 returned {records_count} records in {time} ms.".format(
        query=summary_2.query, records_count=len(records_2),
        time=summary_2.result_available_after,
    ))

    print("Creating Index....")
    # creating index on movieID
    neo4j.create_index("movie_id_index","id", "Movie")
    
    #Creating index on userID
    neo4j.create_index("user_id_index", "id", "User")
    
    #creating index on relationship RATED
    neo4j.create_index("rating_index","rating","RATED")

    # #creating index on relationship HAS_GENRE
    # driver.create_index("genre_index","HAS_GENRE")

    # #creating index on relationship ACTED_IN
    # driver.create_index("actor_index","ACTED_IN")

    # #creating index on relationship DIRECTED
    # driver.create_index("director_index","DIRECTED")


    print("Looking at movies based on the number and types of overlapping traits of movies watched by user...")
    records_1, summary_1, keys_1  = neo4j._driver.execute_query(
    match_user+userID+trait_query
    )

    print("The query 1 returned {records_count} records in {time} ms.".format(
        query=summary_1.query, records_count=len(records_1),
        time=summary_1.result_available_after,
    ))        
    
    records_2, summary_2, keys_2  = neo4j._driver.execute_query(
    match_user+userID+jaccard_index_query
    )
    
    print()
    print("Looking at movies based on the jaccard index...")
    print("The query 2 returned {records_count} records in {time} ms.".format(
        query=summary_2.query, records_count=len(records_2),
        time=summary_2.result_available_after,
    ))

    # Deleting Index
    neo4j.delete_index("movie_id_index")
    neo4j.delete_index("user_id_index")
    neo4j.delete_index("rating_index")

def get_cf_recommendations(neo4j, userID):
    driver = neo4j._driver
    match_user = "MATCH (u:User {id: \'"
    cf_query="""\'})-[r1:RATED]->(:Movie)<-[r2:RATED]-(peer:User)
    \nWHERE abs(toFloat(r1.rating)-toFloat(r2.rating)) < 1
    \nWITH distinct u, peer
    \nMATCH (peer)-[r3:RATED]->(rec:Movie)
    \nWHERE toFloat(r3.rating) > 6
    \nAND NOT EXISTS { (u)-[:RATED]->(rec) }
    \nWITH rec, count(*) as freq, avg(toFloat(r3.rating)) as rating
    \nRETURN rec.title, rec.year, rating, freq
    \nORDER BY rating DESC, freq DESC
    \nLIMIT 25"""

    knn_based_cf_query="""\'})-[r:RATED]->(m:Movie)
    \nWITH u, avg(toFloat(r.rating)) AS u_mean
    \nMATCH (u)-[r1:RATED]->(m:Movie)<-[r2:RATED]-(other)
    \nWITH u, u_mean, other, COLLECT({r1: r1, r2: r2}) AS ratings WHERE size(ratings) > 6
    \nMATCH (other)-[r:RATED]->(m:Movie)
    \nWITH u, u_mean, other, avg(toFloat(r.rating)) AS other_mean, ratings
    \nUNWIND ratings AS r
    \nWITH sum((toFloat(r.r1.rating)-u_mean) * (toFloat(r.r2.rating)-other_mean)) AS nom,
    \nsqrt( sum((toFloat(r.r1.rating) - u_mean)^2) * sum((toFloat(r.r2.rating) - other_mean) ^2)) AS denom,u, other WHERE denom <> 0
    \nWITH u, other, nom/denom AS pearson
    \nORDER BY pearson DESC LIMIT 10
    \nMATCH (other)-[r:RATED]->(m:Movie) WHERE NOT EXISTS( (u)-[:RATED]->(m) )
    \nRETURN m.title, SUM( pearson * toFloat(r.rating)) AS score
    \nORDER BY score DESC LIMIT 25"""
    
    print("Looking at movies being rated similarly, and then picking highly rated movies ...")
    records_1, summary_1, keys_1  = driver.execute_query(
    match_user+userID+cf_query
    )
    print("The query 1 returned {records_count} records in {time} ms.".format(
        query=summary_1.query, records_count=len(records_1),
        time=summary_1.result_available_after,
    ))

    
    print()
    print("Movies rated highly by 10 users with tastes in movies most similar to mine, that user hasn't seen yet ...")
    records_2, summary_2, keys_2  = driver.execute_query(
    match_user+userID+knn_based_cf_query
    )
    print("The query 2 returned {records_count} records in {time} ms.".format(
        query=summary_2.query, records_count=len(records_2),
        time=summary_2.result_available_after,
    ))

    print()
    print("Creating Index....")
    # creating index on movieID
    neo4j.create_index("movie_id_index","id", "Movie")
    
    #Creating index on userID
    neo4j.create_index("user_id_index", "id", "User")
    
    #creating index on relationship RATED
    neo4j.create_index("rating_index","rating","RATED")
    
    print("Looking at movies being rated similarly, and then picking highly rated movies ...")
    records_1, summary_1, keys_1  = driver.execute_query(
    match_user+userID+cf_query
    )
    print("The query 1 returned {records_count} records in {time} ms.".format(
        query=summary_1.query, records_count=len(records_1),
        time=summary_1.result_available_after,
    ))

    print()
    print("Movies rated highly by 10 users with tastes in movies most similar to mine, that user hasn't seen yet ...")
    records_2, summary_2, keys_2  = driver.execute_query(
    match_user+userID+knn_based_cf_query
    )
    print("The query 2 returned {records_count} records in {time} ms.".format(
        query=summary_2.query, records_count=len(records_2),
        time=summary_2.result_available_after,
    ))
