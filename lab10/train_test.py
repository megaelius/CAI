import csv
import math
import Recommender as recom
import pandas as pd
import numpy as np

'''
Reads a csv with the following header: userId,movieId,rating,timestamp
and partitions it into training and test by taking "percentage" different userId's
for training and the rest for test
'''
def partition_by_user(path,percentage):
    df = pd.read_csv(path,sep=',')
    print(df.columns)
    users = df['userId'].unique()
    '''
    Fractions the data set in two groups, assigning
    'percentage' of users to training and the rest to test.
    '''
    msk = np.random.rand(len(users)) < percentage
    print(users[msk],len(users),len(users[msk]))

    train = df[df['userId'].isin(users[msk])]

    test = df[~df['userId'].isin(users[msk])]

    print(len(train),len(test))

    train.to_csv("./ml-latest-small/ratings_train",index = False)

    test.to_csv("./ml-latest-small/ratings_test.csv",index = False)

def read_test_data(test_path):
    # read rating file and create _movie_ratings (ratings for a movie)
    # and _user_ratings (ratings by a user) dicts
    movie_ratings_test = {}
    user_ratings_test = {}
    f = open(test_path,"r",encoding="utf8")
    reader = csv.reader(f)
    next(reader)  # skips header line
    for line in reader:
        userid = line[0]
        movieid = line[1]
        rating = line[2]
        # ignore line[3], timestamp
        if userid in user_ratings_test:
            user_ratings_test[userid].append((movieid,float(rating)))
        else:
            user_ratings_test[userid] = [(movieid,float(rating))]

        if movieid in movie_ratings_test:
            movie_ratings_test[movieid].append((userid,float(rating)))
        else:
            movie_ratings_test[movieid] = [(userid,float(rating))]
    f.close()
    return movie_ratings_test, user_ratings_test

def evaluate_test(recommender,type,test_path,threshold):
    movie_ratings_test, user_ratings_test = read_test_data(test_path)
    error = 0
    for user in user_ratings_test:
        for i,movie,rate in enumerate(user_ratings_test[user]):
            #predicción
            aux = user_ratings_test[user][0:i]
            avg_aux = sum([r for _,r in aux])/len(aux)
            pred = avg_aux
            similar_ratings = recommender.get_similar_ratings(aux,recommender._user_ratings,recommender._user_ratings,threshold)
            if len(similar_ratings > 0):
                pred += recommender.pred(similar_ratings,recommender.get_user_ratings,dict(recommender.get_movie_ratings(movie)))
            error += abs(rate-pred)
    return error

def main():
    partition_by_user("./ml-latest-small/ratings.csv",0.7)
    r = recom.Recommender("./ml-latest-small/movies.csv","./ml-latest-small/ratings_train.csv")
    print(evaluate_test(r,"user-to-user","./ml-latest-small/ratings.csv",0.3))
main()
