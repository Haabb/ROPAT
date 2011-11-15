class Gadget:

    def __init__(self):
        self.instruction = []
        self.definition = ''
        self.tail=False

    ''' Adds an instruction to the gadget chain.
        If an instruction is a tail, set gadget_tail=instruction if length > 1
        else None saying that gadget is meaningless!'''

    def add(self, instruction): 
        accepted_instr = ['RET','MOV','CALL','POP','DB', 'PUSH', 'SUB', 'ADD', 
                          'INC', 'DEC' ]
        tails = ['RET','CALL']

        registers = ['EAX', 'AX', 'AL', 'AH', 'EBX', 'BX', 'BL', 'BH', 'ECX', 'EDX', 'EDI', 'ESI', 'EIP', 'ESP', 
                     'EBP']

        if instruction.type in accepted_instr:            
            self.instruction.append(instruction)

            if instruction.type in tails:
                if len(self.instruction)>1 or (len(self.instruction)==1 and
                                               self.instruction[0].type=="CALL" and
                                               self.instruction[0].dest in registers):
                    

                    if len(self.instruction)==2 and self.instruction[0].type=='LEAVE':
                        self.tail=None
                    else:
                        if instruction.type=='CALL':
                            if instruction.dest in registers:
                                self.tail=instruction
                            else:
                                self.tail=None
                        else:
                            self.tail=instruction
                        
                else:
                    self.tail=None
        else:
            self.tail=None
    
    def output(self):
        if len(self.instruction)>0:
            output = "0x%.8x \t|" % ( self.instruction[0].offset + 0x08048000 )
            for ins in self.instruction:
                output = "{0} {1} #".format(output, ins.comment)
            return output
        else:
            return ""
