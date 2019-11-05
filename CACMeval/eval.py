from invert import *
from parseText import *
import time
import shelve
import re
import math
from collections import Counter
import operator
from parseQuery import *
from parseQrels import *

Qrels = parseQrels('qrels.text')
Qrels.parseQ()

def stem_word(word1):
    stemmer = PorterStemmer()
    stem1 = stemmer.stem(word1, 0, len(word1) - 1)
    return stem1


query_counter = 1
i = 0
query_times = []
count = 0
stStop = open('../CACMsearch/sStop.txt', 'r')
stopW = False
stem = False

pQ = parseQuery('query.text')
pQ.parseQ()
parse = parseText('cacm.all')
parse.parseT()
db = DocPostings()
index = Invert(db)
docdb = DocFreqDb()
search_term = ''
frequency = False
df = 0

with open('../CACMsearch/sStop.txt','r') as f:
    sym = [line.strip() for line in f]
print(sym)

if 'sy' in sym:
    stopW = True
if 'my' in sym:
    stem = True

for doc in parse.documents:  # loops through documents and finds frequencies of terms in each document (aka term frequency) -> saves to database
    index.invert_index(doc, stopW, stem)

for key in index.index:  # finds document frequency (how many documents a term is present) and saves it to database
    e = DocFreq(index, key)
    docdb.add(e)

# normWeight = shelve.open('normN.shlf')
if stopW and stem:
    normWeight = shelve.open('norm.shlf')
elif stopW:
    normWeight = shelve.open('normmN.shlf')
elif stem:
    normWeight = shelve.open('normsN.shlf')
elif not stopW and not stem:
    normWeight = shelve.open('normN.shlf')
else:
    # normWeight = shelve.open('norm.shlf')
    print('not working')

print(normWeight.items())
post = shelve.open("../CACMsearch/postings.shlf")  # saved dictionary

freq = shelve.open('../CACMsearch/frequency.shlf') #saved postings

N = 3204

splitWords = {}

for document in pQ.documents:
    clean_text = re.sub(r'[^\w\s]', '', document['query'])
    splitWords[document['id']] = clean_text

IDs = []
sumWeights = {}
sumAll = 0
sumMAP = 0
for id,terms in splitWords.items():

    sumQ = 0
    R = 0
    splitQuery = terms.split()
    for search_term in splitQuery:
        if stopW and is_stop_word(search_term):
            continue
        if stem:
            search_term = stem_word(search_term)

        # search for term in databases
        for word in freq.keys():
            if search_term == word:
                df = freq[word]
        if df is not 0:
            idf = math.log10(N/df)
        else:
            continue

        weights = {}
        distances = {}

        for term in post.keys():
            if term != search_term:
                continue
            for out in post[term]:
                for docID in out:
                    frequency = out[docID][0]


                    tf = 1 + math.log10(frequency)
                    w = tf * idf
                    if tf > 1:
                        IDs.append(docID)
                        if docID in sumWeights:
                            sumWeights[docID] += w
                        else:
                            sumWeights[docID] = w

    query_count = Counter(splitQuery)
    query_count = [pow(int(x),2) for x in query_count.values()]
    sum_query = sum(query_count)
    sqrt_query = math.sqrt(sum_query)
    IDs = set(IDs)
    IDs = sorted(IDs)

    sim = {}
    for docID in IDs:
        nw = float(normWeight[str(docID)])
        if (sqrt_query*nw) is not 0:
            sim[docID] = (sumWeights[docID])/(sqrt_query*nw)

    print(query_counter)
    rlen = 0
    sorted_sim = {}
    sorted_sim = sorted(sim.items(), reverse = True, key=operator.itemgetter(1))
    for key,val in enumerate(sorted_sim):
        for Qid, relevant in Qrels.relevants.items():
            if int(id) == int(Qid):
                for r in relevant:
                    rlen+=1
                    if int(r) == int(val[0]):
                        R += 1
                        Rprecision = R/rlen
                        print("Rprecision: " + str(Rprecision))
                        sumQ += Rprecision
    if rlen is not 0:
        mapQ = sumQ/rlen
        print("MAP of query: " + str(mapQ))
        sumMAP += mapQ

        # print((key+1),val)


    query_counter+=1

    print('-------------------------------------------------------------------------------------------------------------------------------------')
avgMAP = sumMAP/64
print("average MAP: " + str(avgMAP))
normWeight.close()
# for term in post.keys():
#     del post[term]
post.close()
freq.close()
#
