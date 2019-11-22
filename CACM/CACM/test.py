from invert import *
from parseText import *
import time

query_times = []
count = 0

parse = parseText('cacm.all')
parse.parseT()
db = DocPostings()
index = Invert(db)
docdb = DocFreqDb()
search_term = ''

postings_list = open('postings.txt', 'w')
frequency_list = open('dictionary.txt', 'w')

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


for doc in parse.documents:  # loops through documents and finds frequencies of terms in each document (aka term frequency) -> saves to database
    index.invert_index(doc, stopW, stem)


for key in index.index:  # finds document frequency (how many documents a term is present) and saves it to database
    e = DocFreq(index, key)
    docdb.add(e)

for element in sorted(index.index.keys()):
    postings_list.write("{}: {}\n".format(element,index.index[element]))

for element in sorted(docdb.freq.keys()):
    frequency_list.write("{}: {}\n".format(element,docdb.freq[element]))


while 1:
    search_term = input('Enter term(s) to search: ')
    start = time.time()
    if search_term == 'zzend' or search_term == 'ZZEND':
        if count > 0:
            print("Average query time: " + str(avgTime) + " seconds")
        break
    result = index.search(search_term)  # search for term in databases

    for term in result.keys():
        for out in result[term]:
            # docID is key for frequency and position list
            docID = list(out.keys())[0]
            frequency = out[docID][0]
            positions = out[docID][1]
            document = db.get(docID)
            print("docID :", docID, "\tfrequency :", frequency, "\tword positions:", positions)
            print(title_highlight_term(docID, term, document['title']))
            if not document['abstract'] == '':
                if is_term_highlighted(docID, term, document['title']):
                    abstract = document['abstract'].split()
                    abstract = ' '.join(abstract[:10])
                    print("Abstract: " + abstract)
                else:
                    print(abstract_highlight_term(docID, term, document['abstract']))
        print("---------------------------------------------------------------------------------------------------")
    print('Document Frequency: ' + str(docdb.getWordFreq(search_term)))
    count += 1
    end = time.time()
    duration = end - start
    duration = round(duration,3)
    query_times.append(duration)
    avgTime = sum(query_times)/count
    avgTime = round(avgTime,3)
    print("Time for query: " + str(duration) + " seconds")
    print("---------------------------------------------------------------------------------------------------")


