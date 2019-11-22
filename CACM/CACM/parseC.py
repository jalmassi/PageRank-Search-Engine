class parseQuery:

    def __init__(self, file):
        self.file = file
        self.c = False
        self.citations = []
        self.doc = {'id': '', 'citations': []}
        self.documents = []
        self.prev = ''

    def parseQ(self):
        with open(self.file) as fo:

            for x in fo.read().split():

                if self.prev == ".i":
                    self.doc['id'] = int(x)

                if x == ".x":
                    self.c = True

                if self.q:
                    if x == ".w":
                        pass
                    elif x == ".n":
                        self.q = False
                        self.citations = (' ').join(self.query)
                        self.doc['citations'] = self.citations
                        self.documents.append(self.doc)
                        self.citations = []
                        self.doc = {'id': '', 'citations': []}
                    else:
                        self.citations.append(x)

                self.prev = x
