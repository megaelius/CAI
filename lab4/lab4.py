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
'''
def Rocchio(query_dict,response_dicts,alpha,beta,R,k):
    dict_avg = dict_average(response_dicts,k)
    aux_nw = 0
    #   ESTO HAY QUE CAMBIARLO HEHE.
    for term in dict_avg:
        if term in query_dict:
            query_dict[term] = alpha*query_dict[term] + beta*dict_avg[term]
        elif aux_nw < R:
            aux_nw += 1
            query_dict[term] = beta*dict_avg[term]
    return query_dict
'''
def Rocchio(query_dict,response_dicts,alpha,beta,R,k):
    dict_avg = dict_average(response_dicts,k)
    new_terms = []
    for term in dict_avg:
        if term in query_dict:
            query_dict[term] = alpha*query_dict[term] + beta*dict_avg[term]
        else:
            new_terms.append((term,dict_avg[term]))
    new_terms.sort(key = lambda x: x[1], reverse = True)
    new_terms = dict(new_terms[:k])
    return query_dict, new_terms
#Function that parses and selects the arguments.
def parse_and_select():
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, help='Index to search')
    parser.add_argument('--nrounds', default=5, help='Number of iterations')
    parser.add_argument('--R', default=None, type = int, help='Maximum number of new terms')
    parser.add_argument('--k', default=5, type=int, help='Number of docs')
    parser.add_argument('--alpha', default=0.5,type = float, help='Weight original query')
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
        print('QUERY INICIAL', query)
        query_dict = ini_query_dic(query)

    try:
        # Iniciamos elasticsearch
        client = Elasticsearch()
        s = Search(using=client, index=index)

        # Resolvemos el query y en base a los k primeros resultados lo actualizamos
        # mediante la regla de Rocchio nrounds veces.
        for _ in range(nrounds):
                q = Q('query_string',query=query[0])
                for i in range(1, len(query)):
                    #CREO QUE FALLA AQUI AL PONER EL AND EN LA SEGUNDA ITERACION.
                    q &= Q('query_string',query=query[i])

                s = s.query(q)
                #Nos quedamos con los k documentos más relevantes
                response = s[0:k].execute()
                print(len(response))

                #Calculamos la representación en TFIDF para cada documento
                #y las guardamos en una lista.
                # No hace falta que los vectores esten ordenados en toTFIDF.
                response_dicts = []
                for r in response:
                    #Evitar repeticion codigo.
                    dr = dict(TFIDF.toTFIDF(client,index,TFIDF.search_file_by_path(client,index,r.path)))
                    response_dicts.append(dr)

                query_dict, new_terms_dict = Rocchio(query_dict,response_dicts,alpha,beta,R,k)
                query = []
                for term,weight in query_dict.items():
                    query.append(term + '^' + str(weight))

                for term,weight in new_terms_dict.items():
                    query.append(term + '^' + str(weight))

                print(query)

                print (f"{response.hits.total['value']} Documents")

    except NotFoundError:
        print(f'Index {index} does not exists')
