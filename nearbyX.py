# this is an algorithm with test for grouping data points into
# an undetermined number of clusters, satisfying the criteria
# that any two points with X eculidian distance must be in the
# same cluster. This may result in large blobs, high variance
# in cluster size depending on the input data.

from scipy.spatial import distance


def testMat():
    mat = list()
    for i in range(200):
        for j in range(200):
            if i % 4 == 0:
                mat.append([[i, j], -1])

    del mat[4:6]

    return mat

# cluster points that are within X of each other
def clusterNNX(mat,X):
    clusters = list()
    clindex = 0
    clusters.append([mat[0]])
    mat[0][1] = clindex
    for pt1 in mat[1:]:

        # first check if this is a neighbor to an existing cluster
        for aclustr in clusters:
            for pt2 in aclustr:
                if distance.euclidean(pt1[0], pt2[0]) < X:
                    pt1[1] = pt2[1]
                    aclustr.append(pt1)
                    break
            if pt1[1] != -1:
                break

        # see if pt1 has been put into a cluster yet
        # if not, check the remaining points
        if pt1[1] == -1:
            for pt2 in mat:
                if (distance.euclidean(pt1[0], pt2[0]) < X) & (pt1 != pt2):
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

clusters = clusterNNX(testMat(),2)

for aclustr in clusters:
    print aclustr


