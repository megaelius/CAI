if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, help='Index to search')
    parser.add_argument('--query', default=None, nargs=argparse.REMAINDER, help='List of words to search')
    parser.add_argument('--nrounds', default=None, help='Number of iterations')
    parser.add_argument('--k', default=None, type=int, help='Number of docs')
    parser.add_argument('--R', default=None, type = int, nargs=argparse.REMAINDER, help='Maximum number of new terms')
    arser.add_argument('--alpha', default=None,type = int, nargs=argparse.REMAINDER, help='Weight original query')
    arser.add_argument('--beta', default=None, type = int,nargs=argparse.REMAINDER, help='Weight positive information')
#----------
    args = parser.parse_args()

        index = args.index
        query = args.query
        query_dic = {}
        for i in query:
            #Poner el elevado
            if i in query_dic:
                query_dict[i] += 1
            else:
                query_dict[i] = 1
        nrounds = args.nrounds
        k = args.k
        R = args.R
        alpha = args.alpha
        beta = args.alpha

        try:
            #Iniciamos elasticsearch
            client = Elasticsearch()
            s = Search(using=client, index=index)

            #Resolvemos el query y en base a los k primersos resultados lo actualizamos
            #mediante la regla de Roccio nrounds veces.
            for _ in range(nrounds):
                if query is not None:
                    q = Q('query_string',query=query[0])
                    for i in range(1, len(query)):
                        q &= Q('query_string',query=query[i])

                    s = s.query(q)
                    response = s[0:k].execute()
                    k_dicts =

            else:
                print('No query parameters passed')

            print (f"{response.hits.total['value']} Documents")

        except NotFoundError:
            print(f'Index {index} does not exists')
