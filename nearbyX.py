# this is an algorithm with test for grouping data points into
# an undetermined number of clusters, satisfying the criteria
# that any two points with X eculidian distance must be in the
# same cluster. This may result in large blobs, high variance
# in cluster size depending on the input data.

from scipy.spatial import distance
import plotly
from plotly.graph_objs import Scatter, Layout
from CluPt import *


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
        if pt1.inClu(): continue

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
        if pt1.inClu(): continue

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


# testing code when run as main
if __name__ == "__main__":
    # execute test code for above functions
    # clusters = clusterNNX(testMat(True), 2)
    clusters = bucskterNNX(testMat(True), 2)
    x = list()
    y = list()
    traceList = list()

    for aclustr in clusters:
        for pt in aclustr:
            print pt.xy(),
            x.append(pt.x)
            y.append(pt.y)
        traceList.append(Scatter(x=x, y=y, mode='markers'))
        x = list()
        y = list()
        print

    # plotly.offline.plot({"data": [Scatter(x,y)], "layout": Layout(title="hello world")})
    # plotly.offline.plot([Scatter(x,y)])

    plotly.offline.plot(traceList)
