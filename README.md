# SearchCACM
The PageRank algorithm is used to calculate the scores while the index is being created, and is used to rank the results after the user submits a query.

The document collection used is the CACM Collection

The program is split into three different parts:

invert : Creates the inverted index for the document collection. The output are files which are needed for the other two programs
search : Provides a command line interface to search for documents within the collection. This program uses the output files produced by the invert program
eval : Evaluates the results of the searching algorithm using the "query.text" and "qrels.text" files 

-disable/enable the removal of stopwords
-disable/enable porter stemming


