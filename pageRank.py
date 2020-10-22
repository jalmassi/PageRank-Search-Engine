from collections import *

class pageRank:

    def __init__(self,keyCitesVal,keyCitedByVal,damping=0.85):
        self.damping = damping
        self.keyCitesVal = keyCitesVal  #arrow outwards (len is denominator)
        self.keyCitedByVal = keyCitedByVal #arrow inwards
        self.keyCitesValCounted = Counter(self.keyCitesVal)
        self.keyCitedByValCounted = Counter(self.keyCitedByVal)
        # self.arrowsInwardCounted = Counter(self.keyCitedByVal)
        self.N = 3204
        self.score = defaultdict(lambda: damping/self.N)

    def pageRankAlgorithm(self,id):
        for doc in self.keyCitedByVal[str(id)]:
            totalOut = len(self.keyCitesVal[doc])

            if self.score[id] == 1/self.N:
                self.score[id] = self.score[doc] / totalOut
                # print('base score')
            else:
                self.score[id] += self.score[doc] / totalOut
            # if doc is not id:
            #     self.score[doc] = self.score[doc] / totalOut

        self.score[id] = self.damping * self.score[id]
        return self.score[id]

    def resetScore(self):
        self.score = defaultdict(lambda: 1/3204)
