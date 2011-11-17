class Gadget:

    def __init__(self):
        self.instructions = []
        self.dest = []
        self.source = []

        accepted_instr = ['RET','MOV','CALL','POP','PUSH', 'SUB', 'ADD', 
                          'INC', 'DEC', 'INT', 'XOR', 'CDQ', 'XCHG' ]

        tails = ['RET','CALL', 'JMP']
        
        registers = ['EAX', 'AX', 'AL', 'AH', 'EBX', 'BX', 'BL', 'BH', 'ECX', 
                     'EDX', 'EDI', 'ESI', 'EIP', 'ESP', 'EBP']



    ''' Is an instruction is accepted in gadgets '''
    def accepted_instruction(self,instruction):
        accepted_instr = ['RET','MOV' ,'POP','PUSH', 'SUB', 'ADD', 
                          'INC', 'DEC', 'INT', 'XOR', 'CDQ', 'XCHG', 'NEG' ]
        return instruction.type in accepted_instr
       

    def add(self, instruction): 
        self.instructions.append(instruction)        

    ''' Check that gadget is good '''
    def check(self):
        
        if len(self.instructions) > 0 and not self.bad_offset() and\
            (self.instructions[-1].type=='RET' and self.instructions[-1].dest==None):
            for i in self.instructions[:-1]:
                if i.type=='RET':
                    return False;

            return True

        return False


    ''' Output contents of a gadget '''
    def output(self):
        if len(self.instructions)>0:
            output = "0x%.8x \t;" % ( self.instructions[0].offset + 0x08048000 )
            for ins in self.instructions:
                output = "{0} {1} #".format(output, ins.instruction)
            return output

    def bad_offset(self):
        memory = "0x%.8x" % ( self.instructions[0].offset + 0x08048000 )
        bad = ['09','0a']
        if self.instructions[0].offset + 0x08048000 > 0x080c4ccc:
            return True  
      
        for b in bad:
            if b in memory:
                return True

        return False
        
