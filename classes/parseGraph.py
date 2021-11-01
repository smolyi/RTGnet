class Deriviation:
    def __init__(self,source,leftState, rightState, score):
        self.source = source
        self.leftState = leftState 
        self.rightState = rightState
        self.score = score
    
    def __hash__(self):
        return hash((self.leftState,self.rightState))
    def __eq__(self,other):
        return self.leftState==other.leftState and self.rightState==other.rightState
    
class State:
    def __init__(self, Q, l, bottomScore = 0 ):
        self.context = Q
        self.length = l
        self.topScore = 0
        self.bottomScore = bottomScore
        self.bestOutsideParseScore = 0
        self.parents = []
        self.children = []
        
    def __str__(self):
        return "(%s,%d,%f,%f,%f)"%(self.context,self.length,self.topScore,self.bottomScore,self.bestOutsideParseScore)
    def __hash__(self):
        return hash((self.context,self.length))
    def hash(self):
        return (self.context,self.length)
    
    
class ParseGraph:
    def __init__(self, grammar):
        self.grammar = grammar
        #print str(grammar)
    
    def printStatesAsLine(self, _dict):
        string = ""
        for s in _dict.values():
            string += str(s)
        print string
    
    def printStates(self, _dict):
        for s in _dict.values():
            print str(s)
        print 
        
    def __insert(self, _dict, state, child1, child2, score):
        hashState = state.hash()
        if not hashState in _dict:
            _dict[hashState] = state
        state = _dict[hashState]
        
        
        newScore = score
        if child1  : 
            newScore = newScore + child1.bottomScore 
        if child2 : 
            newScore = newScore + child2.bottomScore 
            
        if state.bottomScore < newScore:
            state.bottomScore = newScore
            
        state.children.append(Deriviation(state,child1, child2, score))
        if child1:
            child1.parents.append(Deriviation(state,child1, child2, score))
        if child2:
            child2.parents.append(Deriviation(state,child1, child2, score))
        
    def parseGraph(self,maxLength):
        
        currentStates = {}
        
        i = 0
        #initialization
        for t in self.grammar.terminals:
            for prod in self.grammar.getInverseProduction((t,)):
                s = State(prod[0], i, prod[1])
                self.__insert(currentStates,s,None,None,prod[1])
        states = currentStates
        
        #self.printStates(states)
        #print "(%d) %d states created. total of %d states."%(i, len(currentStates), len(states))
        
        #main loop
        i += 1
        while len(currentStates)>0:
            
            newStates = {}
            for s1 in currentStates.values():
                '''
                for Q,score in self.grammar.getStartProductions((s1.context)):
                    s = State(Q, s1.length+1) 
                    self.__insert(newStates,s,s1,None,score)
                '''
                for s2 in states.values():
                    l = s1.length+s2.length+1 
                    if l <= maxLength:     
                        for Q,score in self.grammar.getProductionByMargins(s1.context,s2.context):
                            s = State(Q, l) 
                            self.__insert(newStates,s,s1,s2,score)
                        for Q,score in self.grammar.getProductionByMargins(s2.context,s1.context):
                            s = State( Q,l ) 
                            self.__insert(newStates,s,s2,s1,score)
            
            currentStates = newStates
            states.update(newStates)
            
            #self.printStates(newStates)
            #print "(%d) %d states created. total of %d states."%(i,len(currentStates),len(states))
            i += 1
            
        self.topDown(states)
        #self.printStates(states)
        self.finalAlphaScores(states)
        #self.printStates(states)
        for key in states:
            states[key] = states[key].bestOutsideParseScore
        return states
    
    def finalAlphaScores(self, states):
        for state in states.values():
            MAX = 0
            if state.context == self.grammar.initialContext:
                MAX = 1
            for deriv in state.parents:
                if deriv.leftState == state:
                    otherChild = deriv.rightState 
                elif deriv.rightState == state:
                    otherChild = deriv.leftState
                else:
                    raise Exception("ERROR - %s"%deriv) 
                otherScore = 1
                if otherChild: 
                    otherScore = otherChild.bottomScore
                score = deriv.source.topScore + deriv.score + otherScore
                if score > MAX:
                    MAX = score
            state.bestOutsideParseScore = MAX
            
    def topDown(self,states):
        def derivationScore(deriv):
            return deriv.source.topScore + deriv.score
        statesKeys = states.keys()
        statesKeys.sort(key=lambda x:states[x].length,reverse = True)
        for key in statesKeys:
            s = states[key]
            if s.context == self.grammar.initialContext:
                s.topScore = 1
            else:
                MAX = 0
                for p in s.parents:
                    tmp = derivationScore(p)
                    if tmp > MAX:
                        MAX = tmp
                s.topScore = MAX
            
    
if __name__=="__main__":
    from classes.grammar import pcfg
    
    productions = {"S":[[("F"),0.4],[("D"),0.6]],          
                   "F":[[("A","C"),0.8],[("A","A"),0.2]],
                    "C":[[("D","A"),1]],
                    "D":[[("B","E"),0.1],[("B","B"),0.9]],
                    "E":[[("F","B"),1]],
                    "A":[[("a"),1]],
                    "B":[[("b"),1]]}  
        
    grammar = pcfg(productions)
    res = ParseGraph(grammar).parseGraph(3)
    for k in res:
        print k,res[k]