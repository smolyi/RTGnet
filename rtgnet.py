import argparse

from RTGGraphParser import RTGparser
from classes.grammar import InputfileGrammarReader
from classes.MyGraph import Graph
from classes.parseGraph import ParseGraph

import pickle 

def __dumpResults(results, dumpFilePath = None,pklFilePath = None):

    results.sort(key = lambda x:x[0].score, reverse = True)
    if dumpFilePath:
        resultsFile = open(dumpFilePath,"w")
        for ke,occ in results:
            resultsFile.write("%f\t%s\t%s\t%s\t%s\n"%(occ.score, occ.signature.hash(), str(occ.nodes), str(occ.edges), str(occ.derivations)) )
        
            #resultsFile.write("%s\t%s\t%f\t%f\n"%(self.__tupleAsString(path[0]),self.__tupleAsString(path[1]),path[2],path[3])) 
        resultsFile.close()
    if pklFilePath:
        fpkl = open(pklFilePath,'w')
        pickle.dump( map (lambda x:x[1],results), fpkl )
        fpkl.close()

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='The RTGnet tool implements a graph-search algorithm which identifies the k-best trees defined using a Regular Tree Grammar (RTG). The user must specify the graph to be searched, the RTG query which defines the trees to be searched and additional parameters (see below). The algorithm was published in a peer-reviewed journal [https://www.liebertpub.com/doi/full/10.1089/cmb.2015.0168]. RTGnet is implemented in Python2.7, no setup or compilation is required.')
    parser.add_argument( 'graph',type=str, help='A graph file path. Format: node1<tab>node2<tab>weight.')
    parser.add_argument( 'nodes',type=str, help='A node-labeling file path. Format: node<tab>label.')
    parser.add_argument( 'grammar',type=str, help='A grammar file path. Format: node<tab>label.')
    parser.add_argument( 'k',type=int, help='The number of trees in the output.')
    parser.add_argument( 'maxSize',type=int, help='The upper bound on the number of nodes in the output trees.')
    parser.add_argument( '-t',type=float, help='A lower bound on the score of the sought trees.',default=0)
    parser.add_argument('-ss',type=int, dest='ss', help='Scoring scheme.1=sum of edge weights. 2=Average of edge weights.3=sum of grammar weights' ,default=1)
    #   parser.add_argument('-sf',type=int, dest='sf', help='Scoring function.' ,default=0)
    args = parser.parse_args()
    
    grammar = InputfileGrammarReader(args.grammar).grammar
    graph = Graph()
    graph.loadEdgesFile(args.graph,  directed = 0, attributes = {2:("score",float)})
    graph.loadValuesMetaFile(args.nodes, 'label', 0, 1)
    
    dumpFilePath = "dump.txt"
    pklFilePath = "dump.pkl"
    
    parseAlpha = ParseGraph(grammar).parseGraph(args.maxSize)
    
    cp = RTGparser(graph, grammar, args.k, args.maxSize, args.t,args.ss, parseAlpha)
    results = cp.Query(pklFilePath)
    print len(results) , "trees found"
    __dumpResults(results.values(),dumpFilePath,pklFilePath)
   


 
