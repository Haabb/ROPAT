class Instruction:
    ''' Initiate an instruction.
        Return None if no instruction is made
        Return False if instruction is bad 
    '''
    def __init__(self, hexcode, offset, instruction):
        self.hexcode = hexcode
        self.offset = offset
        self.instruction = instruction
        instruction = instruction.split(" ")
        self.type=self.type=instruction[0]
        self.dest=None
        self.source=None
        
        if len(instruction)>1:  

            # does the instruction have a source?
            if instruction[1][-1]==',':
                self.dest = instruction[1][0:len(instruction[1])-1]
                self.source = instruction[2]
            else:
                self.dest = instruction[1]
