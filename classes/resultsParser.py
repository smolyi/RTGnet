import pickle
from conf import Converters
from MyFileHandler import MyFileHandler
from interactionSet import InteractionSet
from MyGraph import Graph
from GeneSet import GeneSet
import numpy,sys
from david import David
from fisher import pvalue
        

class ResultsHandler:
    def __init__(self, pklFilePath = None, occurences = None):
        if pklFilePath:
            self.occurrences = pickle.load(open(pklFilePath))
        elif occurences:
            self.occurrences = occurences
        else:
            print "error"
        
        

        self.edges = set()
        self.nodes = set()
        
        self._getEdgesAndNodes()
    
    def printStats(self):
        print len(self.occurrences), "occurrences loaded"
        print "Nodes: ",len(self.nodes)
        print "Edges: ",len(self.edges)
        
    def dumpPKL(self, fpath):
        pickle.dump(self.occurrences,open(fpath,'w')) 
          
    def dumpEdges(self,fpath):
        f = open(fpath,'w')
        for e in self.edges:
            f.write("%s\t%s\t%s\n"%(e[0],e[1],e[2]))
        f.close()
       
    def getTerminals(self,o):
        ret = set()
        for rule in o.derivations:
            if len(rule.split("->"))==1:
                ret.add(rule)
        return ret
    def printOccurrences(self):
        for o in self.occurrences:
            print o.parseScore, o.getNormalizedEdgeScore()
            print o.derivations
            for e in o.edges:
                print ("%s\t%s\t%s"%(e[0],e[1],e[2]))
            print
            for n in o.nodes:
                print "%s\t%s\t%s"%(n[0],n[1],n[2])
    def printOccurrence(self, ind = 0):
        o = self.occurrences[ind]
        print o.parseScore, o.getNormalizedEdgeScore()
        print o.derivations
        for e in o.edges:
            print ("%s\t%s\t%s"%(e[0],e[1],e[2]))
        print
        for n in o.nodes:
            print "%s\t%s"%(n[0],n[1])
    def printEdges(self):
        for e in self.edges:
            print ("%s\t%s\t%s"%(e[0],e[1],e[2]))
    
    def printNodes(self):
        for n in self.nodes:
            print ("%s\t%s"%(n[0],n[1]))
            
    def dumpEdgesPosterior(self,fpath): 
        edgesDict = {}
        totalScore = 0
        for e in self.edges:
            edgesDict[e] = 0
        for o in self.occurrences:
            score = o.getNormalizedEdgeScore()
            totalScore += score
            for e in o.edges:
                edgesDict[e] += score
         
        f = open(fpath,'w')
        keys = edgesDict.keys()
        keys.sort(key=lambda x:edgesDict[x])
        for e in keys:
            f.write("%s\t%s\t%s\t%f\n"%(e[0],e[1],e[2],edgesDict[e]/totalScore))
        f.close()
        
        
    def dumpNodesPosterior(self,fpath): 
        nodesDict = {}
        for n in self.nodes:
            nodesDict[n] = 0
        for o in self.occurrences:
            score = o.getNormalizedEdgeScore()
            for n in o.nodes:
                nodesDict[n] = max(score,nodesDict[n])
         
        keys = nodesDict.keys()
        keys.sort(key = lambda x: nodesDict[x],reverse = True)
        f = open(fpath,'w')
        for n in keys:
            f.write("%s\n"%(n))
            #f.write("%s\t%f\n"%(n,nodesDict[n]))
        f.close()
        
    def TopKEdgeScore(self, k, reverse = True):
        self.occurrences.sort( key=lambda x: x.parseScore, reverse=reverse)
        self.occurrences = self.occurrences[:k]
        self._getEdgesAndNodes()
    
    
    def getMaxVal(self,func = lambda x:x.parseScore):
        self.occurrences.sort( key=lambda x: func(x) , reverse=True)
        if len(self.occurrences)==0:
            return 0,set()
        return func(self.occurrences[0]),self.occurrences[0].nodes
    
    def dumpTopKResults(self, k , opath, seperate = True):
        ofile = open(opath,'w')
        self.occurrences.sort( key=lambda x: str(x.parseScore) + str(x.getNormalizedEdgeScore()), reverse=True)
        
        if not seperate:
            es = set()
            for o in self.occurrences[:k]:
                es = es|o.edges
            for e in es:
                ofile.write("%s\t%s\n"%(e[0],e[2]) )

        if seperate:
            i = 0
            for o in self.occurrences[:k]:
                i+=1
                for e in o.edges:
                    ofile.write("%s\t%s\n"%(e[0]+"-"+str(i),e[2]+"-"+str(i)) )
        ofile.close()
        
    def filterByNodes(self, nodes):
        newset = list()
        for o in self.occurrences:
            if len(nodes&o.nodes)>0:
                newset.append(o)
        self.occurrences = newset
        self._getEdgesAndNodes()
        
    def filterByEdgeScore(self, t):
        newset = list()
        for o in self.occurrences:
            if o.edgeScore >= t:
                newset.append(o)
        self.occurrences = newset
        self._getEdgesAndNodes()
        
    def GOenrich(self, world,ofilepath):
        david = David("smolyi@bgu.ac.il")
        david.loadBackground(world, "uni", "bg")
        david.loadList(self.nodes, "uni", "targets")
        david.DAVIDenrich( listName = "targets",bgName = "bg", outputFilePath = ofilepath)
        MyFileHandler.dumpCon(ofilepath+"-targets.txt", self.nodes)
        MyFileHandler.dumpCon("bg.txt", world)
        
    def NodesFisher(self, checkset, world):
        #print "input:", len(self.nodes&cosmic),len(self.nodes),len(checkset),len(world)
        #print "params:", len(self.nodes&cosmic),len(self.nodes&world-checkset),len(checkset&world-self.nodes),len(world-checkset-self.nodes)
        nodes = set(map(lambda x:x[0],self.nodes))
        return pvalue(len(nodes&checkset),len(nodes&world-checkset),len(checkset&world-nodes),len(world-checkset-nodes))
    
    def getNodesByLabel(self,label):
        nodes = set()
        for o in self.occurrences:
            for n in o.nodes:
                if n[1]==label:
                    nodes.add(n[0])
        return nodes
    
    def getNodeName(self):
        return set(map(lambda x:x[0], self.nodes))
    def IsContainNodeSet(self,nodes, misses = 0):
        s = set()
        for o in self.occurrences:
            if len(nodes&o.nodes) >= len(nodes)-misses:
                s.add(o)
        return s
    
    def EdgesContained(self, edges, world,directed = False):
        if not directed:
            newset = set()
            for e in edges:
                newset.add((e[0],e[1]))
                newset.add((e[1],e[0]))
            edges = newset
            
        s = set()
        for o in self.occurrences:
            oedges = set(filter(lambda x:x[0] in world and x[1] in world, o.edges))
                
            if (len(oedges&edges)) >=  (len(oedges) ) :
                    s.add(o)
        return s
    
    def dumpCytoscape(self, targetPath, label2color, name = "", ind = 0):
        from myGraph import CytoGraph,XGMMLExporter
        
        cg = CytoGraph(name)   
        for e in self.occurrences[ind].edges:
            cg.addEdge( e[0], e[2], e[1], True)
        for n in self.occurrences[ind].nodes:
            cg.addNodeByName(n[0])
            
        for n in self.occurrences[ind].nodes:
            cg.colorNodeByName(n[0], label2color[n[2]])
        XGMMLExporter.XGMMLExporter().Convert( cg, targetPath)
        
        
    def _getEdgesAndNodes(self):
        self.edges  = set()
        self.nodes  = set()
        for o in self.occurrences:
            for e in o.edges:
                self.edges.add(e)
            for n in o.nodes:
                self.nodes.add(n)
       
    def dumpNodes(self,fpath):
        f = open(fpath,'w')
        for n in self.nodes:
            f.write("%s\n"%(n[0]))
        f.close() 
    def translateOccurrences(self, _dict):
        for o in self.occurrences:
            newset = set()
            for item in o.nodes:
                if len(item)==3:
                    gene,context,label = item
                else:
                    gene,context,label = item[0],item[1],item[1]
                if gene in _dict:
                    newgene = _dict[gene]
                    gene = newgene
                newset.add((gene,context,label))
            o.nodes = newset
        
        
            newset = set()
            for e in o.edges:
                gene1 = e[0]
                if e[0] in _dict:
                    gene1 = _dict[e[0]]
                    
                gene2 = e[2]
                if e[2] in _dict:
                    gene2 = _dict[e[2]]
                newset.add((gene1,e[1],gene2))
            o.edges = newset
            
        self._getEdgesAndNodes()
    
    def __iter__(self):
        return iter(self.occurrences)

'''
    def NodesContained(self, nodes, world ):
        s = set()
        for o in self.occurrences:
            #print len(o.nodes & nodes & world),len(o.nodes & world)
            if world and len(o.nodes & nodes & world) >=  len(o.nodes & world)  :
                    #print path, o
                    s.add(o)
            if not world is None and len(nodes&o.nodes) == len(nodes):
                s.add(o)
                
        return s
'''

class ResultsSetHandler(ResultsHandler):
    def __init__(self, pklFilePath):
        ResultsHandler.__init__(self, pklFilePath)
        self.subgraphsDict = {}

        self.__updateSubgraph()
        
        
    def printStats(self):
        ResultsHandler.printStats(self)
        print len(self.subgraphsDict), "non-redundant"
        
        
    def __updateSubgraph(self):
        for o in self.occurrences:
            hashString = self.__edgesAsString(o.edges)
            #hashString = self.__nodesAsString(o.nodes)

            toadd = o
            if hashString in self.subgraphsDict:
                toadd = max(self.subgraphsDict[hashString],toadd, key = lambda x:x.parseScore)
            self.subgraphsDict[hashString] = toadd
       
    def rankOccurrences(self,  func = lambda x:x.parseScore, reverse = True):   
        keys = self.subgraphsDict.keys()
        keys.sort( key=lambda x: func( self.subgraphsDict[x]), reverse=reverse)
        newlist = []
        for key in keys:
            newlist.append(self.subgraphsDict[key])
        self.occurrences = newlist
        self._getEdgesAndNodes()
        self.__updateSubgraph()
        
        
    def TopKEdgeScore(self, k, reverse=True, function = lambda x: x.parseScore):
        keys = self.subgraphsDict.keys()
        keys.sort( key=lambda x: function(self.subgraphsDict[x]), reverse=reverse)

        keys = keys[:k]
        newlist = []
        for key in keys:
            newlist.append(self.subgraphsDict[key])
        self.occurrences = newlist
        self._getEdgesAndNodes()
        self.__updateSubgraph()
        
    def __edgesAsString(self,s):
        l = map(str,s)
        l.sort()
        return ",".join(l)
    
    def __nodesAsString(self,s):
        l = map(lambda x: x[0],s)
        l.sort()
        return ",".join(l)
    
    def __setAsString(self,s):
        l= list(s)
        l.sort()
        return ",".join(l)
    
   