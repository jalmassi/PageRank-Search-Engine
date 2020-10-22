import shelve
from invert import *
from parseText import *
import time
import math
import operator
from pageRank import *
from collections import *

def stem_word(word1):
    stemmer = PorterStemmer()
    stem1 = stemmer.stem(word1, 0, len(word1) - 1)
    return stem1


avgTime = 0
i = 0
query_times = []
count = 0
stStop = open('../sStop.txt', 'r')
stopW = False
stem = False

parse = parseText('cacm.all')
parse.parseT()
parse1 = parseText('cacm.all')
parse1.parseT()
db = DocPostings()
index = Invert(db)
docdb = DocFreqDb()
search_term = ''
frequency = False
df = 0


with open('../sStop.txt', 'r') as f:
    sym = [line.strip() for line in f]
#print(sym)

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
    normWeight = shelve.open('../../CACMeval/norm.shlf')
elif stopW:
    normWeight = shelve.open('../../CACMeval/normmN.shlf')
elif stem:
    normWeight = shelve.open('../../CACMeval/normsN.shlf')
elif not stopW and not stem:
    normWeight = shelve.open('../../CACMeval/normN.shlf')
else:
    # normWeight = shelve.open('norm.shlf')
    print('not working')

citations = shelve.open("../../CACMsearch/citations.shlf")  # open saved citations dictionary - key is

post = shelve.open("../../CACMsearch/postings.shlf")  # saved dictionary

freq = shelve.open('../../CACMsearch/frequency.shlf')  # saved postings

keyCitesVal = shelve.open('../keyCitesVal.shlf')  # arrows pointing away
keyCitedByVal = shelve.open('../keyCitedByVal.shlf')  # arrows pointing inwards

pageRankScores = open('../pageRankScores.txt', 'w')

pgRank = pageRank(keyCitesVal, keyCitedByVal)
# pgRank.pageRankAlgorithm(3204)
# pgRank.resetScore()

N = 3204

weightRank, weightpageRank = input('write the two weights (second is for PageRank) where w1+w2=1\n').split()

while 1:

    splitWords = input('Enter term(s) to search: ').split()
    i = 0
    sorted_sim = {}
    IDs = []
    sumWeights = {}
    pgRank.resetScore()
    for search_term in splitWords:
        i+=1
        if search_term == 'zzend' or search_term == 'ZZEND':
            break
        else:
            if len(search_term) < 3:
                continue
            search_term = search_term.lower()
            if stopW and is_stop_word(search_term):
                continue
            if stem:
                search_term = stem_word(search_term)


            # search for term in databases
            for word in freq.keys():
                if search_term == word:
                    df = freq[word]
            if df is not 0:
                idf = math.log10(N / df)
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
                        IDs.append(docID)


                        tf = 1 + math.log10(frequency)
                        w = tf * idf


                        if docID in sumWeights:
                            sumWeights[docID] += w
                        else:
                            sumWeights[docID] = w



        query_count = Counter(splitWords)
        query_count = [pow(x, 2) for x in query_count.values()]
        sum_query = sum(query_count)
        sqrt_query = math.sqrt(sum_query)
        IDs = sorted(IDs)


        if IDs == []:
            print("No Results")
            continue

        sim = {}
        for docID in IDs:
            nw = float(normWeight[str(docID)])
            if (sqrt_query * nw) is not 0:
                sim[docID] = (float(weightRank)*sumWeights[docID]) / (sqrt_query * nw)


        currentScore = defaultdict(lambda: 1)
        previousScore = defaultdict(lambda: 0) #collects scores and saves in file
        for key, val in enumerate(sim):
            if i == 1:
                sim[val] = sim[val] / 100
            # print(sim[val],val)
            # print("\n")

            while(abs(previousScore[val] - currentScore[val]) > 0.000000000001): #uses power method until the change in pageRank is too small
                # print(type(pgRank.pageRankAlgorithm(val[0])))
                # val = list(val)
                # print(val,sim[val])
                x = currentScore[val]
                currentScore[val] = 10*pgRank.pageRankAlgorithm(val)


                # print(val,currentScore[val])
                previousScore[val] = x
            # print(currentScore[val])
            currentScore[val] *= float(weightpageRank)
            sim[val] += currentScore[val]
            # currentScore[val] *= float(weightpageRank)*currentScore[val]
            # print(val, currentScore[val])

        # for key, val in enumerate(sim):
        #     print(sim[val],val)

        sorted_sim = sorted(sim.items(), reverse=True, key=operator.itemgetter(1))

    if search_term != 'zzend':
        for key, val in enumerate(sorted_sim[:50]):
            print((key + 1), val,end="\t")

            for doc in parse1.documents:
                if doc['id'] == val[0]:
                    print("Authors: " + doc['authors'],end='\t')
                    print("Title: " + doc['title'])

        # currentScore = sorted(currentScore.items(), key=operator.itemgetter(1))

        for key,element in sorted(currentScore.items(),key = lambda kv:(kv[1], kv[0]),reverse=True):
            # print(key,element)
            pageRankScores.write("{}: {}\n".format(key, element))
        pageRankScores.write("\n")
    else:
        break

pageRankScores.close()
keyCitesVal.close()
keyCitedByVal.close()
normWeight.close()
# post.clear()
# for term in post.keys():
#     del post[term]
post.close()
freq.close()

# for doc in parse1.documents:
                    #     for name in doc['authors'].split(' '):
                    #         if len(name) < 4:
                    #             continue
                    #         name = name.replace(',', '')
                    #         if stem:
                    #             name = stem_word(name)
                    #
                    #         if search_term == name:
                    #             w *= 100
                    #             break

                        # for werd in doc['title'].split(' '):
                        #     if len(name) < 4:
                        #         continue
                        #     if stem:
                        #         name = stem_word(name)
                        #     if search_term == werd:
                        #         frequency *= 2