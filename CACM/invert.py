import re
from stem import *
from parseText import *
import shelve
import math
from collections import Counter

def stem_word(word):
    stemmer = PorterStemmer()
    stem = stemmer.stem(word, 0, len(word) - 1)
    return stem


def title_highlight_term(id, term, text):
    replaced_text = text.replace(term, "\033[1;32;40m {term} \033[0;0m".format(term=term), 1)
    return "Title: {replaced}".format(replaced=replaced_text)


def abstract_highlight_term(id, term, text):
    text_list = text.split()
    word_index = 0
    for index,word in enumerate(text_list):
        if term in word:
            word_index = index
    if word_index - 5 >= 0 and word_index + 5 < len(text_list):
        subtext_list = text_list[(word_index-5):(word_index+5)]
    elif word_index - 10 >= 0:
        subtext_list = text_list[(word_index - 10):word_index]
    elif word_index + 10 < len(text_list):
        subtext_list = text_list[word_index:(word_index + 10)]
    else:
        subtext_list = text_list[word_index:(word_index+5)]
    text = ' '.join(subtext_list)
    replaced_text = text.replace(term, "\033[1;32;40m {term} \033[0;0m".format(term=term), 1)
    return "Abstract: {replaced}".format(replaced=replaced_text)


def is_term_highlighted(id, term, text):
    replaced_text = text.replace(term, "\033[1;32;40m {term} \033[0;0m".format(term=term))
    if not replaced_text == text:
        return True
    return False


def stop_words():
    wordFile = open('common_words', 'r')
    wordList = wordFile.read()
    stopWords = wordList.split()
    return stopWords


def is_stop_word(x):
    if x in stop_words():
        return True
    return False


class Docs:
    def __init__(self, docID, frequency, position):
        self.docID = docID
        self.frequency = frequency
        self.position = position

    def append_position(self, position):
        self.position.append(position)
        return self.position

    def asdict(self):
        return {self.docID: [self.frequency, self.position]}


class DocPostings:
    def __init__(self):
        self.db = {}

    def get(self, id):
        return self.db.get(id, None)

    def add(self, document):
        return self.db.update({document['id']: document})

    def remove(self, document):
        return self.db.pop(document['id'], None)


class Invert:
    def __init__(self, db):
        self.index = dict()
        self.db = db
        stemmer = PorterStemmer

    def invert_index(self, document, stopW, stem):
        # document['text'] = 2*document['title'] + ' ' + document['abstract']
        clean_text = re.sub(r'[^\w\s]', '', document['abstract'])
        terms = clean_text.split(' ')
        out_dict = dict()
        word_position = 0

        for word in terms:
            word_position += 1
            if self.check_if_stop_word(word, stopW):
                continue
            if len(word) < 3:
                continue
            if stem:
                word = stem_word(word)

            if word in out_dict:
                term_frequency = out_dict[word].frequency
                positions = out_dict[word].append_position(word_position)
            else:
                term_frequency = 0
                positions = [word_position]
            out_dict[word] = Docs(document['id'], term_frequency + 1, positions)

            # document['text'] = 2 * document['title'] + ' ' + document['abstract'] + ' '
        clean_text = re.sub(r'[^\w\s]', '', document['authors'])
        terms = clean_text.split(' ')
        # out_dict = dict()
        word_position = 0

        for word in terms:
            word_position += 1
            if self.check_if_stop_word(word, stopW):
                continue
            if len(word) < 3:
                continue
            if stem:
                word = stem_word(word)

            if word in out_dict:
                term_frequency = out_dict[word].frequency
                positions = out_dict[word].append_position(word_position)
            else:
                term_frequency = 0
                positions = [word_position]
            out_dict[word] = Docs(document['id'], term_frequency + 100, positions)

            # document['text'] = 2 * document['title'] + ' ' + document['abstract'] + ' '
        clean_text = re.sub(r'[^\w\s]', '', document['title'])
        terms = clean_text.split(' ')
        # out_dict = dict()
        word_position = 0

        for word in terms:
            word_position += 1
            if self.check_if_stop_word(word, stopW):
                continue
            if len(word) < 3:
                continue
            if stem:
                word = stem_word(word)

            if word in out_dict:
                term_frequency = out_dict[word].frequency
                positions = out_dict[word].append_position(word_position)
            else:
                term_frequency = 0
                positions = [word_position]
            out_dict[word] = Docs(document['id'], term_frequency + 3, positions)

        for word in out_dict:
            out_dict[word] = out_dict[word].asdict()
        updateDict = {key: [out] if key not in self.index else self.index[key] + [out] for (key, out) in
                      out_dict.items()}
        self.index.update(updateDict)
        self.db.add(document)
        return document

    def search(self, query):
        return {term: self.index[term] for term in query.split(' ') if term in self.index}

    def check_if_stop_word(self, word, stopW):
        if not stopW:
            return False
        if is_stop_word(word):
            return True
        return False


class DocFreq:

    def __init__(self, invert, word):
        self.invIndex = invert
        self.word = word

    def getDocFreq(self):
        return len(self.invIndex.index[self.word])

    def str(self):
        return str(self.word) + ': ' + str(self.getDocFreq())


class DocFreqDb:

    def __init__(self):
        self.freq = dict()

    def add(self, docFreq):
        if docFreq.word not in self.freq:
            frequency = docFreq.getDocFreq()
            updateDict = {docFreq.word: frequency}
            self.freq.update(updateDict)
            return True
        return False

    def getWordFreq(self, word):
        if word in self.freq:
            return self.freq[word]

    def printWordFreq(self, word):
        frequency = self.getWordFreq(word)
        return str(word) + ': ' + str(frequency)

    def check_if_stop_word(self, word):
        stopWords = stop_words()
        if is_stop_word(word):
            return True
        return False

    def str(self):
        return self.freq


query_times = []
count = 0
stStop = open('../CACMsearch/sStop.txt','w')

parse = parseText('cacm.all')
parse.parseT()
db = DocPostings()
index = Invert(db)
docdb = DocFreqDb()
search_term = ''

norm_list = open('../CACMeval/normf.txt', 'w')
postings_list = open('../CACM1/postings.txt', 'w')
frequency_list = open('../CACM1/dictionary.txt', 'w')

useStem = input("Enter 'y' to use stem or 'n' to not use stem: ")
useStop = input("Enter 'y' to remove stop words or 'n' to to keep them: ")

if useStem == 'y':
    stem = True
elif useStem == 'n':
    stem = False

if useStop == 'y':
    stopW = True
elif useStop == 'n':
    stopW = False


if stopW == True:
    stStop.write("sy\n")
elif stopW == False:
    stStop.write("sn\n")

if stem == True:
    stStop.write("my")
elif stem == False:
    stStop.write("mn")

for doc in parse.documents:  # loops through documents and finds frequencies of terms in each document (aka term frequency) -> saves to database
    index.invert_index(doc, stopW, stem)


for key in index.index:  # finds document frequency (how many documents a term is present) and saves it to database
    e = DocFreq(index, key)
    docdb.add(e)

for element in sorted(index.index.keys()):
    postings_list.write("{}: {}\n".format(element,index.index[element]))

for element in sorted(docdb.freq.keys()):
    frequency_list.write("{}: {}\n".format(element,docdb.freq[element]))

# file to be used
shelfPost = shelve.open("../CACMsearch/postings.shlf")
shelfFreq = shelve.open("../CACMsearch/frequency.shlf")
# norm = shelve.open('../CACMeval/normf.shlf')

# serializing
for element in sorted(index.index.keys()):
    shelfPost[element] = index.index[element]

for element in sorted(docdb.freq.keys()):
    shelfFreq[element] = docdb.freq[element]

shelfPost.close()
shelfFreq.close()
shelfFreq = shelve.open("../CACMsearch/frequency.shlf")
normWeight = {}
sumSqWeights = 0
docs = {}
N = 3204
id = 0

'''for document in parse.documents:
    document['text'] = document['title'] + ' ' + (document['abstract'])
    id = document['id']
    docs[id] = document['title']
    clean_text = re.sub(r'[^\w\s]', '', document['text'])
    wordList = clean_text.split(' ')

    if stopW:
        wordList = [x for x in wordList if not is_stop_word(x)]
    if stem:
        wordList = [stem_word(x) for x in wordList]
    count = Counter(wordList)
    sumSqWeights = 0
    for wo, f in count.items():
        for word in shelfFreq.keys():
            if wo == word:
                tf = 1 + math.log10(f)
                for wor in shelfFreq.keys():
                    if wo == wor:
                        df = shelfFreq[wor]

                idf = math.log10(N / df)
                weight = tf * idf
                squaredWeight = pow(weight, 2)
                sumSqWeights += squaredWeight
    normWeight[id] = math.sqrt(sumSqWeights)
    norm[str(id)] = normWeight[id]
    norm_list.write("{}: {}\n".format(id, normWeight[id]))
    # print(id)
    print(id,normWeight[id])'''

# norm.close()

# frequency_list.close()
postings_list.close()



