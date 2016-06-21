
class cluPt:
    x = 0
    y = 0
    cluId = -1
    originId = -1

    def inClu(self):
        if self.cluId == -1:
            return False
        else:
            return True

    def xy(self):
        return tuple([self.x, self.y])

    def __init__(self, x, y):
        self.x = x
        self.y = y
        return

