class parseText:

    def __init__(self,file):
        self.file = file
        self.T = False
        self.Ab = False
        self.title = []
        self.abstract = []
        self.authors = []
        self.doc = {'id': '', 'title': '', 'abstract': '','authors': ''}
        self.documents = []
        self.prev = ''
        self.aut = False
    def isStopWord(self, x):
        if x in self.stopWords:
            return True
        return False

    def parseT(self):
        with open(self.file) as fo:
            self.T = False
            self.Ab = False

            for x in fo.read().split():

                x = x.lower()

                if self.prev == '.a':
                    self.aut = True

                if self.prev == ".i":
                    self.doc['id'] = int(x)

                if x == ".t":
                    self.T = True
                elif x == '.w':
                    self.Ab = True

                if self.Ab:
                    if x == ".w":
                        pass
                    elif x == ".b":
                        self.Ab = False
                        self.abstract = (' ').join(self.abstract)
                        self.doc['abstract'] = self.abstract
                        # self.documents.append(self.doc)
                        self.abstract = []
                        # self.doc = {'id': '', 'title': '', 'abstract': ''}
                    else:
                        self.abstract.append(x)
                if self.T:
                    if x == ".t":
                        pass
                    elif x == ".b" or x == ".w":
                        self.T = False
                        self.title = ' '.join(self.title)
                        self.doc['title'] = self.title
                        self.title = []
                        # if not self.Ab:
                        #     self.documents.append(self.doc)
                    else:
                        self.title.append(x)

                if (x == '.k' or x == '.n') and self.aut:
                    self.aut = False
                    self.authors = ' '.join(self.authors)
                    self.doc['authors'] = self.authors
                    self.documents.append(self.doc)
                    self.doc = {'id': '', 'title': '', 'abstract': '', 'authors': ''}
                    self.authors = []
                elif self.aut:
                    self.authors.append(x)

                self.prev = x

            fo.close()


