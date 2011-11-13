class Gadget:

    def __init__(self):
        self.instruction = []
        self.definition = ''
        self.gadget_end=False

    def add(self, instruction): 
        if instruction.is_accepted()!=False:
            if instruction.type=='RET':
                if len(self.instruction)>0:
                    self.instruction.append(instruction)
    
    def output(self):
        if len(self.instruction)>0:
            output = "{0} \t|".format(self.instruction[0].offset)
            for ins in self.instruction:
                output = "{0} {1}".format(output, ins.comment)
            print output
