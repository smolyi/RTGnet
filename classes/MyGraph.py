"""
Author
-----
    Ilan Smoly.  
"""

class Node:
   
    def __init__(self, name):
        """
        A constructor for this class.
        
        Parameter
        ---------
            name : string
                the name from this attribute.
        """
        self.Name = name
        self.IncomingEdges = []
        self.OutgoingEdges = []
        self.attr = {}
        self.__meta = {}
        self.__id = -1
    
    def setID(self,_id):
        self.__id = _id
    def getID(self):
        return self.__id
    def IncomingNodes(self):
        return set(map(lambda x:x.SourceNode,self.IncomingEdges))
    def OutgoingNodes(self):
        return set(map(lambda x:x.TargetNode,self.OutgoingEdges))
    def getHashString(self):
        return "%s"%(self.Name)
    def getInDegree(self,edgeType = None):
        if edgeType:
            return len(filter(lambda x: edgeType==x.getType(), self.IncomingEdges))
        return len(self.IncomingEdges)
    def getOutDegree(self,edgeType = None):
        if edgeType:
            return len(filter(lambda x: edgeType==x.getType(), self.OutgoingEdges))
        return len(self.OutgoingEdges)
    def getDegree(self,edgeType = None):
        return self.getOutDegree(edgeType) + self.getInDegree(edgeType)
    def clone(self):
        n = Node(self.Name)
        for key in self.attr:
            n.setAttribute(key, self.getAttribute(key))
        for key in self.__meta:
            for value in self.getMetaData(key):
                n.addMetaData(key, value)
        return n
    
    #meta data ***************************************************
    def hasMeta(self,key):
        return key in self.__meta
    def hasMetaData(self,key, value):
        if self.hasMeta(key):
            return value in self.__meta[key]
        return False
    def removeMetaKey(self,key):
        self.__meta.pop(key)
    def removeMetaData(self,key, value):
        self.__meta[key].remove(value)
    def addMetaData(self,key,value):
        if not key in self.__meta:
            self.__meta[key] = set()
        self.__meta[key].add(value)
    def getMetaData(self,key):
        if key in self.__meta: return self.__meta[key]
        else: return set()
        
    #attributes **************************************************
    def hasAttribute(self,key):
        return key in self.attr
    def removeAttribute(self,key):
        self.attr.pop(key)
    def addAttribute(self,key,value):
        if key in self.attr:
            raise Exception("key - %s, is already an attribute.")
        self.setAttribute(key, value)
    def setAttribute(self,key,value):
        self.attr[key] = value    
    def getAttribute(self,key):
        if key in self.attr: return self.attr[key]
        else: return None
    
    #sys ****************************************************
    def __eq__(self, other):
        if not isinstance(other, Node): return False
        return self.Name == other.Name
    def __hash__(self):
        return hash("%s"%(self.Name))
    def __str__(self):
        string =  "%s"%(self.Name)
        if len(self.attr)>0:
            meta = "\t"
            keys = self.attr.keys()
            keys.sort()
            for k in keys:
                if type(float())==type(self.attr[k]):
                    meta += "%s:%.10f|"%(k,self.attr[k])
                else:
                    meta += "%s:%s|"%(k,self.attr[k])
            string = string+meta
        return string
    
class Edge:
    
    def __init__(self, sourceNode, targetNode, _type = ""):
        """
        The constructor for this class.
        
        Parameters
        ----------
            sourceNode : Node
                The source node.
            tagetNode : Node
                The target node.
            _type: string. optional.
        """
        self.SourceNode = sourceNode
        self.TargetNode = targetNode
        self.__Type = _type
        self.attr = {}
        self.__meta = {}
        self.__id = -1
    
    def setID(self,_id):
        self.__id = _id
    def getID(self):
        return self.__id
    def getHashString(self):
        return "%s,%s,%s"%(self.SourceNode.getHashString(), self.TargetNode.getHashString(),self.__Type)
    def getType(self):
        return self.__Type
    def setType(self,_type):
        self.__Type = _type
    def isType(self,_type):
        return self.__Type==_type
    def clone(self):
        e = Edge(self.SourceNode.clone(),self.TargetNode.clone(),self.getType())
        for key in self.attr:
            e.setAttribute(key, self.getAttribute(key))
        for key in self.__meta:
            for value in self.getMetaData(key):
                e.addMetaData(key, value)
        return e
    
    #meta data ***************************************************
    def hasMeta(self,key):
        return key in self.__meta
    def removeMetaKey(self,key):
        self.__meta.pop(key)
    def removeMetaData(self,key, value):
        self.__meta[key].remove(value)
    def addMetaData(self,key,value):
        if not key in self.__meta:
            self.__meta[key] = set()
        self.__meta[key].add(value)
    def getMetaData(self,key):
        if key in self.__meta: 
            return self.__meta[key]
        else: return set()
        
    #attributes ***************************************************
    def hasAttribute(self,key):
        return key in self.attr
    def removeAttribute(self,key):
        self.attr.pop(key)
    def setAttribute(self,key,value):
        self.attr[key] = value
    def getAttribute(self,key):
        if key in self.attr: return self.attr[key]
        else: return None
        
    #sys **********************************************************
    def __hash__(self):
        return hash(self.getHashString())
    def __eq__(self, other):
        if not isinstance(other, Edge): return False
        return self.getHashString() == other.getHashString()
    def __str__(self):
        return "%s\t%s\t%s"%(self.SourceNode.getHashString(), self.TargetNode.getHashString(),self.__Type) 
         

class Graph:
    
    def __init__(self, name = ""):
        self.Nodes = {}
        self.Edges = {}
        self.Name = name
        
        self.__nextAllocatedEdgeID = 1
        self.__nextAllocatedNodeID = 1
    
    def translate(self,_dict = None, dictpath = None, eliminate_false = False):
        import pickle
        if not _dict and dictpath:
            _dict = pickle.load(open(dictpath))
            
        int_missed = [0,0]
        for edge in self.edges():
            int1 = edge.SourceNode.Name
            int2 = edge.TargetNode.Name
            set1 = set()
            set2 = set()
            if _dict.has_key(edge.SourceNode.Name):  
                set1 = _dict[int1]
            else:
                int_missed[0] += 1
                if not eliminate_false : 
                    set1.add(int1)
                    
            if _dict.has_key(int2):  
                set2 = _dict[int2]
            else:
                int_missed[1] += 1
                if not eliminate_false : 
                    set2.add(int2)
            
            self.__removeEdge(edge)    
            for i1 in set1:
                for i2 in set2:
                    newedge = edge.clone()
                    newedge.SourceNode.Name = i1
                    newedge.TargetNode.Name = i2
                    self._addEdge(newedge)
            
        return int_missed
    def getNodesMetaAsSet(self,key):
        ans = set()
        for node in self.nodes():
            ans = ans | node.getMetaData(key)
        return ans
    def getNodesByAttributes(self,attr,value):
        ans = []
        for node in self.nodes():
            if node.hasAttribute( attr) and node.getAttribute(attr)==value:
                ans.append(node)
        return ans
    
    def getNodesByMetaValues(self,key,value):
        ans = []
        for node in self.nodes():
            if node.hasMetaData(key,value):
                ans.append(node)
        return ans
    
    def getNodesByMeta(self,key):
        ans = []
        for node in self.nodes():
            if node.hasMeta(key):
                ans.append(node)
        return ans
    
    def setNodeMetaByFunction(self,key,value,function):
        for node in self.nodes():
            if function(node):
                node.addMetaData( key, value)
                
    def setMetaByList(self,ids, key, value):
        count = 0
        for node in self.nodes():
            if node.Name in ids:
                node.addMetaData( key, value)
                count += 1
        return count
    
    def setMetaToInteractorsByList(self,ids_list, key, value):
        interactors = []
        for ids in ids_list:
            tmp = set()
            for nodeName in ids:
                for neighbor in self.getNeighbors(nodeName):
                    tmp.add(neighbor)
            interactors.append(tmp)
            
        intersection = set(interactors[0])
        for item in interactors:
            intersection = intersection & item
        for node in intersection:
            node.addMetaData( key, value)
            
        return len(intersection)
    
    def loadValuesAttributesFile(self,inputFilePath, attr, delim = "\t"):
        f = open(inputFilePath)
        for line in f:
            line = line.strip("\n")
            tokens = line.split(delim)
            nodehash = Node(tokens[0]).getHashString()
            if nodehash in self.Nodes:
                self.Nodes[nodehash].setAttribute(attr,tokens[1])
                
    def loadValuesMetaFile(self,inputFilePath, key, keyInd = 0, valInd = 1,delim = "\t", valueEditFunction = lambda x:x):
        count = 0
        f = open(inputFilePath)
        for line in f:
            line = line.strip("\n")
            tokens = line.split(delim)
            nodehash = Node(tokens[keyInd]).getHashString()
            if nodehash in self.Nodes:
                self.Nodes[nodehash].addMetaData(key,valueEditFunction(tokens[valInd]))
                count += 1
        return count
    
    def loadAttributesFile(self,inputFilePath, attr, value):
        f = open(inputFilePath)
        for line in f:
            line = line.strip("\n")
            nodehash = Node(line).getHashString()
            if nodehash in self.Nodes:
                self.Nodes[nodehash].setAttribute(attr,value)
        f.close()
        
    def loadMetadataFile(self,inputFilePath, key, value, valueEditFunction = lambda x:x):
        f = open(inputFilePath)
        for line in f:
            line = line.strip("\n")
            nodehash = Node(line).getHashString()
            if nodehash in self.Nodes:
                self.Nodes[nodehash].addMetaData(key,valueEditFunction(value))
        f.close()
    
    def setMetaByFunction(self,key,value,function):
        count = 0
        for node in self.nodes():
            if function(node):
                node.addMetaData( key, value)
                count+=1
        return count
    def setMetaToAllNodes(self, key, value):
        for node in self.nodes():
            node.addMetaData( key, value)
    def setMetaToAllEdges(self, key, value):
        for edge in self.edges():
            edge.addMetaData( key, value)
    def setAttributeToAllEdges(self,key,val):
        for e in self.edges():
            e.setAttribute(key,val)
    def setAttributeToAllNodes(self,key,val):
        for n in self.nodes():
            n.setAttribute(key,val)
    
    def importGraph(self, otherGraph, overrideAttributes = False):
        """
        import another graph into this graph.
        
        nodes:
            1) importing clones of all nodes that do not appear in this graph (including their attributes).
            2) if a node is already in the graph, will import only attributes.
        
        edges:
            1) for each edge that do not appear in this graph creates a new edge in this graph bases on the nodes names and import it's attributes.
            2) if a edge is already in the graph, will import only attributes.
            
        parameter
        ---------
            otherGraph. Graph.
            overrideAttributes. boolean. optional - default = False
                True - override existing attributes.
        """
        for n in otherGraph.nodes():
            newNode = n.clone()
            if not self._addNode(newNode):
                nodeObj = self.Nodes[newNode.getHashString()]
                for key in newNode.attr:
                    if not nodeObj.hasAttribute(key) or overrideAttributes:
                        nodeObj.setAttribute(key,newNode.getAttribute(key))
                        
        for e in otherGraph.edges():
            self.addEdge(e.SourceNode.Name, e.TargetNode.Name, e.getType())
            
            edgeObj = self.Edges[e.getHashString()]
            for key in e.attr:
                if not edgeObj.hasAttribute(key) or overrideAttributes:
                    edgeObj.setAttribute(key,e.getAttribute(key))
                    
        
    def addEdge(self, sourceName, targetName, _type, directed = True):
        """
        This method will add the nodes and an edge to the graph.
        
        Parameters
        ----------
            sourceName : string
                the name of the source node.
            targetName : string
                The name of the target node.
            _type : string
             __Typehe edge Type.
            directed :  boolean
                whether the edge is direcred or not.
        """
        sourceNode = self.addNodeByName(sourceName)
        targetNode = self.addNodeByName(targetName)
        
        
        edge = Edge(sourceNode, targetNode, _type)
        self._addEdge(edge)
        
        if  not directed:
            revEdge = Edge(targetNode, sourceNode,_type)
            self._addEdge(revEdge)
        
        return 
    
    def reduceGraph(self, nodesNamesSet, neighborhood = 0, directed = False):
        """
        """
        newGraph = Graph()
        for nodeName in nodesNamesSet:
                newGraph.addNodeByName(nodeName)
        while neighborhood >= 1:
            newSet = set()
            for nodeName in nodesNamesSet:
                node = Node(nodeName).getHashString()
                if not node in self.Nodes:
                    continue
                oldNode = self.Nodes[node]
                l = oldNode.OutgoingEdges
                if not directed:
                    l +=  oldNode.IncomingEdges    
                for edge in l:
                    if not newGraph.isNode(edge.TargetNode.Name):
                        newSet.add(edge.TargetNode.Name)
                    newEdge = edge.clone()
                    newGraph._addEdge(newEdge)
            nodesNamesSet = newSet
            neighborhood -= 1
        return newGraph
         
    def addNodeByName(self, node_name):
        tmp_dict = self.Nodes
        node = Node(node_name)
        self._addNode(node)
        return tmp_dict[node.getHashString()]
    
    def removeNodeByName(self,nodeName):
        node = Node(nodeName)
        return self.__removeNode(node)
    
    def removeNodes(self,names):
        c=0
        for name in names:
            if self.removeNodeByName(name):
                c+=1
        self.__reallocateIDs()
        return c
        
    def loadEdgesFile(self,inputFilePath, ind = [0,1], edgesType = "",directed = 0, delim = "\t", startFromLine = 0, attributes = {}):
        """
        adds the edges in the file to the graph.
        assign edgeType to the edges.
        file should be in the following format:
        sourceNode\ttargetNode\n
        """
        f = open(inputFilePath,'r')
        line = f.readline()
        lineCounter = 0
        while len(line)>0:
            if lineCounter < startFromLine:
                line = f.readline()
                lineCounter += 1
                continue
            line = line.split("\n")[0]
            tokens = line.split(delim)
            int1, int2 = tokens[ind[0]], tokens[ind[1]]
            
            e = Edge(Node(int1), Node(int2), edgesType)
            for index in attributes:
                if len(tokens) > index:
                    e.setAttribute( attributes[index][0], attributes[index][1](tokens[index]))
            self._addEdge(e)
            
            if not directed:
                e = Edge(Node(int2), Node(int1), edgesType)
                for index in attributes:
                    if len(tokens) > index:
                        e.setAttribute( attributes[index][0], attributes[index][1](tokens[index]))
                self._addEdge(e)
            line = f.readline()
            lineCounter += 1
        f.close() 
        
    def dumpEdgeFile(self,ouptutFilePath,delim = "\t",hashedNodes = False, attributes = [],meta = []): 
        """
        dumps the edges to a file.
        the output file in following format:
        sourceNode\ttargetNode\tedgeType\n
        
        Parameters
        ---------
            edgeType. string. optional.
                assign a general type to the edges. if not specified the individual edge type will be assigned.
            hashNodes. boolean. optional.
                True - to dump the node's hash strings. False - dumps nodes names.
        """   
        f = open(ouptutFilePath,'w')
        for e in self.Edges.values():
            if hashedNodes: source = e.SourceNode.getHashString() 
            else: source = e.SourceNode.Name
            if hashedNodes: target = e.TargetNode.getHashString() 
            else: target = e.TargetNode.Name
            
            _type  = e.getType()
            toprint = "%s\t%s\t%s"%(source, target, _type)
            for attr in attributes: 
                toprint += "\t%s"%e.getAttribute(attr)
            for met in meta: 
                toprint += "\t%s"%e.getMetaData(met)
            f.write(toprint+"\n")
        f.close() 
        
        
    def removeHubs(self,p = 0.05):
        degrees = map(lambda x: x.getDegree(),  self.nodes())
        degrees.sort(reverse = True)
        ind = int (p*len(degrees) ) - 1

        maxDegree = degrees[ind]
        #print "maxDegree",maxDegree,ind,degrees
        return self.filterNodesByDegree(maxDegree)
         
    
    def filterNodesByDegree(self,deg):
        c = 0
        for n in self.nodes():
            if n.getDegree() >= deg:
                self.removeNodeByName(n.Name) 
                c+=1
        self.__reallocateIDs()
        return c
    
    def getNeighborsByList(self, nodeNames):
        s = set()
        for n in nodeNames:
            s = s | set(map(lambda x:x.Name, self.getNeighbors(n)))
        return s
    def getNeighbors(self, nodeName,incoming = False):
        try:
            node = self.getNodeByName(nodeName)
            if incoming:
                return node.IncomingNodes()
            return node.OutgoingNodes()
        except:
            return []
    
    def areNeighbors(self,node1,node2):
        """
        returns
        -------
            (bool,bool) - (node2 => node1 , node1 => node2) 
        """
        try:
            node1 = self.getNodeByName(node1)
            node2 = self.getNodeByName(node2)
            return node2 in node1.IncomingNodes(), node2 in  node1.OutgoingNodes()
        except:
            return False,False
    
    def getEdgeAttribute(self, int1, int2, attr, edgeType = None):
        e = Edge(Node(int1), Node(int2),edgeType)
        hashString = e.getHashString()
        if hashString in self.Edges:
            e = self.Edges[hashString]
            if e.hasAttribute(attr):
                return e.getAttribute(attr)
        return None
    
    def getEdge(self, node1, node2, edgeType = None):
        e = Edge(node1, node2, edgeType)
        hashString = e.getHashString()
        if hashString in self.Edges:
            return self.Edges[hashString]
        return None
 
    def setEdgeMetaByType(self, edgeType, key, value):
        for edge in self.edges():
            if edge.getType() == edgeType:
                edge.addMetaData(key, value)
                
    def setEdgeMetaByNodesNames(self,sourceNode, targetNode, key, value, _type = None):
        e = self._getEdge(sourceNode, targetNode, _type)          
        if e:
            e.addMetaData(key, value)
            return True
        return False
    def getEdgeTypes(self,int1,int2,reversible = False): 
        l = []
        node1 = self.getNodeByName(int1)
        for edge in node1.OutgoingEdges:
            if edge.TargetNode.Name == int2:
                l.append(edge.getType())
        if reversible:
            for edge in node1.IncomingEdges:
                if edge.SourceNode.Name == int2:
                    l.append(edge.getType())
        return l
       
    def getNodeDegree(self,nodeName, edgeType = None):
        n = Node(nodeName)
        if n.getHashString() in self.Nodes:
            nObj =  self.Nodes[n.getHashString()]
            return nObj.getInDegree(edgeType),nObj.getOutDegree(edgeType)
        else:
            return [0,0]
        
    def contains(self, sourceName, targetName,edgeType):
        e = Edge(sourceName, targetName,edgeType)
        return e.getHashString() in self.Edges
    def edges(self):
        return self.Edges.values()
    def nodes(self):
        return self.Nodes.values()
    def numberOfEdges(self):
        return len(self.edges())
    def numberOfNodes(self):
        return len(self.nodes()) 
    def isNode(self,name):
        n = Node(name)
        return n.getHashString() in self.Nodes  
    
    def _getEdge(self, int1, int2, _type):
        tmpEdge = Edge(Node(int1), Node(int2), _type)
        if tmpEdge.getHashString() in  self.Edges:
            return self.Edges[tmpEdge.getHashString()]
        raise Exception(str((int1, int2, _type))+ " not in graph.")
    
    def getNodeByName(self,name):
        tmpNode = Node(name)
        if tmpNode.getHashString() in  self.Nodes:
            return self.Nodes[tmpNode.getHashString()]
        raise Exception(name+ " not in graph.")
    
    def _addNode(self,node):
        if not self.Nodes.has_key(node.getHashString()):
            self.Nodes[node.getHashString()] = node
            self.__allocateNodeID(node)
        return self.Nodes[node.getHashString()]
  
    def _addEdge(self, edge,attrFunc = lambda x,y: max([abs(x),abs(y)])):
        edge.SourceNode = self._addNode(edge.SourceNode)
        edge.TargetNode = self._addNode(edge.TargetNode)

        if not self.Edges.has_key(edge.getHashString()):
            self.Edges[edge.getHashString()] = edge
            self.__allocateEdgeID(edge)
            edge.SourceNode.OutgoingEdges.append(edge)
            edge.TargetNode.IncomingEdges.append(edge)  
            return True
        else:
            e = self.Edges[edge.getHashString()]
            for attr in edge.attr:
                if attr in e.attr:
                    e.setAttribute(attr,attrFunc(e.getAttribute(attr),edge.getAttribute(attr)))
                else:
                    e.setAttribute(attr,edge.getAttribute(attr))
        return False
    
    def __allocateEdgeID(self,edge):
        edge.setID(self.__nextAllocatedEdgeID)
        self.__nextAllocatedEdgeID += 1
    
    def __allocateNodeID(self,node):
        node.setID(self.__nextAllocatedNodeID)
        self.__nextAllocatedNodeID += 1
    
    def __reallocateIDs(self):
        self.__nextAllocatedNodeID = 0
        for n in self.nodes():
            self.__allocateNodeID(n)
            
        self.__nextAllocatedEdgeID = 0
        for e in self.edges():
            self.__allocateEdgeID(e)
        
    def __removeEdge(self, edge):
        """
        This method will remove an edge from the graph. If unconnected nodes remain it will delete them as well.
        
        Parameters
        ----------
            edge : Edge
                The edge to remove.
        """
        if not isinstance(edge, Edge):
            raise Exception("Edge instance is expected! %s is given."%edge.__class__())
        
        if self.Edges.has_key(edge.getHashString()):
            edgeObj = self.Edges[edge.getHashString()]
            
            edgeObj.SourceNode.OutgoingEdges.remove(edgeObj)
            if edgeObj.SourceNode.getDegree()==0 : 
                self.Nodes.pop(edgeObj.SourceNode.getHashString())

            edgeObj.TargetNode.IncomingEdges.remove(edgeObj)
            if edgeObj.TargetNode.getDegree()==0 : 
                self.Nodes.pop(edgeObj.TargetNode.getHashString())
                
            self.Edges.pop(edge.getHashString())
            return True
        return False
                    
    def __removeNode(self, node):
        """
        This method will remove a node from the graph and all of the edges it appears in.
        
        Parameters
        ----------
            node : Node
                The node to remove.
        """
        if not isinstance(node, Node):
            raise Exception("Node instance is expected! %s is given."%node.__class__())
        
        if self.Nodes.has_key(node.getHashString()):
            nodeObj = self.Nodes[node.getHashString()]
            edgesToRemove = nodeObj.IncomingEdges + nodeObj.OutgoingEdges
            for edge in edgesToRemove:
                if not self.__removeEdge(edge): 
                    continue #raise Exception("error while removing edge - %s"%edge)
            #self.Nodes.pop(node.getHashString())
            return True
        return False
    
    def __len__(self):
        return len(self.Edges)
'''
graph = Graph()
graph.loadEdgesFile("/home/skuper/workspace/SubpathQuery/data/interactions/yeast/yeast-genes.txt", edgesType = "1", directed = False, delim = "\t",attributes={2:("score",float)})
#print graph.getEdgeAttribute("HAL5", "PAH1", attr = "score", edgeType="1")
graph.loadMetadataFile("/home/skuper/workspace/SubpathQuery/data/genes/yeast/tfs", "label", "tf")
graph.loadMetadataFile("/home/skuper/workspace/SubpathQuery/data/genes/yeast/phospho", "label", "phospho")
s = ["PRS1"]
graph1 = graph.reduceGraph(s, 1)
graph2 = graph.reduceGraph(s, 2)
print len(graph.Nodes),len(graph1.Nodes),len(graph2.Nodes)

for n in graph1.edges():
    print n
'''

