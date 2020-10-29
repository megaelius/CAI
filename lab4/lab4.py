from __future__ import print_function
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from queue import PriorityQueue

import argparse

from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q

import TFIDFMod as TFIDF
#----------------------------------------------------------

# Computes the average tf-idf weight for the restrieved documents.
def dict_average(dict_list,k):
    result = {}
    # In case the number of documents that match the query < k.
    size = min(len(dict_list),k)
    for i in range(size):
        for word in dict_list[i]:
            if word in result:
                result[word] += dict_list[i][word]/size
            else: result[word] = dict_list[i][word]/size
    return result
#----------------------------------------------------------

#Applies Rocchio's rule to the current query.
def Rocchio(query_dict,response_dicts,alpha,beta,k):
    dict_avg = dict_average(response_dicts,k)
    query_dict = dict(TFIDF.normalize(query_dict.items()))
    for term in dict_avg:
        if term in query_dict:
            query_dict[term] = alpha*query_dict[term] + beta*dict_avg[term]
        else:
            query_dict[term] = beta*dict_avg[term]
    return query_dict

#Returns a dictionary containing top R elements from a dictionary
def select_top_R(query_dict,R):
    top_R = PriorityQueue(maxsize = R)
    for term,weight in query_dict.items():
        # Comparison with the least weighted term.
        if top_R.full():
            top = top_R.get()
            if(weight > top[0]):
                top_R.put((weight,term))
            else: top_R.put(top)
        else:
            top_R.put((weight,term))
    result = {}
    while not top_R.empty():
        aux = top_R.get()
        result[aux[1]] = aux[0]
    return result

#Function that parses and selects the arguments.
def parse_and_select():
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, help='Index to search')
    parser.add_argument('--nrounds', default=5, type = int, help='Number of iterations')
    parser.add_argument('--R', default=None, type = int, help='Maximum number of new terms')
    parser.add_argument('--k', default=5, type=int, help='Number of docs')
    parser.add_argument('--alpha', default=1,type = float, help='Weight original query')
    parser.add_argument('--beta', default=0.5, type = float,help='Weight positive information')
    parser.add_argument('--query', default=None, nargs=argparse.REMAINDER, help='List of words to search')
    args = parser.parse_args()

    return args.index,args.nrounds,args.R,args.k,args.alpha,args.beta,args.query
#----------------------------------------------------------

# Creates a dictionary for the user-introduced query.
def ini_query_dic(query):
    query_dict = {}
    for term in query:
        split_term = term.split('^')
        #We have found an specific weight for the term.
        if(len(split_term) > 1):
            weight = float(split_term[1])
        else: weight = 1

        word = split_term[0]
        #Check if the query already contined that word (e.g --query nyc nyc^2)
        if word in query_dict:
            query_dict[word] += weight
        else:
            query_dict[word] = weight
    return query_dict
#----------------------------------------------------------

if __name__ == '__main__':
    # Selection of the arguments.
    index,nrounds,R,k,alpha,beta,query = parse_and_select()

    #If the user introduced the agrument (--query) but not the terms to search.
    if not query:
        print('No query parameters passed!')
        raise SystemExit
    else:
        query_dict = ini_query_dic(query)

    try:
        # Start of elasticsearch
        client = Elasticsearch()
        s = Search(using=client, index=index)

        # The query is solved and, using the k most relevant documents retrieved,
        # the query is updated using the Rocchio's rule nrounds.
        for _ in range(nrounds):
                #Creation of the query.
                q = Q('query_string',query=query[0])
                for i in range(1, len(query)):
                    q &= Q('query_string',query=query[i])

                s = s.query(q)
                # We select the k most relevant documents.
                response = s[0:k].execute()

                # We compute the TFIDF representation for each document and
                #  store them in a list
                response_dicts = []
                for r in response:
                    dr = dict(TFIDF.toTFIDF(client,index,TFIDF.search_file_by_path(client,index,r.path)))
                    response_dicts.append(dr)

                # Application of the Roccio's rule to the previous query.
                query_dict = Rocchio(query_dict,response_dicts,alpha,beta,k)

                #Selection of the R terms with higher weight.
                query_dict = select_top_R(query_dict,R)

                print(query_dict)


                query = []
                for term,weight in query_dict.items():
                    query.append(term + '^' + str(weight))

        # Number of documents found after the refination process.

        for r in response:  # only returns a specific number of results
            print(f'ID= {r.meta.id} SCORE={r.meta.score}')
            print(f'PATH= {r.path}')
            print(f'TEXT: {r.text[:50]}')
            print('-----------------------------------------------------------------')

        print (f"{response.hits.total['value']} Documents")

    except NotFoundError:
        print(f'Index {index} does not exists')
