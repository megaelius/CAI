#!/usr/bin/python

import time
import sys
from math import sqrt

# a simple 4-node graph from the course slides
simple_graph = {
  "1": ["1","3","4"],
  "2": ["1","4"],
  "3": ["2","4"],
  "4": ["2"]
}

def read_airports():
# sample line:
# 1382,"Charles De Gaulle","Paris","France","CDG","LFPG",49.012779,2.55,392,1,"E"
    airportsTxt = open("airports.txt", "r",encoding="utf8");
    cont = 0
    airport_dict = {}
    for line in airportsTxt.readlines():
        try:
            temp = line.split(',')
            airp_name = temp[4][1:-1]
            airport_dict[airp_name] = (
                airp_name+
                " ("+temp[1][1:-1]+", "+
                temp[2][1:-1]+", "+
                temp[3][1:-1]+")"
                )
        except Exception as inst:
            # print("incorrect line in airports:",line)
            pass
    airportsTxt.close()
# for the sample line, it adds to dict the pair
# "CDG": "CDG (Charles de Gaulle, Paris, France)"
    print(airport_dict["CDG"])
    print(len(airport_dict), "airports read successfully")
    return airport_dict

def read_routes(airp):
# sample line:
# AB,214,CDG,1382,VIE,1613,Y,0,320 321
# note: there are no " quotes around airport names, unlike in airports.txt
    routesTxt = open("routes.txt", "r",encoding="utf8");
    cont = 0
    route_dict = {}
    nroutes = 0
    for line in routesTxt.readlines():
        try:
            temp = line.split(',')
            origin_airp = airp[temp[2]]
            dest_airp = airp[temp[4]]
            if not origin_airp in route_dict:
                route_dict[origin_airp] = [] # empty LIST
            ltemp = route_dict[origin_airp]
            ltemp.append(dest_airp)
            route_dict[origin_airp] = ltemp
            nroutes += 1
        except Exception as inst:
            # print("incorrect line, or unknown airport, in routes:", line)
            pass
    routesTxt.close()
    print(nroutes,"routes read successfully")

    # remove sinks: airports to which some route arrives
    # but from which no route leaves
    for i in route_dict.keys():
        route_dict[i] = [ j for j in route_dict[i] if j in route_dict]

    return route_dict

def compute_pageranks(g,d):
    # write your code
    pass

def output_pageranks(l):
    l = [(key,val) for key,val in l.items()]
    # sort decreasingly by rank
    l = sorted(l, key=lambda tup: -tup[1])
    sum = 0
    for (name, rank) in l:
        print(name+":", rank)
        sum += rank
    print("sum = ",sum)

def rank_simple_graph():
    damping_factor = 1  # to get the slide example. Change
    time1 = time.time()
    pageranks, iterations = compute_pageranks(simple_graph,damping_factor)
    time2 = time.time()
    output_pageranks(pageranks)
    print("#Iterations:", iterations)
    print("Time to computePageRanks():", time2-time1)

def rank_airports():
    damping_factor = 0.85  # Change
    airp = read_airports()
    routes = read_routes(airp)
    time1 = time.time()
    pageranks, iterations = compute_pageranks(routes,damping_factor)
    time2 = time.time()
    output_pageranks(pageranks)
    print("#Iterations:", iterations)
    print("Time to computePageRanks():", time2-time1)

rank_simple_graph()
#rank_airports()
