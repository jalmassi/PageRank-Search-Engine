class parseQrels:

    def __init__(self, file):
        self.file = file
        self.doc = {'Qid': [], 'DocID': ''}
        self.relevants = {}

    def parseQ(self):
        with open(self.file) as fo:

            for line in fo:
                line = line.split()
                if line[0] in self.relevants:
                    self.relevants[line[0]].append(line[1])
                else:
                    self.relevants[line[0]] = [line[1]]








        fo.close()
