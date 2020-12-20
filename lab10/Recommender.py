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
        f.close

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
        for item in a_dict:
            if item in b_dict:
                dot_a_b += (a_dict[item]-average_a)*(b_dict[item]-average_b)
                dot_a_a += (a_dict[item] - average_a)**2
                dot_b_b += (b_dict[item] - average_b)**2
        if dot_a_b == 0: return 0
        else: return dot_a_b/(math.sqrt(dot_a_a)*math.sqrt(dot_b_b))

    '''
    input:
        similar_ratings: dict user_name -> similarity with our user
        film:
    '''
    def pred(self,similar_ratings,film,ratings_dict,*args):
        '''
        with this if we check in which case we are:
            no extra arg -> user to user recommendation
            extra arg -> item to item recommendation
        '''
        if not len(args):
            ratings = dict(self.get_movie_ratings(film))
        else:
            ratings = args[0]
        num  = 0
        den = 0
        #print(len(similar_ratings),self.movie_name(film),len(self.get_movie_ratings(film))) #be careful with this
        for item in similar_ratings:
            if item in ratings:
                average_b = sum([rating for (id,rating) in ratings_dict(item)])/len(ratings_dict(item))
                num += similar_ratings[item] *(ratings[item] - average_b)
                den += similar_ratings[item]
        return num/den

    """input: similar_ratings -> dict of pairs (rating_list,similarity with user_ratings)
              user_ratings -> ratings of the user we want to recommend a film to
       output: list of predictions of ratings of new films for the given user"""
    def pred_list(self,similar_ratings,user_ratings):
        predictions = []
        average_user =  sum([rating for (id,rating) in user_ratings])/len(user_ratings)
        user_ratings_dict = dict(user_ratings)
        # Mirar solo las peliculas de usuarios con similaridad alta.
        prueba = set([item[0] for user in similar_ratings for item in self._user_ratings[user]])
        for film in prueba:
            if film not in user_ratings_dict: predictions.append((film,average_user+self.pred(similar_ratings,film,self.get_user_ratings)))
        return predictions

    """returns a list of at most k pairs (movieid,predicted_rating)
       adequate for a user whose rating list is rating_list"""
    def recommend_user_to_user(self,rating_list,k,threshold):
        #Get only the lists of ratings that are similar to the ones
        '''
        key = user similar to ours -> sim_user
        value = sim(rating_list, sim_user)
        '''
        similar_ratings = {} # OPTIMIZAR LO DE HACER LA COPIA
        for user in self._user_ratings:
            similarity = self.sim(self._user_ratings[user],rating_list)
            if similarity > threshold:
                similar_ratings[user] = similarity
        total_predictions = self.pred_list(similar_ratings,rating_list)
        return sorted(total_predictions,key = lambda t: -t[1])[:k]

    """returns a list of at most k pairs (movieid,predicted_rating)
       adequate for a user whose rating list is rating_list"""
    def recommend_item_to_item(self,rating_list,k,threshold):
        #print(len(self._user_ratings),len(self._movie_ratings),len(rating_list))
        '''
        User/Peli 1 2 3
                A 5 N 2
                B 4 1 4
                C 5 0 2

        Explotar correlación de las columnas
        '''
        rating_dict = dict(rating_list)
        average_user =  sum([rating for (id,rating) in rating_list])/len(rating_list)
        total_predictions = []
        for movie in self._movie_ratings:
            if movie not in rating_dict:
                '''
                key = similar movie to "movie" -> seen_movie_i
                value = sim(movie,seen_movie_i)
                '''
                #Get only the lists of ratings that are similar to the ones
                similar_ratings = {}
                for seen_movie in rating_dict:
                    similarity = self.sim(self._movie_ratings[movie],self._movie_ratings[seen_movie])
                    if similarity > threshold:
                        similar_ratings[seen_movie] = similarity
                #Hacer predicción para la película movie en el usuario en base a las películas similares con movie
                if(len(similar_ratings) > 0):
                    prediccion_movie = average_user + self.pred(similar_ratings,movie,self.get_movie_ratings,rating_dict)
                    total_predictions.append((movie,prediccion_movie))
        return sorted(total_predictions,key = lambda t: -t[1])[:k]


def main():
    r = Recommender("./ml-latest-small/movies.csv","./ml-latest-small/ratings.csv")
    '''
    print(len(r.movieid_list())," movies with ratings from ",len(r.userid_list()),"different users")
    print("The name of movie 1 is: ",r.movie_name("1"))
    print("movie 1 was recommended by ",r.get_movie_ratings("1"))
    print("user 1 recommended movies ",r.get_user_ratings("1"))
    '''
    #print(r.movie_name("1"),r.movie_name("1"))
    #print(r.get_movie_ratings("1"),r.get_movie_ratings("2"))
    a = r.get_user_ratings("1")
    print("Previously seen films:")
    for (film,rate) in a:
        print(r.movie_name(film),rate)
    #b = r.get_movie_ratings("1")
    #print(a)
    #print(r.sim(a,b))
    print("\n")
#--------------------------------------------------------
    print("Recommended films with user-to-user")
    for (film,rate) in r.recommend_user_to_user(a,5,0.3):
        print(r.movie_name(film),rate)
    print("\n")
#--------------------------------------------------------
    print("Recommended films with item-to-item")
    for (film,rate) in r.recommend_item_to_item(a,20,0.3):
        print(r.movie_name(film),rate)
main()
