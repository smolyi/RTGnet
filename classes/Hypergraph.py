from classes import kbest

class HypernodeCC():
    def __init__(self,rootnode,context, colorCoding, signature = None):
        self.rootNode = rootnode
        self.context = context
        self.length = len(filter(lambda x: x,colorCoding))
        self.colorCoding = colorCoding
        
        self.backstar = []
        
        self.score = -1
        self.kbest = []
    
    def updateScore(self,newscore):
        self.score = max (self.score, newscore)
    
    def __hash__(self):
        return hash((self.rootNode.getID(),self.context,self.colorCoding))
    
    
    def addBackstar(self,e):
        if not isinstance(e, Hyperedge):
            raise Exception("e is not Hyperedge")
        self.backstar.append(e)
        
    def __str__(self):
        return "(%s,%s,%d,%s,score:%f)"%(self.rootNode.Name,self.context,self.length, str(self.colorCoding),self.score )        
   
class Hyperedge:
    def __init__(self, head, left, right, grammarScore, edgeScore, edge,production):
        self.head = head
        self.left = left 
        self.right = right
        
        self.grammarScore = grammarScore
        self.edgeScore = edgeScore
        self.edge = edge
        self.production = production
        
   
    def __hash__(self):
        return hash((self.head,self.left,self.right))
    def __eq__(self,other):
        return hash(other)==hash(self)

#c = HypernodeCC(None, None, [], None).addBackstar(Hyperedge(None, None, None, None, None, None, None))