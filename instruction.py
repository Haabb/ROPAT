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
        self.type=False
        self.dest=None
        self.source=None
        

        accepted_instr = ['RET','MOV','CALL', 
                          'ADD','POP','DB','LEAVE' ]

        if instruction[0] in accepted_instr:
            self.type=instruction[0]
        
        if len(instruction)>1:    
            # does the instruction have a source?
            if instruction[1][-1]==',':
                self.dest = instruction[1][0:len(instruction[1])-1]
                self.source = instruction[2]
            else:
                self.dest = instruction[1]
        
        types = {        
            'RET': 'RET',
            'JMP': "JMP {0}".format(self.dest),
            'CALL': "CALL {0}".format(self.dest),
            'LEAVE': 'LEAVE',
            'DB': 'DB {0}'.format(self.dest),
            'POP': "stack -> {0}".format(self.dest),
            'MOV': "{0} -> {1}".format(self.source, self.dest),
            'ADD': "{0} + {1} -> {0}".format(self.dest, self.source),
            False: ''
            }
        self.comment = types[self.type]

    def is_accepted(self):
        return self.type

    ''' is_end returns true if the instruction ends a gadget '''
    def is_end(self):
        end_types = {
                        'RET': 0,
                        'JMP': 0,
                        'CALL': 0 }
        return self.type in end_types

            
