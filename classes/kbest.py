import heapq

class Signature:
    def __init__(self, root):
        self.root = root
        self.__childs = []
    def merge(self,other):
        ret = Signature(self.root)
        ret.__childs = self.__childs + [other.hash(),]
        ret.__childs.sort()
        #ret.appendChild(other.hash())
        return ret
    def appendChild(self,child):
        _childs = self.__childs
        i = 0
        for c in _childs:
            if child < c:
                break
        self.__childs = _childs[:i] + [child] + _childs[i:]
    def hash(self):
        childs = ",".join(self.__childs)
        return "(%s,%s)"%(self.root,childs)
    
class kbestElement:
    def __init__(self, hypernode, left, right,leftInd, rightInd, edgeScore, grammarScore):
        self.hypernode = hypernode
        self.left = left
        self.right = right
        self.leftInd = leftInd
        self.rightInd = rightInd
        self.edgeScore = edgeScore
        self.grammarScore = grammarScore
        self.length = self.hypernode.length
        
        if right:
            signatureLeft = left.kbest[leftInd][1].signature
            signatureRight = right.kbest[rightInd][1].signature
            self.signature = signatureLeft.merge(signatureRight)
        else:
            self.signature = Signature( self.hypernode.rootNode.getID() ) 
        self.score = -1
    
    
class Kbest:
    def __init__(self,k,function):
        self.k = k
        self.function = function
      
       
    def findKbestAlg2(self,hypernode):
        kbest = []
        def cand(ke):
            res = []
            if len(ke.left.kbest) < ke.leftInd+1:
                ke1 = kbestElement(hypernode, ke.left , ke.right, ke.leftInd+1, ke.rightInd, ke.edgeScore, ke.grammarScore)
                self.score(ke1)
                res.append(ke1)
            if len(ke.left.kbest) < ke.leftInd+1:
                ke2 = kbestElement(hypernode, ke.left, ke.right ,ke.leftInd, ke.rightInd+1, ke.edgeScore, ke.grammarScore)
                self.score(ke2)
                res.append(ke2)
            return res
        
        def append(top):
            if not top in kbest: # redundancy check
                kbest.append(top)
                
        Q = []
        for e in hypernode.backstar:
            ke = kbestElement(hypernode, e.left,e.right,  0, 0, e.edgeScore, e.grammarScore)
            self.score(ke)
            Q.append( (ke.score, ke) )
        heapq.heapify(Q)
     
        
        while len(kbest) < self.k and len(Q)>0:
            top = heapq.heappop(Q)
            append(top)
            for item in cand(top[1]):
                heapq.heappush(Q , (item.score, item) )
                
        hypernode.kbest = kbest

    def score(self, ke):
        k1 = ke.left.kbest[ ke.leftInd ][1]
        k2 = ke.right.kbest[ ke.rightInd ][1]
        ke.score = self.function(k1, k2, ke.grammarScore, ke.edgeScore)
        return ke.score
    
            
    def findKbestNaive(self,hyperedge):
        return None
        '''
        newScore = left.score+right.score+hyperedge.parseScore
        #newScore = left.score+right.score+ math.log(hyperedge.parseScore)
        #lexicographic ordering
        signature = megreSignature(left.subgraph,right.subgraph)
        l.sort()
        subgraph = "("+l[0]+l[1]+")"
        
        he = hyperedge.clone()
        he.left = left
        he.right = right
        
        element = kbestElement(newScore, headNode, he, signature)
        k2best.append(element)
        
        
        k2best += headNode.kbest   
        '''
        #k2best.sort(key = lambda x:x.score,reverse = True)
        #headNode.kbest = k2best[:self.k]
        
        

    
    
    '''   
    def init(self,headNode,score):
        e = kbestElement( headNode, score, str(headNode.rightNode.getID()))
        headNode.kbest.append(e)
    '''
        
    