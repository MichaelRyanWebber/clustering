# this is an algorithm with test for grouping data points into
# an undetermined number of clusters, satisfying the criteria
# that any two points with X eculidian distance must be in the
# same cluster. This may result in large blobs, high variance
# in cluster size depending on the input data.

from scipy.spatial import distance

import plotly
from plotly.graph_objs import Scatter, Layout


def testMat():
    mat = list()
    for i in range(40):
        for j in range(20):
            if (i % 4 == 0) and (j % 10 != 0):
                mat.append([[i, j], -1])
            elif j % 8 == 0:
                mat.append([[i, j], -1])

    mat.append([[3.54,8.9],-1])
    # mat.append([[3.54,8.9],-1])



    del mat[4:6]

    return mat


# join the clusters specified by ids
# expects ids as a set
def joinClusters(clusters, ids):
    lids = list(ids)
    for index in lids[1:]:
        clusters[lids[0]].extend(clusters[index])

    for pt in clusters[lids[0]]:
        pt[1] = lids[0]

    for index in lids[1:]:
        clusters[index] = []


# cluster points that are within X of each other
def clusterNNX(mat,X):
    clusters = list()
    clindex = 0
    clusters.append([mat[0]])
    mat[0][1] = clindex
    for pt1 in mat:

        # first check if this is a neighbor to an existing cluster
        joinIds = set()
        for aclustr in clusters:
            for pt2 in aclustr:
                if distance.euclidean(pt1[0], pt2[0]) < X and pt1 != pt2:
                    if len(joinIds) == 0:
                        pt1[1] = pt2[1]
                        aclustr.append(pt1)
                        joinIds.add(pt1[1])
                    else:
                        joinIds.add(pt2[1])

        # see if this point should join 2 or more existing clusters
        if len(joinIds) > 1:
            joinClusters(clusters, joinIds)

        # see if pt1 has been put into a cluster yet
        # if not, check the remaining points
        if pt1[1] == -1:
            for pt2 in mat:
                if (distance.euclidean(pt1[0], pt2[0]) < X) and (pt1 != pt2):
                    clindex += 1
                    pt1[1] = clindex
                    pt2[1] = clindex
                    clusters.append([pt1, pt2])
                    break

        # if still not in a cluster, we know this pt is
        # a singleton cluster
        if pt1[1] == -1:
            clindex += 1
            pt1[1] = clindex
            clusters.append([pt1])

    return clusters


# execute test code for above functions

clusters = clusterNNX(testMat(), 2)
x = list()
y = list()
traceList = list()

for aclustr in clusters:
    for pt in aclustr:
        print pt[0],
        x.append(pt[0][0])
        y.append(pt[0][1])
    traceList.append(Scatter(x=x,y=y,mode='markers'))
    x = list()
    y = list()
    print


# plotly.offline.plot({"data": [Scatter(x,y)], "layout": Layout(title="hello world")})
# plotly.offline.plot([Scatter(x,y)])

plotly.offline.plot(traceList)


