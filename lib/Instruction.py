class Gadget:

	def __init__(self):
        self.instruction = []
        self.definition = ''

    def is_register(self, reg):
        return (reg == 'EAX' or 
                reg == 'EBX' or
                reg == 'ECX' or
                reg == 'EDX' or
                reg == 'EBP')

    def add(self, instruction): 
        self.instruction.append(instruction)

    
