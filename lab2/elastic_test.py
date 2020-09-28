"""
.. module:: testelastic

testelastic
******

:Description: testelastic

    Queries Elasticsearch to see if it is up

:Authors:
    bejar

:Version: 

:Date:  23/06/2017
"""

from __future__ import print_function
import requests

__author__ = 'bejar'

if __name__ == '__main__':
    try:
        resp = requests.get('http://localhost:9200/?pretty')

        print(resp.content)
    except Exception:
        print('Elastic search is not running')
