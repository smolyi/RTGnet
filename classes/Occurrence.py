class Occurrence:
    def __init__(self,nodes, derivations, parseScore, edgeScore, edges, score = -1, signature = None):
        self.signature = None
        self.nodes = nodes
        self.edges = edges
        self.derivations = derivations
        self.edgeScore = edgeScore
        self.parseScore = parseScore
        self.score = score
        self.signature = signature
    
    def getScore(self):
        return self.parseScore
    
    def setSubgraph(self,subgraph):
        self.subgraph = subgraph
        
    def __str__(self):
        nodesString = self.__conAsString(self.nodes)
        edgesString = self.__conAsString(self.edges)
        derivationsString = self.__conAsString(self.derivations)
        return "%s\t%s\t%f\t%f\t%s"%( nodesString,edgesString,self.parseScore,self.edgeScore,derivationsString)
    
    def __conAsString(self,tup):
        string = ""
        for item in tup:
            string += str(item)+","
        return string.strip(",")
    
    def getNormalizedEdgeScore(self):
        if len(self.edges)>0:
            return self.edgeScore/len(self.edges)
        return self.edgeScore
    