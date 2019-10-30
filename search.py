from invert import *
from parseText import *
import time
import shelve
import re
import math


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

N = len(freq)

while 1:
    search_term = input('Enter term(s) to search: ')
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

    idf = math.log10(N/df)
    weights = {}
    for term in post.keys():
        if term != search_term:
            continue
        frequency = True
        for out in post[term]:
            for docID in out:
                frequency = out[docID][0]


                tf = 1 + math.log10(frequency)
                w = tf * idf
                weights[docID] = w

        print(weights)



'''    print("---------------------------------------------------------------------------------------------------")
    if frequency:
        print('Document Frequency: ' + str(docdb.getWordFreq(search_term)))
    else:
        print('Document Frequency: None')
    frequency = False
    count += 1
    end = time.time()
    duration = end - start
    duration = round(duration, 3)
    query_times.append(duration)
    avgTime = sum(query_times) / count
    avgTime = round(avgTime, 3)
    print("Time for query: " + str(duration) + " seconds")
    print("---------------------------------------------------------------------------------------------------")
post.clear()
freq.clear()
for term in post.keys():
    del post[term]
post.close()
freq.close()'''

