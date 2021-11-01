from bitarray import bitarray 
from classes.Hypergraph import HypernodeCC,Hyperedge
from classes.kbest import Kbest
from classes.Occurrence import Occurrence

import random, numpy, pickle, datetime
from classes.kbest import kbestElement


class HypernodesContainer:
    def __init__(self, m, n):
        self.numberOfnodes = n
        self.maximum = m
        self.__container = []
        self.__NodeArray = []
        self.iterator = []
        self.__size = 0
        self.init()

    def init(self):
        self.__container = []
        self.__NodeArray = []
        for i in range(self.maximum+1):
            self.__container.append([])
        for i in range(self.numberOfnodes+1):
            self.__NodeArray.append([])
        self.iterator = []
        
    def get(self,rootnodeID, context, colorCoding):
        nodelist = self.__NodeArray[rootnodeID]
        ans = None
        for item in nodelist:
            if item.context == context and item.colorCoding == colorCoding:
                ans = item
                break
        
        return ans

    def put(self, rootnode, context, colorCoding ):
        found = self.get(rootnode.getID(), context, colorCoding)
        if found:
            return found
        
        toadd = HypernodeCC(rootnode, context, colorCoding)
        nodelist = self.__NodeArray[rootnode.getID()]
        nodelist.append(toadd)  
        self.__container[toadd.length].append(toadd)
        self.iterator.append(toadd)
        self.__increaseSize()
            
        return toadd
 
    def remove(self,hypernode):
        nodelist = self.__NodeArray[hypernode.rootNode.getID()]
        for item in nodelist:
            if item == hypernode:
                nodelist.remove(item)
                self.__decreaseSize()
                return True
        return False
    
    def __iter__(self):
        return iter(self.iterator)
        
    def __str__(self):
        string = ""
        for i in range(len(self.__container)):
            
            if self.__container[i]:
                string += "(%d):"%(i)
                for item in self.__container[i]:
                    string += str(item)
                string += "\n"
        return string
    
    def __len__(self):
        return len(self.iterator)
    def __increaseSize(self):
        self.__size += 1
    def __decreaseSize(self):
        self.__size -= 1
    def __stateHash(self, context, colorCoding):
        return "%s,%s"%(context,str(colorCoding))
    def getListForRootnode(self,nodeid):
        return self.__NodeArray[nodeid]
    def getListForLength(self,length):
        return self.__container[length]          
      
class RTGparser:
    def __init__(self,
                 graph, 
                 grammar, 
                 k, 
                 maxLength, 
                 scoreThreshold, 
                 scoringScheme = 0 ,
                 parseScoreAlphaDict = None,
                 pathScoreAlphaDict = None,
                 
                 ):
        self.graph = graph
        self.grammar = grammar
        self.maxLength = maxLength
        self.numberOfColors = maxLength+1
        self.k = k
        

        
        self.scoreThreshold = scoreThreshold
        self.parseScoreAlphaDict = parseScoreAlphaDict 
        #self.pathScoreAlphaDict = pathScoreAlphaDict
        print "params:"
        print "maxLength = ", self.maxLength
        print "scoreThreshold = ", self.scoreThreshold
        print "k = ", self.k
        print "numberOfColors = ", self.numberOfColors
        print "parseScoreAlphaDict:", self.parseScoreAlphaDict
        
        def edgeScoreSum(leftHypernode,rightHypernode,gScore, eScore):
            return leftHypernode.score + rightHypernode.score + eScore
        def edgeScoreAverage(leftHypernode,rightHypernode,gScore, eScore):
            newscore = (leftHypernode.length-1)*leftHypernode.score + (rightHypernode.length-1)*rightHypernode.score + eScore
            return float(newscore)/(leftHypernode.length + rightHypernode.length - 1)
        def grammarScoreSum(leftHypernode,rightHypernode,gScore, eScore):
            return leftHypernode.score + rightHypernode.score + gScore
                        
        self.scoringScheme = { 1: (edgeScoreSum,"edgeScoreSum"),
                  2: ( edgeScoreAverage,"edgeScoreAverage" ) ,
                   3 : ( grammarScoreSum , "grammarScoreSum")
                   }[scoringScheme]
        print "scoringScheme = ", self.scoringScheme[1]

        
    def Query(self, pklFilePath, epsilon = 0.05, debug = False):
        import math
        numberOfExecutions = int(math.log(1/epsilon) * math.exp(self.maxLength)) 
        print "numberOfExecutions=",numberOfExecutions
        
        numberOfNodes = len(self.graph.nodes())
        hypernodesCon = HypernodesContainer( self.maxLength+1, numberOfNodes+1)
        
        
        total = 0
        ans = {}
        for i in range(numberOfExecutions):
            start = datetime.datetime.now()
            print "execution",i
            hypernodesCon.init()
            res = self.QueryCC(hypernodesCon,debug)
            total += len(res)
            print len(res), "occurrences found"
            print total, "occurrences total"
            
            for occ in res:
                hashing = occ[0].signature.hash()
                toadd = occ
                if hashing in ans and toadd[1].getScore() < ans[hashing][1].getScore():
                    toadd = ans[hashing]
                ans[hashing] = toadd
            print len(ans), "unique occurrences total"
            
            occurrences = ans.values()
            occurrences.sort(key = lambda x:x[0].score,reverse = True)
            occurrences = occurrences[:self.k]
            
            print  "dumping pathways to [%s]"%(pklFilePath)
            f = open(pklFilePath,'w')
            pickle.dump(map (lambda x:x[1],occurrences),f)
            f.close()
            
            if len(occurrences) > 0:
                self.scoreThreshold = max(self.scoreThreshold, occurrences[min(self.k,len(occurrences)-1)][0].score )
                print "parse-score threshold update: %f"% self.scoreThreshold
            print "iteration running-time: ", datetime.datetime.now() - start
        return ans
            
        
    def QueryCC(self, hypernodesCon, debug = False): 
        def printColorsCount():
            color = [0 for i in range(self.maxLength+1)] 
            for n in self.graph.nodes():
                c = n.getAttribute("color")
                color[c]+=1
            print color

        def forceColors():
            self.graph.getNodeByName("P13501").setAttribute("color",0)

        def colorGraph():
            for n in self.graph.nodes():
                color = int(random.randint(0,self.numberOfColors-1))
                n.setAttribute("color",color)
                       
        def getColorCodingForNode(node):
            color = node.getAttribute("color")
            bits = bitarray(self.numberOfColors)
            bits.setall(False)
            bits[color] = True
            return bits
            
        def removeState(state):
            hypernodesCon.remove(state)
            #if state in currentStates:
            #    currentStates.remove(state)
                      
        def examination(leftHypernode, rightHypernode, edgeObject,direction = ""):
            b = bitarray(self.numberOfColors)
            b.setall(False)
            
            if leftHypernode != rightHypernode and leftHypernode.colorCoding & rightHypernode.colorCoding == b: 
                eScore = edgeObject.getAttribute("score")   
                #for Q,gScore in self.grammar.getProductions((leftHypernode.context,rightHypernode.context)):
                for Q,gScore in self.grammar.getInverseProduction((leftHypernode.context,rightHypernode.context)):
                    colorCoding = leftHypernode.colorCoding | rightHypernode.colorCoding
                    head = hypernodesCon.put(leftHypernode.rootNode, Q, colorCoding)
                    newscore = self.scoringScheme[0]( leftHypernode, rightHypernode,gScore, eScore )
                    he = Hyperedge(head,leftHypernode,rightHypernode,gScore,eScore,edgeObject, (Q,leftHypernode.context,rightHypernode.context))
                    head.updateScore(newscore,)
                    ke = kbestElement(head,  he.left, he.right, 0, 0, he.edgeScore, he.grammarScore)
                    ke.score = 0
                    
                    head.kbest.append((ke.score,ke))
                    head.backstar.append(he)
                        
                
                #for edgeLabel in edgeObject.getMetaData("label"): 
                    #edgeLabeldirected = direction+edgeLabel
                    #edge = (edgeObject.SourceNode.Name,edgeLabel,edgeObject.TargetNode.Name)
            
                        #derivation = "%s->%s"%(Q,(leftHypernode.context,edgeLabeldirected,rightHypernode.context))
                        #hyperedge = HyperEdge(None, leftHypernode, rightHypernode, score, edgeScore, edge, derivation)
                        #self.kbest.mergeHyperNodes(newstate, leftHypernode, rightHypernode, hyperedge)
            
        colorGraph()        
        
        #initialization
        nodelabels = set()
        labels = set()
        for node in self.graph.nodes():
            for label in node.getMetaData("label"):
                nodelabels.add(label)
                for prod in self.grammar.getInverseProduction((label,)):
                    newHypernode = hypernodesCon.put(node, prod[0], getColorCodingForNode(node))
                    #newHypernode.updateScore( float(prod[1]))
                    newHypernode.updateScore( 0)

                    ke = kbestElement(newHypernode, None, None, 0, 0, 0, 0)
                    ke.score = 0
                    newHypernode.kbest.append( (ke.score,ke) ) 
                    labels.add(label)
        
        print "labels: ",labels
        print "nodelabels: ",nodelabels
        counter = 0
        
        #main loop
        for iteration in range (1,self.maxLength+2):
            print "(%d)"%iteration,
            examinations = 0
            #examinationsSet = set()
            
            currentStates = hypernodesCon.getListForLength(iteration)
            print  "%d states created. total of %d states."%(len(currentStates),len(hypernodesCon))
            
            
            for s1 in currentStates:
                for edgeObject in s1.rootNode.OutgoingEdges:
                    targetnode = edgeObject.TargetNode
                    neighboringHypernodes = hypernodesCon.getListForRootnode(targetnode.getID())
                    for s2 in neighboringHypernodes:
                        if s2.length <= s1.length:
                            examination(s1,s2,edgeObject)
                            examination(s2,s1,edgeObject)
                            examinations += 1 
                        #toadd = (s1.rootNode.Name,s1.context,s2.rootNode.Name,s2.context)
                        #if toadd in examinationsSet:
                        #    print toadd,str(s1.colorCoding) ,str(s2.colorCoding)
                        #examinationsSet.add(toadd)
                
            print "number of hypernodes examinations", (examinations)        
            #print "number of unique examinations", len(examinationsSet)        
            print "counter",counter

            toRemove = set()
            debug = False
            FUNCTION = self.scoringScheme[1]
            if FUNCTION == "edgeScoreAverage":
                print "pruning ...",
                maxScore = 1
                for hypernode in hypernodesCon:
                    if  hypernode.length <= iteration:
                        edgesNum = hypernode.length-1 
                        bestElement = hypernode.kbest[0][1]
                        merit = float(hypernode.score * edgesNum + maxScore * (self.maxLength-edgesNum) )/self.maxLength
                        if  merit < self.scoreThreshold:
                            toRemove.add(hypernode)
                        if debug:
                            print hypernode, "merit",merit
                           
            if FUNCTION == "edgeScoreSum":
                print "pruning ..."
                maxScore = 1
                for hypernode in hypernodesCon:
                    if  hypernode.length <= iteration:
                        edgesNum = hypernode.length-1 
                        bestElement = hypernode.kbest[0][1]
                        merit = bestElement.score + maxScore * (self.maxLength-edgesNum) 
                        if  merit < self.scoreThreshold:
                            toRemove.add(hypernode)
                            if debug:
                                print hypernode, "merit",merit
                                  
            if FUNCTION == "grammarScoreSum":
                print "pruning ..."

                for hypernode in hypernodesCon:
                    if  hypernode.length <= iteration:
                        bestElement = hypernode.kbest[0][1]
                        parseAlpha = self.parseScoreAlphaDict[(hypernode.context , hypernode.length)]
                        if bestElement.score + parseAlpha < self.scoreThreshold:
                            toRemove.add(hypernode)
                
            print "deleting %d hypernodes ... "%(len(toRemove)),
            for s in toRemove:
                removeState(s)    
            print "deleted. "
           
             
            
            if debug:
                print hypernodesCon 
                   
        print
         
            

        #parsing results
        optimalHypernode = None,-1
        for state in hypernodesCon:
            if state.context == self.grammar.initialContext and state.score > optimalHypernode[1]:
                optimalHypernode = state, state.score
        
        self.computeKbest(hypernodesCon.iterator )
        allkbests = []
        for hn in hypernodesCon.iterator:
            if hn.context == self.grammar.initialContext :
                allkbests += map(lambda x:x[1], hn.kbest)
        allkbests.sort(key=lambda x:x.score, reverse=True)
        ans = map(lambda x: ( x, self.parseKbest(x)) , allkbests[:self.k])
               
        if len(hypernodesCon)>0: 
            print "max score",numpy.max(map(lambda x:x.kbest[0][1].score,hypernodesCon))   
        
        '''
        if optimalHypernode[0]:
            ret = self.parseOptimalSolution(optimalHypernode[0])   
            res.append(ret)  
        '''
        print "number of paths found - ",len(ans) 
        return ans
    
    def computeKbest(self, hypernodes):
        kbest = Kbest( self.k, self.scoringScheme[0] )
        hypernodes.sort( key = lambda x: x.length )
        for hn in hypernodes:
            if hn.length>1:
                kbest.findKbestAlg2( hn )

            
    def parseOptimalSolution(self, hypernode):
        if  len(hypernode.backstar)==0:
            o = Occurrence(set([(hypernode.rootNode.Name,hypernode.context)]), [], hypernode.score, 0, [])
            return o
         
        leftTail = hypernode.backstar[0].left   
        rightTail = hypernode.backstar[0].right   
        production = hypernode.context,leftTail.context,rightTail.context
        edge = leftTail.rootNode.Name,rightTail.rootNode.Name
        
         
        t1 = self.parseOptimalSolution(leftTail)
        t2 = self.parseOptimalSolution(rightTail)
              
        newedgescore = 0 #p1.edgeScore + p2.edgeScore + edgescore
        newparseScore = 0 #p1.parseScore + p2.parseScore + parseScore
        nodes = t1.nodes | t2.nodes
        rules = [production] + t1.derivations + t2.derivations
        edges = t1.edges + [edge] + t2.edges
        
        o = Occurrence(nodes, rules, newparseScore, newedgescore, edges)
        return o
    
    def parseKbest(self, ke):
        if  not ke.right:
            o = Occurrence(set([(ke.hypernode.rootNode.Name,ke.hypernode.context)]), [], ke.hypernode.score, 0, [])
            return o
         
        production = ke.hypernode.context,ke.left.context,ke.right.context
        edge = ke.left.rootNode.Name,ke.right.rootNode.Name
        
         
        t1 = self.parseKbest(ke.left.kbest[ke.leftInd][1])
        t2 = self.parseKbest(ke.right.kbest[ke.rightInd][1])
              
        newedgescore = 0 #p1.edgeScore + p2.edgeScore + edgescore
        newparseScore = 0 #p1.parseScore + p2.parseScore + parseScore
        nodes = t1.nodes | t2.nodes
        rules = [production] + t1.derivations + t2.derivations
        edges = t1.edges + [edge] + t2.edges
        
        o = Occurrence(nodes, rules, newparseScore, newedgescore, edges, ke.score, ke.signature)
        return o    
  
