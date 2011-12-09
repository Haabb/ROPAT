class Gadget:

    def __init__(self):
        self.instructions = []
        self.dest = []
        self.source = []
        
        self.registers = ['EAX', 'AX', 'AL', 'AH', 'EBX', 'BX', 'BL', 'BH', 'ECX', 
                     'EDX', 'EDI', 'ESI', 'EIP', 'ESP', 'EBP']



    ''' Is an instruction is accepted in gadgets '''
    def accepted_instruction(self,instruction):
        accepted_instr = ['RET','MOV' ,'POP','PUSH', 'SUB', 'ADD', 
                          'INC', 'DEC', 'INT', 'XOR', 'CDQ', 'XCHG', 'NEG', 'JB' ]
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

            if self.instructions[0].type!='MOV':
                    if self.instructions[0].dest!=None and '[' in self.instructions[0].dest:
                        return False
                    if self.instructions[0].source!=None and '[' in self.instructions[0].source:
                        return False

            # Check that instructions in gadget does not interfere with first
            # or that ESP is not changed
            for i in self.instructions[1:]: 
                if i.dest==self.instructions[0].dest or \
                    self.register_conflict(i.dest, self.instructions[0].dest) or \
                   (i.dest=='ESP' and (i.type=='POP' or i.type=='MOV') or \
                    'DWORD' in i.instruction or 'WORD' in i.instruction or \
                    'BYTE' in i.instruction):
                    return False

                if i.dest!=None and '[' in i.dest:
                    return False
                if i.source!=None and '[' in i.source:
                    return False

            return True

        return False

    ''' Determains if registers conflict. Ex. mov [eax+4]... mov [eax+8] 
        return True on conflict '''
    def register_conflict(self, reg1, reg2):    
        if reg1!=None and reg2!=None:
            if '[' in reg1 and '[' in reg2:
                if reg1[1:4]==reg2[1:4] and len(reg1)>5 and len(reg2)>5:
                    for reg in self.registers:
                        if reg in reg2[5:-1]:
                            return True
                    if  int(reg1 [5:-1], 16)-int(reg2[5:-1], 16)<128 or \
                        int(reg1[5:-1], 16)-int(reg2[5:-1], 16)>-128:
                        return True
        return False


    ''' Output contents of a gadget '''
    def output(self):
        if len(self.instructions)>0:
            output = "\n;dd 0x%.8x \t;" % ( self.instructions[0].offset )
            for ins in self.instructions:
                output = "{0} {1} #".format(output, ins.instruction)
            return output

    def bad_offset(self):
        memory = "0x%.8x" % ( self.instructions[0].offset )
        bad = ['09','0a']
        if self.instructions[0].offset > 0x080c4ccc:
            return True  
      
        for b in bad:
            if b in memory:
                return True

        return False
    def __repr__(self):
         return self.output()
    def __str__(self):
         return self.output()
