
class GraphPreprocessor:
    def __init__(self, graph, maxLength):
        self.graph = graph
        self.maxLength = maxLength
        
    def run(self):
        nodes = self.graph.nodes()
        numberOfNode = len(nodes)
        dijkstra = self.dijkstra
        
        
        ans = [[0 for i in range(self.maxLength+1)] for j in range(numberOfNode+1)]
        count = 0
        percentile = 10
        
        
        for node in nodes:
            nodeID = node.getID()
            
            count += 1
            if count*100/numberOfNode > percentile:
                print str(percentile)+"%"
                percentile = percentile + 10 
                
            res = dijkstra(node)
            for k in range(len(res)):
                listOfNodes = res[k]
                prev = 0
                if k > 0:
                    prev = ans[nodeID][k-1]
                if listOfNodes:
                    ans[nodeID][k] = max( prev , max(listOfNodes.values()))
                
        return ans
             
    def dijkstra(self,startNode):  
        dist = [None]*(self.maxLength+1)
        
        dist[0] = {}
        dist[0][startNode] = 0     
                                                        
        for k in range(self.maxLength):
            nextDist = {}
            curDist = dist[k]
            for node in curDist:
                sourceScore = curDist[node]
                for edge in node.OutgoingEdges:
                    targetNode = edge.TargetNode
                    edgeScore = edge.getAttribute("score")
                    if not targetNode in nextDist:
                        nextDist[targetNode] = 0
                    nextDist[targetNode] =  max(nextDist[targetNode],sourceScore + edgeScore)
                for edge in node.IncomingEdges:
                    sourceNode = edge.SourceNode
                    edgeScore = edge.getAttribute("score")
                    if not sourceNode in nextDist:
                        nextDist[sourceNode] = 0
                    nextDist[sourceNode] =  max(nextDist[sourceNode],sourceScore + edgeScore)
            dist[k+1] = nextDist

        return dist

