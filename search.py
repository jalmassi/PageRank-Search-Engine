from invert import *
from parseText import *
import time
import shelve
import re
import math
from collections import Counter


def stem_word(word1):
    stemmer = PorterStemmer()
    stem1 = stemmer.stem(word1, 0, len(word1) - 1)
    return stem1

avgTime = 0
i = 0
query_times = []
count = 0
stStop = open('sStop.txt', 'r')
stopW = False
stem = False

parse = parseText('cacm.all')
parse.parseT()
db = DocPostings()
index = Invert(db)
docdb = DocFreqDb()
search_term = ''
frequency = False
df = 0

for line in stStop.readlines():
    for word in line.split():
        if re.search("my", word):
            stem = True
        if re.search("mn", word):
            stem = False
        if re.search('sy', word):
            stopW = True
        if re.search("sn", word):
            stopW = False

for doc in parse.documents:  # loops through documents and finds frequencies of terms in each document (aka term frequency) -> saves to database
    index.invert_index(doc, stopW, stem)

for key in index.index:  # finds document frequency (how many documents a term is present) and saves it to database
    e = DocFreq(index, key)
    docdb.add(e)

#
post = shelve.open("postings.shlf")  #saved dictionary
freq = shelve.open('frequency.shlf') #saved postings

N = 3204

while 1:
    splitWords = input('Enter term(s) to search: ').split()
    IDs = []
    sumWeights = {}
    for search_term in splitWords:
        if stem:
            search_term = stem_word(search_term)
        start = time.time()
        if search_term == 'zzend' or search_term == 'ZZEND':
            if count > 0:
                print("Average query time: " + str(avgTime) + " seconds")
            break
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
            #frequency = True
            for out in post[term]:
                for docID in out:
                    frequency = out[docID][0]
                    IDs.append(docID)

                    tf = 1 + math.log10(frequency)
                    w = tf * idf

                    if docID in sumWeights:
                        sumWeights[docID] += w
                    else:
                        sumWeights[docID] = w

                    # if docID not in weights:
                    #     weights[docID] = []
                    #     weights[docID].append(w)
                    # else:
                    #     weights[docID].append(w)


    #distances = {key: math.sqrt(value) for key, value in sumSquaredWeights.items()}
    query_count = Counter(splitWords)
    query_count = [pow(x,2) for x in query_count.values()]
    sum_query = sum(query_count)
    sqrt_query = math.sqrt(sum_query)
    normWeight = {}
    sumSqWeights = 0
    IDs = sorted(IDs)
    for id in IDs:
        for document in parse.documents:
            if document['id'] == id:
                document['text'] = document['title'] + ' ' + (document['abstract'])
                clean_text = re.sub(r'[^\w\s]', '', document['text'])
                wordList = clean_text.split(' ')
                count = Counter(wordList)
                print(count.items())
                # print(count)
                for wo,f in count.items():
                    for word in freq.keys():
                        if wo == word:
                            tf = 1 + math.log10(f)
                            for wor in freq.keys():
                                if wo == wor:
                                    df = freq[wor]
                            idf = math.log10(N/df)
                            weight = tf * idf
                            print(df)
                            squaredWeight = pow(weight,2)
                            sumSqWeights += squaredWeight
                            # print('{}: {}'.format(word, freq[word]))
                normWeight[id] = math.sqrt(sumSqWeights)

    sim = {}
    for docID in IDs:
        if normWeight is not 0:
            sim[docID] = (sumWeights[docID])/(sqrt_query*normWeight[docID])
            # print(normWeight[docID])
    print(sim.items())
    # print(idnormWeight.items())
    # print(weights)
    # print(distances)
    # print(sumSquaredWeights)




# post.clear()
# freq.clear()
# for term in post.keys():
# del post[term]
# post.close()
# freq.close()

