import csv
import math
import Recommender as recom
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

'''
Reads a csv with the following header: userId,movieId,rating,timestamp
and partitions it into training and test by taking "percentage" different userId's
for training and the rest for test
'''
def partition_by_user(path,percentage):
    df = pd.read_csv(path,sep=',')
    users = df['userId'].unique()
    '''
    Fractions the data set in two groups, assigning
    'percentage' of users to training and the rest to test.
    '''
    msk = np.random.rand(len(users)) < percentage

    train = df[df['userId'].isin(users[msk])]

    test = df[~df['userId'].isin(users[msk])]

    train.to_csv("./ml-latest-small/ratings_train.csv",index = False)

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
    count = 0
    residuals = []
    predicted = []
    for k,user in enumerate(user_ratings_test):
        if type == "user-to-user":
            similar_ratings = recommender.get_similar_ratings(user_ratings_test[user],recommender._user_ratings,recommender._user_ratings,threshold)
            similar_user_movies = set([item[0] for user in similar_ratings for item in recommender._user_ratings[user]])
        for i,(movie,rate) in enumerate(user_ratings_test[user]):
            aux_user = user_ratings_test[user]
            aux_user.pop(i)
            if type == "item-to-item":
                aux_movie = recommender.get_movie_ratings(movie)
                if aux_movie is None: continue
                for j, user_aux in enumerate(aux_movie):
                    if user_aux == user: aux_movie.pop(j)

            if type == "user-to-user":
                avg_aux = sum([r for (_,r) in aux_user])/len(aux_user)
                pred = avg_aux
                if len(similar_ratings) > 0 and movie in similar_user_movies:
                    pred += recommender.pred(similar_ratings,recommender.get_user_ratings,dict(recommender.get_movie_ratings(movie)))
                else: continue

            elif type == "item-to-item":
                similar_ratings = recommender.get_similar_ratings(aux_movie,recommender._movie_ratings,dict(aux_user),threshold)
                avg_aux = sum([r for (_,r) in aux_movie])/len(aux_movie)
                pred = avg_aux
                if(len(similar_ratings) > 0):
                    pred += recommender.pred(similar_ratings,recommender.get_movie_ratings,dict(aux_user))
                else: continue
            error += abs(rate-pred)
            residuals.append(rate-pred)
            predicted.append(pred)
            count +=1
        #print(k)
    return error/count, count, residuals, predicted

def main():
    np.random.seed(1234)
    partition_by_user("./ml-latest-small/ratings.csv",0.9)
    r = recom.Recommender("./ml-latest-small/movies.csv","./ml-latest-small/ratings_train.csv")
    error_user, num_pred_films_user,res_user, pred_user = evaluate_test(r,"user-to-user","./ml-latest-small/ratings_test.csv",0.9)
    print(error_user,num_pred_films_user)
    error_item, num_pred_films_item,res_item, pred_item = evaluate_test(r,"item-to-item","./ml-latest-small/ratings_test.csv",0.9)
    print(error_item, num_pred_films_item)
    print(np.mean(res_user),np.var(res_user))
    print(np.mean(res_item),np.var(res_item))
main()
