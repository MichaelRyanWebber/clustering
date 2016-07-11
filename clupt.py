import geopy


class CluPt:
    def __init__(self, x, y, index):
        self.x = x
        self.y = y
        self.cluId = -1
        self.originId = index
        return

    def inClu(self):
        if self.cluId == -1:
            return False
        else:
            return True

    def xy(self):
        return tuple([self.x, self.y])


# buckets of cluster points:
# a sparse array of lists implemented by dict keyed on xy-coord
# bucket size is defined by maxRadius (distance within which to group points)
class Buckets:

    # initialize a Buckets object, defined by maxRadius
    def __init__(self, X):
        self.maxRadius = X
        self.mBuckets = dict()

    # this is the hash used to assign buckets, floor division then
    # multiplication by maxRadius
    def getKey(self, pt):
        return tuple(
            [pt.x // self.maxRadius * self.maxRadius,
             pt.y // self.maxRadius * self.maxRadius])

    # return a list of keys for this bucket and the 8 adjacent buckets
    # does no bounds checking, as all access methods are safe to bounds
    def getNeighborKeys(self, pt):
        middle = self.getKey(pt)
        keys = list()
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                keyX = middle[0] + (i * self.maxRadius)
                keyY = middle[1] + (j * self.maxRadius)
                keys.append(tuple([keyX, keyY]))
        return keys

    # fill buckets, implemented as dict keyed on
    # the tuple of [x , y] coords, containing a list CluPts
    def makeBuckets(self, mat):
        for pt in mat:
            self.add(pt)

    # get a bucket: an always iterable safe bucket retrieve
    def getBucket(self, key):
        return self.mBuckets.get(key, range(0))

    # add a point to the appropriate bucket
    def add(self, pt):
        if self.getKey(pt) in self.mBuckets:
            self.mBuckets[self.getKey(pt)].append(pt)
        else:
            self.mBuckets[self.getKey(pt)] = [pt]

    # remove a point from the appropriate bucket
    # deleting the bucket if it is empty
    def remove(self, pt):
        self.mBuckets[self.getKey(pt)].remove(pt)
        if len(self.mBuckets[self.getKey(pt)]) == 0:
            del self.mBuckets[self.getKey(pt)]
