class yearString(str):
    def __init__(self,stringIns):
        self.stringIns = stringIns
    def __lt__(self,other):
        LString,RString = self.stringIns,other.stringIns
        if self.stringIns[0] == '/':
            LString = self.stringIns[1:]
        if other.stringIns[0] == '/':
            RString = other.stringIns[1:]
        return int(LString) < int(RString)
    def __gt__(self,other):
        LString,RString = self.stringIns,other.stringIns
        if self.stringIns[0] == '/':
            LString = self.stringIns[1:]
        if other.stringIns[0] == '/':
            RString = other.stringIns[1:]
        return int(LString) > int(RString)
    def __cmp__(self,other):
        LString,RString = self.stringIns,other.stringIns
        return int(LString) == int(RString)
    

class basinIDString(str):
    def __init__(self,stringIns):
        if stringIns[-1].isalpha():
            self.stringIns = stringIns[:-1]
            self.letter = stringIns[-1]
        else:
            self.stringIns = stringIns
            self.letter = chr(ord('A')-1)
    def __lt__(self,other):
        LString,RString = self.stringIns,other.stringIns
        LLetter,RLetter = self.letter, other.letter
        if int(LString) != int(RString):
            return int(LString) < int(RString)
        else:
            return LLetter < RLetter
    def __gt__(self,other):
        LString,RString = self.stringIns,other.stringIns
        LLetter,RLetter = self.letter, other.letter
        if int(LString) != int(RString):
            return int(LString) > int(RString)
        else:
            return LLetter > RLetter
    def __cmp__(self,other):
        LString,RString = self.stringIns,other.stringIns
        LLetter,RLetter = self.letter, other.letter
        return (int(LString) == int(RString)) and (LLetter == RLetter)
        

    
    
    
if __name__ == "__main__":
    print yearString("/2010") == yearString("/2010")
    print basinIDString('202') == basinIDString('202A')
        
            