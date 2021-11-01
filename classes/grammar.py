
class Grammar:
    def __init__(self, productions, terminals = None, startSymbol = "S"):
        """

        parameters
        ---------
            productions (dictionary). context -> list of pairs. each pair is a (production,score)
            terminals (set of strings in lower case). terminal symbols.
            
        """
        self.initialContext = startSymbol
        self.productions = productions
        self.__inverseProductions = self.__inverseDict(productions)
        self.terminals = terminals
        if self.terminals == None:
            self.terminals = set()
            self.__parseTerminals()
    
    def getInverseProduction(self, key):
        if key in self.__inverseProductions:
            return self.__inverseProductions[key]
        else:
            pass
            #print key, self.__inverseProductions
        return []
    
    def getProductions(self, _deriviation):
        res = []
        for Q in self.productions:
            for deriviation in self.productions[Q]:
                if deriviation[0]==_deriviation:
                    res.append((Q,deriviation[1]))
        return res
    
    def getProductionByMargins(self,left,right):
        res = []
        for Q in self.productions:
            for deriviation in self.productions[Q]:
                if deriviation[0][0] == left and deriviation[0][-1] == right:
                    res.append((Q,deriviation[1]))
        return res
     
    def getStartProductions(self, _deriviation):
        res = []
        for derivation in self.productions[self.initialContext]:
            if derivation[0]==_deriviation:
                res.append((self.initialContext,derivation[1]))
                
        return res
     
    def __parseTerminals(self):
        for symbols in self.__inverseProductions:
            #print symbols
            for symbol in symbols:
                if symbol.islower():
                    self.terminals.add(symbol)
                
    def __inverseDict(self,_dict):
        inverseDict = {}
        for key in _dict:
            for pair in _dict[key]:
                production = pair[0]
                prob = pair[1]
                if not production in inverseDict:
                    inverseDict[production] = []
                inverseDict[production].append([key,prob])
        return inverseDict
    
    def __len__(self):
        c = 0
        for prod in self.productions.values():
            for item in prod:
                c+=1
        return c
    
    def __str__(self):
        string = "Start symbol: %s\n"%self.initialContext
        string += "Terminals: "+ str(self.terminals)+"\n"
        for prod in self.productions:
            string += str(prod)+"->"+str(self.productions[prod])+" | "
        return string

class InputfileGrammarReader():
    
    def __init__(self,inputFilePath):
        self.grammar = self.__loadFile(inputFilePath)
    
    def __loadFile(self,filePath):
        productions = {}
        terminals = []
        startSymbol = "-"
        
        f = open(filePath)
        first = True
        for line in f:
            line = line.split("\n")[0]
            rule,score = line.split(",")
            score = float(score)
            head,tail = rule.split("->")
            if first:
                startSymbol = head
                first = False
            if "@" in tail:
                tail1,tail2 = tail.split("@")
                toadd = ((tail1,tail2) ,score )
            else:
                toadd = ((tail,) ,score )
                terminals.append(tail)
            
            if not head in productions:
                productions[head] = []
            productions[head].append(toadd)
        
        return Grammar(productions, terminals, startSymbol)

    

#i = InputfileGrammarReader("../../data/sample/grammar.txt")
#print i.grammar

#TODO
"""
    1) input validation
        - no lower case symbols as keys in prods
        - no upper case sym in terminals
        - no duplicates
        - 
    2) chomski transformation
    3) normalize scores
    4) no prob optionality
    """

'''
starTRrecEBV = {
                "S*" : [ [("H","-TR", "X*") ,0.5 ],[("S*","-TR", "V1") ,1 ] ],
                "X*" : [ [ ("X","PPI", "V1") ,2 ],[ ("X*","PPI", "V1") ,2 ]],#, [ ("X","PPI", "X1*") ,0.5 ]],
              #  "X1*" : [ [ ("X","PPI", "V1") ,2 ], [ ("X1*","PPI", "V1") ,2 ]],
                }

productions = starTRrecEBV
productions["H"] = [[("h",),1]]
productions["X"] = [[("x",),1]]
productions["T"] = [[("t",),1]]
productions["V1"] = [[("v1",),1]]

grammar = pcfg(productions, None , initialContext = "S*")
print grammar
print grammar.getInverseProduction(("v1",))

'''
    