import json
import sys
from queue import PriorityQueue
from math import radians, cos, sin, asin, sqrt

class BaMHD(object):
    def __init__(self, db_file='ba_mhd_db.json'):
        # Initialize BaMHD object, load data from json file
        self.data = json.load(open(db_file, 'r'))

    def distance(self, stop1, stop2):
        # Return distance between two stops in km.
        if isinstance(stop1, BusStop): stop1 = stop1.name
        if isinstance(stop2, BusStop): stop2 = stop2.name
        coords1 = self.data['bus_stops'][stop1]
        coords2 = self.data['bus_stops'][stop2]

        def haversine(lon1, lat1, lon2, lat2):
            # (You don`t need to understand following code - it`s just geo-stuff)
            # Calculate the great circle distance between two points on the earth (specified in
            # decimal degrees)
            # Courtesy of http://stackoverflow.com/a/15737218

            # convert decimal degrees to radians
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            # haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            km = 6367 * c
            return km

        return haversine(coords1[0], coords1[1], coords2[0], coords2[1])

    def neighbors(self, stop):
        # Return neighbors for a given stop
        return self.data['neighbors'][stop.name if isinstance(stop, BusStop) else stop]

    def stops(self):
        # Return list of all stops (names only)
        return self.data['neighbors'].keys()


class BusStop(object):
    # Object representing node in graph traversal. Includes name, parent node, and total cost of
    # path from root to this node (i.e. distance from start).
    def __init__(self, name, parent = None, pathLength = 0):
        self.name = name
        self.parent = parent
        self.pathLength = pathLength

    def traceBackPath(self):
        # Returns path represented by this node as list of node names (bus stop names).
        if self.parent == None:
            return [self.name]
        else:
            path = self.parent.traceBackPath()
            path.append(self.name)
            return path

class BSUC(BusStop):
    def __lt__(self, busStop):
        return self.pathLength < busStop.pathLength

class BSAS(BusStop):
    def __init__(self, name, parent = None, pathLength = 0, h = 0):
        super().__init__(name, parent, pathLength)
        self.h = h
        
    def __lt__(self, busStop):
        return self.pathLength + self.h < busStop.pathLength + busStop.h


def findPathUniformCost(bamhd, stopA, stopB):
    # Implement Uniform-cost search to find shortest path between two MHD stops in Bratislava.
    # Return a list of MHD stops, print how many bus stops were added to the "OPEN list"
    # and total path length in km.

    o = PriorityQueue()
    o.put(BSUC(stopA))
    res = None
    num = 1
    c = []
    while o.not_empty:
        n = o.get()
        if n.name in c:
            continue
        c.append(n.name)
        if n.name == stopB:
            res = n
            break
        for node in bamhd.neighbors(n):
            num += 1
            pathLength = bamhd.distance(n.name, node) + n.pathLength
            o.put(BSUC(node, n, pathLength))
    if res is None:
        return ["No path found"]
    print(f'\t{num} bus stops in "OPEN list", length = {res.pathLength}km')
    return res.traceBackPath()


def findPathAStar(bamhd, stopA, stopB):
    o = PriorityQueue()
    h = bamhd.distance(stopA, stopB)
    o.put(BSAS(stopA, h=h))
    num = 1
    c = []
    res = None
    while o.not_empty:
        n = o.get()
        if n.name in c:
            continue
        c.append(n.name)
        if n.name == stopB:
            res = n
            break
        for node in bamhd.neighbors(n):
            num += 1
            h = bamhd.distance(node, stopB)
            pathLength = bamhd.distance(n.name, node) + n.pathLength
            o.put(BSAS(node, n, pathLength, h))
    if res is None:
        return ["No path found"]
    print(f'\t{num} bus stops in "OPEN list", length = {res.pathLength}km')
    return res.traceBackPath()


if __name__ == "__main__":
    # Initialization
    bamhd = BaMHD()

    # Your task: find best route between two stops with:
    # A) Uniform-cost search
    print('Uniform-cost search:')
    print('Zoo - Aupark:')
    path = findPathUniformCost(bamhd, 'Zoo', 'Aupark')
    print(f'\tpath: {path}')

    print('VW - Astronomicka:')
    path = findPathUniformCost(bamhd, 'Volkswagen', 'Astronomicka')
    print(f'\tpath: {path}')

    # B) A* search
    print('\nA* search:')
    print('Zoo - Aupark:')
    path = findPathAStar(bamhd, 'Zoo', 'Aupark')
    print(f'\tpath: {path}')

    print('VW - Astronomicka:')
    path = findPathAStar(bamhd, 'Volkswagen', 'Astronomicka')
    print(f'\tpath: {path}')
