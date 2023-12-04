import re
import csv
from more_itertools import unique_everseen

# genres = dict()
# persons = dict()
# directors = dict()

# g_id = 1
# p_id = 1

# person_file = open('Nodes/talent.csv', mode='w', newline='')
# person_writer = csv.writer(person_file, delimiter=',')

# genre_file = open('Nodes/genre.csv', 'w', newline='')
# genre_writer = csv.writer(genre_file, delimiter=',')

input_file = open('Nodes/imdb_top_1000.csv','r')
input_reader = csv.reader(input_file, delimiter=',')    
next(input_reader)

movie_file = open('Nodes/movie.csv','w', newline='')
movie_writer = csv.writer(movie_file, delimiter=',')
movie_writer.writerow(["id","title","year","certificate","genre","director","stars","rating"])

# mg_file = open('Relationships/movie_genres.csv', mode='w', newline='')
# mg_writer = csv.writer(mg_file, delimiter=',')
# mg_writer.writerow(["m_id", "g_id"])

# md_file = open('Relationships/movie_director.csv', mode='w', newline='')
# md_writer = csv.writer(md_file, delimiter=',')
# md_writer.writerow(["m_id", "p_id"])

# ma_file = open('Relationships/movie_actor.csv', mode='w', newline='')
# ma_writer = csv.writer(ma_file, delimiter=',')
# ma_writer.writerow(["m_id", "a_id"])

user_file = open('Nodes/users.csv','w', newline='')
user_writer = csv.writer(user_file, delimiter=',')
user_writer.writerow(["id", "gender", "age_group"])

um_file = open('Relationships/user_movie.csv', mode='w', newline='')
um_writer = csv.writer(um_file, delimiter=',')
um_writer.writerow(["u_id", "m_id", "rating"])

for movie in input_reader:
    genre = movie[4].strip(' ').replace(" ", "")
    director = movie[6].strip()
    stars = movie[7].strip() +","+ movie[8].strip() +","+ movie[9].strip() +","+ movie[10].strip()
    movie_writer.writerow([movie[0], movie[1], movie[2], movie[3], genre, director, stars, movie[5]])

    # arrOfGenre = genre.split(",")
    # for i in range (0, len(arrOfGenre)):
    #     genre = arrOfGenre[i].strip(' ')
    #     if(genre in genres.values()):
    #         mg_writer.writerow([movie[0], list(genres.keys())[list(genres.values()).index(genre)]])
    #     else:
    #         genres[g_id] = genre
    #         genre_writer.writerow([g_id, genre])
    #         mg_writer.writerow([movie[0],g_id])
    #         g_id = g_id + 1

    
    # if (director not in directors.values()):
    #    directors[p_id] = director
    #    person_writer.writerow([p_id, director, "DIRECTOR"])
    #    md_writer.writerow([movie[0], p_id])
    #    p_id = p_id + 1
    # else:
    #    md_writer.writerow([movie[0], list(directors.keys())[list(directors.values()).index(director)]])

    # stars = movie[7:10]
    # for star in stars:
    #     person = star.strip()
    #     if(person not in persons.values()):
    #         persons[p_id] = person
    #         person_writer.writerow([p_id, person, "ACTOR"])
    #         ma_writer.writerow([movie[0], p_id])
    #         p_id = p_id + 1
    #     else:
    #          ma_writer.writerow([movie[0], list(persons.keys())[list(persons.values()).index(person)]])


# genre_file.close()
# person_file.close()
# mg_file.close()
# md_file.close()
movie_file.close()

datContent = [i.strip().split() for i in open("/Users/sakshi/Downloads/ml-1m 2/users.dat").readlines()]

for data in datContent:
    user_data = data[0].split("::")
    if int(user_data[0]) <= 1500:
        user_writer.writerow([user_data[0], user_data[1], user_data[2]])
    
um_map = dict()

datContent = [i.strip().split() for i in open("/Users/sakshi/Downloads/ml-1m 2/ratings.dat").readlines()]
for data in datContent:
    rating_data = data[0].split("::")
    if int(rating_data[0]) <= 1500:
        if(rating_data[0] not in um_map.keys()):
            um_map[rating_data[0]] = 0
        else:
            um_map[rating_data[0]] = int(um_map[rating_data[0]]) + 1
        if um_map[rating_data[0]] < 20 :
            movie_id = int(rating_data[1]) % 1000
            movie_rating = int(rating_data[2])*2
            um_writer.writerow(unique_everseen([rating_data[0], movie_id, movie_rating]))

movie_file.close()
um_file.close()

