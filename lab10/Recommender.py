import csv
import math

"""implements a recommender system built from
   a movie list name
   a listing of userid+movieid+rating"""

class Recommender(object):
    #"""initializes a recommender from a movie file and a ratings file"""
    def __init__(self,movie_filename,rating_filename):
        # read movie file and create dictionary _movie_names
        self._movie_names = {}
        f = open(movie_filename,"r",encoding="utf8")
        reader = csv.reader(f)
        next(reader)  # skips header line
        for line in reader:
            movieid = line[0]
            moviename = line[1]
            # ignore line[2], genre
            self._movie_names[movieid] = moviename
        f.close()

        # read rating file and create _movie_ratings (ratings for a movie)
        # and _user_ratings (ratings by a user) dicts
        self._movie_ratings = {}
        self._user_ratings = {}
        f = open(rating_filename,"r",encoding="utf8")
        reader = csv.reader(f)
        next(reader)  # skips header line
        for line in reader:
            userid = line[0]
            movieid = line[1]
            rating = line[2]
            # ignore line[3], timestamp
            if userid in self._user_ratings:
                self._user_ratings[userid].append((movieid,float(rating)))
            else:
                self._user_ratings[userid] = [(movieid,float(rating))]

            if movieid in self._movie_ratings:
                self._movie_ratings[movieid].append((userid,float(rating)))
            else:
                self._movie_ratings[movieid] = [(userid,float(rating))]
        f.close()

    """returns a list of pairs (userid,rating) of users that
       have rated movie movieid"""
    def get_movie_ratings(self,movieid):
        if movieid in self._movie_ratings:
            return self._movie_ratings[movieid]
        return None

    """returns a list of pairs (movieid,rating) of movies
       rated by user userid"""
    def get_user_ratings(self,userid):
        if userid in self._user_ratings:
            return self._user_ratings[userid]
        return None

    """returns the list of user id's in the dataset"""
    def userid_list(self):
        return self._user_ratings.keys()

    """returns the list of movie id's in the dataset"""
    def movieid_list(self):
        return self._movie_ratings.keys()

    """returns the name of movie with id movieid"""
    def movie_name(self,movieid):
        if movieid in self._movie_names:
            return self._movie_names[movieid]
        return None

    """returns the similarity between two lists of movie or user ratings"""
    def sim(self,a,b):
        average_a = sum([rating for (id,rating) in a])/len(a)
        average_b = sum([rating for (id,rating) in b])/len(b)
        dot_a_b = 0
        dot_a_a = 0
        dot_b_b = 0
        a_dict = dict(a)
        b_dict = dict(b)
        evaluated_items = 0
        for item in a_dict:
            if item in b_dict:
                evaluated_items += 1
                dot_a_b += (a_dict[item]-average_a)*(b_dict[item]-average_b)
                dot_a_a += (a_dict[item] - average_a)**2
                dot_b_b += (b_dict[item] - average_b)**2
        '''
        We check that there are enough elements in commont in order to evaluate
        the similarity
        '''
        if dot_a_b == 0 or (evaluated_items < min(len(a),3)): return 0
        else: return dot_a_b/(math.sqrt(dot_a_a)*math.sqrt(dot_b_b))

    '''
    input:
        similar_ratings: dict key = user_name -> value = similarity with our user
        ratings_dict: function to extract rating lists from
        ratings: previous ratings to compare with
    '''
    def pred(self,similar_ratings,ratings_dict,ratings):
        num  = 0
        den = 0
        #print(len(similar_ratings),self.movie_name(film),len(self.get_movie_ratings(film))) #be careful with this
        for item in similar_ratings:
            if item in ratings:
                average_b = sum([rating for (id,rating) in ratings_dict(item)])/len(ratings_dict(item))
                num += similar_ratings[item] *(ratings[item] - average_b)
                den += similar_ratings[item]
        return num/den


    """input: -similar_ratings -> dict of pairs (rating_list,similarity with user_ratings)
              -user_ratings -> ratings of the user we want to recommend a film to
       output: list of predictions of ratings of new films for the given user"""
    def pred_list(self,similar_ratings,user_ratings):
        predictions = []
        average_user =  sum([rating for (id,rating) in user_ratings])/len(user_ratings)
        user_ratings_dict = dict(user_ratings)
        # Mirar solo las peliculas de usuarios con similaridad alta.
        similar_user_movies = set([item[0] for user in similar_ratings for item in self._user_ratings[user]])
        for film in similar_user_movies:
            if film not in user_ratings_dict:
                predictions.append((film,average_user+self.pred(similar_ratings,self.get_user_ratings,dict(self.get_movie_ratings(film)))))
        return predictions

    """input:
              -target_list -> list of pairs (movie/user,rate)
              -ratings_dict -> self.get_user_ratings or self.get_movie_ratings
                              (depending on the type of target_list)
              -possible_similar -> same format as ratings_dict
              -threshold -> we consider that two lists are similar if their
                           similarity is greater that threshold
       output:
              similar_ratings -> dictionary with:
                  -keys: movie/user (depending on the type of target_list)
                  -values: similarity between the ratings_dict[key] and target_list"""
    def get_similar_ratings(self,target_list,ratings_dict,possible_similar,threshold):
        similar_ratings = {}
        for key in possible_similar:
            if key in ratings_dict:
                similarity = self.sim(target_list,ratings_dict[key])
                if similarity > threshold:
                    similar_ratings[key] = similarity
        return similar_ratings


    """returns a list of at most k pairs (movieid,predicted_rating)
       adequate for a user whose rating list is rating_list"""
    def recommend_user_to_user(self,rating_list,k,threshold):
        #Get only the lists of ratings that are similar to the ones
        '''
        key = user similar to ours -> sim_user
        value = sim(rating_list, sim_user)
        '''
        similar_ratings = self.get_similar_ratings(rating_list,self._user_ratings,self._user_ratings,threshold)
        total_predictions = self.pred_list(similar_ratings,rating_list)
        return sorted(total_predictions,key = lambda t: -t[1])[:k]

    """returns a list of at most k pairs (movieid,predicted_rating)
       adequate for a user whose rating list is rating_list"""
    def recommend_item_to_item(self,rating_list,k,threshold):
        rating_dict = dict(rating_list)
        total_predictions = []
        for movie in self._movie_ratings:
            if movie not in rating_dict:
                average_item =  sum([rating for (id,rating) in self.get_movie_ratings(movie)])/len(self.get_movie_ratings(movie))
                #Get only the lists of ratings that are similar to the ones
                similar_ratings = self.get_similar_ratings(self.get_movie_ratings(movie),self._movie_ratings,rating_dict,threshold)
                #Hacer predicción para la película movie en el usuario en base a las películas similares con movie
                if(len(similar_ratings) > 0):
                    prediccion_movie = average_item + self.pred(similar_ratings,self.get_movie_ratings,rating_dict)
                    total_predictions.append((movie,prediccion_movie))
        return sorted(total_predictions,key = lambda t: -t[1])[:k]


def main():

    r = Recommender("./ml-latest-small/movies.csv","./ml-latest-small/ratings.csv")

    U = len(r._user_ratings)
    M = len(r._movie_ratings)
    LR = sum(len(rating_list) for user,rating_list in r._user_ratings.items())/U
    LC = sum(len(rating_list) for movie,rating_list in r._movie_ratings.items())/M
    print("U = ",U)
    print("M = ",M)
    print("LR = ", LR)
    print("LC = ", LC)

    a = r.get_user_ratings("1")
#--------------------------------------------------------
    print("Recommended films with user-to-user")
    for i,(film,rate) in enumerate(r.recommend_user_to_user(a,10,0.3)):
        print(i+1,". ",r.movie_name(film), " [",rate,"]",sep ='')
    print("----------------------------------------------")
#--------------------------------------------------------
    print("Recommended films with item-to-item")
    for i,(film,rate) in enumerate(r.recommend_item_to_item(a,10,0.3)):
        print(i+1,". ",r.movie_name(film), " [",rate,"]",sep ='')
#main()
