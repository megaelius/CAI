"""
.. module:: TFIDFViewer

TFIDFViewer
******

:Description: TFIDMod

    Modified version of the original code provided in order to allow the
    importation of the code from another file. (cosine_similarity_automatic.py)

:Authors:
    Elias Abad Rocamora and Victor Novelle Moriano

:Version:

:Date:  08/10/2020
"""

from __future__ import print_function, division
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.client import CatClient
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q

import argparse

import numpy as np

__author__ = 'Elias Abad Rocamora and Victor Novelle Moriano'

def search_file_by_path(client, index, path):
    """
    Search for a file using its path

    :param path:
    :return:
    """
    s = Search(using=client, index=index)
    q = Q('match', path=path)  # exact search in the path field
    s = s.query(q)
    result = s.execute()

    lfiles = [r for r in result]
    if len(lfiles) == 0:
        raise NameError(f'File [{path}] not found')
    else:
        return lfiles[0].meta.id


def document_term_vector(client, index, id):
    """
    Returns the term vector of a document and its statistics a two sorted list of pairs (word, count)
    The first one is the frequency of the term in the document, the second one is the number of documents
    that contain the term

    :param client:
    :param index:
    :param id:
    :return:
    """
    termvector = client.termvectors(index=index, id=id, fields=['text'],
                                    positions=False, term_statistics=True)

    file_td = {}
    file_df = {}

    if 'text' in termvector['term_vectors']:
        for t in termvector['term_vectors']['text']['terms']:
            file_td[t] = termvector['term_vectors']['text']['terms'][t]['term_freq']
            file_df[t] = termvector['term_vectors']['text']['terms'][t]['doc_freq']
    return sorted(file_td.items()), sorted(file_df.items())


def toTFIDF(client, index, file_id):
    """
    Returns the term weights of a document

    :param file:
    :return:
    """

    # Get document terms frequency and overall terms document frequency
    file_tv, file_df = document_term_vector(client, index, file_id)

    max_freq = max([f for _, f in file_tv])

    dcount = doc_count(client, index)

    tfidfw = []
    #Computation of the tf-idf weights for each term in the document
    #
    for (t, w),(_, df) in zip(file_tv, file_df):
        tf = w/max_freq
        idf = np.log2(dcount/df)
        weight = tf*idf
        tfidfw.append((t,weight))

    return normalize(tfidfw)

def print_term_weigth_vector(twv):
    """
    Prints the term vector and the corresponding weights
    :param twv:
    :return:
    """
    for(t,w) in twv:
        print(t,":",w)
    pass


def normalize(tw):
    """
    Normalizes the weights in t so that they form a unit-length vector
    It is assumed that not all weights are 0
    :param tw:
    :return:
    """
    # Separated paired elements in tuple to separate tuples.
    unzipped_object = zip(*tw)
    unzipped_list = list(unzipped_object)
    # Selection of the weight elements from the list (discard the terms).
    weight_vector = unzipped_list[1]
    norm = np.linalg.norm(weight_vector)
    # Normalitzation of the weight for each term in the document.
    tw_norm = [(t,w/norm) for (t,w) in tw]
    return tw_norm


def cosine_similarity(tw1, tw2):
    """
    Computes the cosine similarity between two weight vectors, terms are alphabetically ordered
    :param tw1:
    :param tw2:
    :return:
    """
    i = j = 0
    sim = 0
    while i < len(tw1) and j < len(tw2):
        if tw1[i][0] < tw2[j][0]:
            i+=1
        elif tw1[i][0] > tw2[j][0]:
            j+=1
        else:
            sim += tw1[i][1]*tw2[j][1]
            i+=1
            j+=1
    return sim

def doc_count(client, index):
    """
    Returns the number of documents in an index

    :param client:
    :param index:
    :return:
    """
    return int(CatClient(client).count(index=[index], format='json')[0]['count'])


def obtain_value(index,file1,file2):

    client = Elasticsearch()

    try:

        # Get the files ids
        file1_id = search_file_by_path(client, index, file1)
        file2_id = search_file_by_path(client, index, file2)

        # Compute the TF-IDF vectors
        file1_tw = toTFIDF(client, index, file1_id)
        file2_tw = toTFIDF(client, index, file2_id)

        return(cosine_similarity(file1_tw, file2_tw))

    except NotFoundError:
        print(f'Index {index} does not exists')
