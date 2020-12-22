import Recommender as recommender

def main():
    r = recommender.Recommender("./ml-latest-small/movies.csv","./ml-latest-small/ratings.csv")
    '''
    Used for obtaining the statistics for the time complexity analysis.
    U = len(r._user_ratings)
    M = len(r._movie_ratings)
    LR = sum(len(rating_list) for user,rating_list in r._user_ratings.items())/U
    LC = sum(len(rating_list) for movie,rating_list in r._movie_ratings.items())/M
    print("U = ",U)
    print("M = ",M)
    print("LR = ", LR)
    print("LC = ", LC)
    '''


    user_input =[('109487',5),('65685',4),('72998',4.5),('40851',4),('39446',3.5),('79132',4),('73017',4),('60069',5),('103253',4.5)]
#--------------------------------------------------------
    print("Recommended films with user-to-user")
    for i,(film,rate) in enumerate(r.recommend_user_to_user(user_input,10,0.9)):
        print(i+1,". ",r.movie_name(film),sep ='')
    print("----------------------------------------------")
#--------------------------------------------------------
    print("Recommended films with item-to-item")
    for i,(film,rate) in enumerate(r.recommend_item_to_item(user_input,10,0.9)):
        print(i+1,". ",r.movie_name(film),sep ='')
main()
