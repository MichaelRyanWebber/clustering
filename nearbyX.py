# this is an algorithm with test for grouping data points into
# an undetermined number of clusters, satisfying the criteria
# that any two points with X eculidian distance must be in the
# same cluster. This may result in large blobs, high variance
# in cluster size depending on the input data.

from scipy.spatial import distance
import plotly
from plotly.graph_objs import Scatter, Layout
from clupt import *
from geopy.distance import great_circle
import csv

def testMat(returnPtObjs=False):
    mat = list()

    for i in range(2000):
        for j in range(2000):
            if (i % 4 == 0) and (j % 10 != 0):
                mat.append([[i, j], -1])
            elif j % 8 == 0:
                mat.append([[i, j], -1])

    # mat.append([[3.54, 8.9], -1])
    # mat.append([[6.7, 32.1], -1])

    del mat[4:6]

    if returnPtObjs == True:
        matClupt = list()
        for index, pt in enumerate(mat):
            matClupt.append(CluPt(pt[0][0], pt[0][1], index))
        return matClupt

    return mat


# join the clusters specified by ids
# expects ids as a set
def joinClusters(clusters, ids):
    lids = list(ids)
    for index in lids[1:]:
        clusters[lids[0]].extend(clusters[index])

    for pt in clusters[lids[0]]:
        pt.cluId = lids[0]

    for index in lids[1:]:
        clusters[index] = []


# cluster points that are within X of each other
def clusterNNX(mat, X):
    # clusters is list of lists of cluPts
    clusters = list()
    clindex = 0
    clusters.append([mat[0]])
    mat[0].cluId = clindex
    for pt1 in mat:

        # first check if this is a neighbor to an existing cluster
        joinIds = set()
        for aclustr in clusters:
            for pt2 in aclustr:
                if distance.euclidean(pt1.xy(), pt2.xy()) < X and pt1 != pt2:
                    if len(joinIds) == 0:
                        pt1.cluId = pt2.cluId
                        aclustr.append(pt1)
                        joinIds.add(pt1.cluId)
                    else:
                        joinIds.add(pt2.cluId)

        # see if this point should join 2 or more existing clusters
        if len(joinIds) > 1:
            joinClusters(clusters, joinIds)

        # see if pt1 has been put into a cluster yet
        # if not, check the remaining points
        if pt1.inClu() == False:
            for pt2 in mat:
                if (distance.euclidean(pt1.xy(), pt2.xy()) < X) and (pt1 != pt2):
                    clindex += 1
                    pt1.cluId = clindex
                    pt2.cluId = clindex
                    clusters.append([pt1, pt2])
                    break

        # if still not in a cluster, we know this pt is
        # a singleton cluster
        if pt1.inClu() == False:
            clindex += 1
            pt1.cluId = clindex
            clusters.append([pt1])

    return clusters


# cluster but use a bucket grid to limit the search for NN
# bucket size is dependent on max radius X
def bucskterNNX(mat, X):
    # clusters is list of lists of cluPts
    clusters = list()
    clindex = 0

    # buckets contains a sparse array of pts based on their
    # proximity, implemented as a dict keyed on coordinates
    buckets = Buckets(X)
    buckets.makeBuckets(mat)
    bucketsclu = Buckets(X)

    # initialize the array of clusters
    # putting the 1st point in the 1st cluster
    clusters.append([mat[0]])
    mat[0].cluId = clindex
    buckets.remove(mat[0])
    bucketsclu.add(mat[0])

    # loop through each point, finding its cluster
    for pt1 in mat[1:]:

        neighborkeys = buckets.getNeighborKeys(pt1)

        joinIds = set()

        # check if this point was already added to a cluster
        if pt1.inClu():
            continue

        # first check if this is a neighbor to an existing cluster
        for key in neighborkeys:
            # check if this bucket has clustered points
            for pt2 in bucketsclu.getBucket(key):
                if distance.euclidean(pt1.xy(), pt2.xy()) < X and pt1 != pt2:
                    if len(joinIds) == 0:
                        pt1.cluId = pt2.cluId
                        clusters[pt1.cluId].append(pt1)
                        joinIds.add(pt1.cluId)
                        # switch to bucketsclu for this point
                        buckets.remove(pt1)
                        bucketsclu.add(pt1)
                    else:
                        joinIds.add(pt2.cluId)

        # see if this point should join 2 or more existing clusters
        if len(joinIds) > 1:
            joinClusters(clusters, joinIds)

        # see if pt1 has been put into a cluster yet
        # if not, check the remaining points
        if pt1.inClu():
            continue

        for key in neighborkeys:
            # check if this bucket has clustered points
            for pt2 in buckets.getBucket(key):
                if distance.euclidean(pt1.xy(), pt2.xy()) < X and pt1 != pt2:
                    clindex += 1
                    pt1.cluId = clindex
                    pt2.cluId = clindex
                    clusters.append([pt1, pt2])
                    # switch to bucketsclu for these two points
                    buckets.remove(pt1)
                    buckets.remove(pt2)
                    bucketsclu.add(pt1)
                    bucketsclu.add(pt2)
                    break

        # if still not in a cluster, we know this pt is
        # a singleton cluster
        if not pt1.inClu():
            clindex += 1
            pt1.cluId = clindex
            clusters.append([pt1])
            buckets.remove(pt1)
            bucketsclu.add(pt1)

    return clusters

# this is almost exactly the code from bucksterNNX
# but takes in already made buckets...
def clusterFromBucket(buckets):
    mat = buckets.allPoints()
    # clusters is list of lists of cluPts
    clusters = list()
    clindex = 0

    # buckets contains a sparse array of pts based on their
    # proximity, implemented as a dict keyed on coordinates
    bucketsclu = Buckets(buckets.maxRadius)

    # initialize the array of clusters
    # putting the 1st point in the 1st cluster
    clusters.append([mat[0]])
    mat[0].cluId = clindex
    buckets.remove(mat[0])
    bucketsclu.add(mat[0])

    # loop through each point, finding its cluster
    for pt1 in mat[1:]:

        neighborkeys = buckets.getNeighborKeys(pt1)

        joinIds = set()

        # check if this point was already added to a cluster
        if pt1.inClu():
            continue

        # first check if this is a neighbor to an existing cluster
        for key in neighborkeys:
            # check if this bucket has clustered points
            for pt2 in bucketsclu.getBucket(key):
                if distance.euclidean(pt1.xy(), pt2.xy()) < buckets.maxRadius and pt1 != pt2:
                    if len(joinIds) == 0:
                        pt1.cluId = pt2.cluId
                        clusters[pt1.cluId].append(pt1)
                        joinIds.add(pt1.cluId)
                        # switch to bucketsclu for this point
                        buckets.remove(pt1)
                        bucketsclu.add(pt1)
                    else:
                        joinIds.add(pt2.cluId)

        # see if this point should join 2 or more existing clusters
        if len(joinIds) > 1:
            joinClusters(clusters, joinIds)

        # see if pt1 has been put into a cluster yet
        # if not, check the remaining points
        if pt1.inClu():
            continue

        for key in neighborkeys:
            # check if this bucket has clustered points
            for pt2 in buckets.getBucket(key):
                if distance.euclidean(pt1.xy(), pt2.xy()) < buckets.maxRadius and pt1 != pt2:
                    clindex += 1
                    pt1.cluId = clindex
                    pt2.cluId = clindex
                    clusters.append([pt1, pt2])
                    # switch to bucketsclu for these two points
                    buckets.remove(pt1)
                    buckets.remove(pt2)
                    bucketsclu.add(pt1)
                    bucketsclu.add(pt2)
                    break

        # if still not in a cluster, we know this pt is
        # a singleton cluster
        if not pt1.inClu():
            clindex += 1
            pt1.cluId = clindex
            clusters.append([pt1])
            buckets.remove(pt1)
            bucketsclu.add(pt1)

    return clusters


# run the clustering and fix checking stuff on the combined_2014.csv
def verify_from_csv(path, maxRadius, path2):
    delimiter = ','
    # open with read/write and universal newline support
    with open(path, 'rU+') as file:
        reader = csv.reader(file, delimiter=delimiter)

        firstline = True
        buckets = Buckets(maxRadius)


        # hard code the google maps state gps coordinates for fun
        center = tuple([42.4072107, -71.3824374])

        for row in reader:
            if firstline:
                firstline = False
                continue

            # table format
            # id,formatted_address,lat,lng,location_type,record_date,grade,record_type
            # populate these USEFUL VARIABLES
            id = row[0]
            lat = float(row[2])
            lng = float(row[3])
            location_type = row[4]
            record_type = row[7]

            # use the first point as a center for coordinate positions in feet
            # if secondline:
            #   center = tuple([lat, lng])
            #   secondline = False

            # check if the location is junk, and we don't want to process
            if location_type in ('APPROXIMATE','GEOMETRIC_CENTER'):
                continue

            # get coords in terms of integer feet and x,y
            y = int(great_circle(center, tuple([lat, center[1]])).feet)
            x = int(great_circle(center, tuple([center[0], lng])).feet)
            # now fix x and y to so they are not absolute values (i.e. distance)
            if center[0] > lat:
                y *= -1
            if center[1] > lng:
                x *= -1

            # check if this is a leak or fix
            if record_type == '2014_leak':
                leak_clupt = CluPt(x, y, id)
                # find a cluster for this point
                buckets.add(leak_clupt)

            if record_type == '2014_repaired':
                # remove all points within distance of this repair
                fix_clupt = CluPt(x, y, id)
                keys = buckets.getNeighborKeys(fix_clupt)
                for key in keys:
                    for pt in buckets.getBucket(key):
                        if distance.euclidean(fix_clupt.xy(), pt.xy()) < maxRadius:
                            buckets.remove(pt)

    print 'Number of points at end of 2014 ', len(buckets.allPoints())

    # now we have all the remaining unrepaired pts in buckets
    # to check against the known leaks as of 2015 make a set of ids to compare to
    recorded_unrepaired = set()
    with open(path2, 'rU+') as file:
        reader = csv.reader(file, delimiter=delimiter)
        for row in reader:
            recorded_unrepaired.add(row[0])

    # iterate over points in buckets to check if in the above set
    for pt in buckets.allPoints():
        if pt.originId in recorded_unrepaired:
            buckets.remove(pt)

    print 'Number of points not accounted for ', len(buckets.allPoints())

    return buckets


def graphClusters(clusters):
    x = list()
    y = list()
    traceList = list()

    for aclustr in clusters:
        for pt in aclustr:
            x.append(pt.x)
            y.append(pt.y)
        traceList.append(Scatter(x=x, y=y, mode='markers'))
        x = list()
        y = list()
        print

    # plotly.offline.plot({"data": [Scatter(x,y)], "layout": Layout(title="hello world")})
    # plotly.offline.plot([Scatter(x,y)])

    plotly.offline.plot(traceList)

def testCode():
    # execute test code for above functions
    # clusters = clusterNNX(testMat(True), 2)
    clusters = bucskterNNX(testMat(True), 2)
    graphClusters(clusters)

# testing code when run as main
if __name__ == "__main__":
    pathtocsv1 = '/Users/mwebber/alsogit/NatGas/NatGas/data/combined_2014.CSV'
    pathtocsv2 = '/Users/mwebber/alsogit/NatGas/NatGas/data/leaks_appearing_in_both_2014_2015.CSV'
    maxRadius = 20

    buckets = verify_from_csv(pathtocsv1, maxRadius, pathtocsv2)
    clusters = clusterFromBucket(buckets)
    graphClusters(clusters)