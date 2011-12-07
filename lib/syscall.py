class Syscall:

    def __init__(self, assembler):
        self.assembler = assembler
        self.memorylocation='0x080c6740'

    def execve(self, program, argv=None, envp=None):
        # EAX = 11
        # EBX = program
        # ECX = argv
        # EDX = envp        
        chains = {      'EAX': self.assembler.load('EAX', 11),\
                        'EBX': self.assembler.store('EBX', program, self.memorylocation),\
                        'ECX': self.assembler.load('ECX', 0),\
                        'EDX': self.assembler.load('EDX', 0) }

        self.memorylocation="0x0%X" % ( int(self.memorylocation, 16) + (len(program) + (128-len(program) ) ) )
        self.solve(chains)

    def write(self, string):
            string = string.replace(" ", "_")
            # EAX = 4
            # EBX = 1
            # ECX = string
            # EDX = len(string)
            chains = {      'EAX': self.assembler.load('EAX', 4),\
                            'EBX': self.assembler.load('EBX', 1),\
                            'ECX': self.assembler.store('ECX', string, self.memorylocation),\
                            'EDX': self.assembler.load('EDX', len(string)) }

            self.memorylocation="0x0%X" % ( int(self.memorylocation, 16) + (len(string) + (128-len(string) ) ) )
            self.solve(chains)

    def exit(self):
        # EAX = 1
        # EBX = 0
        # ECX = 0
        # EDX = 0
        chains = {      'EAX': self.assembler.load('EAX', 1),\
                        'EBX': self.assembler.load('EAX', 0),\
                        'ECX': self.assembler.load('ECX', 0),\
                        'EDX': self.assembler.load('EDX', 0) }

        self.solve(chains)
        
            
        
    def solve(self, chains):
        stack=[]
        sidefree = {}
        registers = ['EAX','EBX','ECX','EDX']
        

        for reg in registers:
            if self.assembler.sidefree( chains[reg], reg ):
                sidefree[reg] = chains[reg]
                registers.remove(reg)

        conflict=True
        while conflict:
            change=False
            for x in range(len(registers)-1):
                sides = self.assembler.stackized_sideeffects( chains[registers[x+1]] )
                if registers[x+1] in sides:
                    sides.remove(registers[x+1])
                if registers[x] in sides:
                    tmp = registers[x+1]
                    registers.remove(tmp)
                    registers.insert(x, tmp)
                    change=True

            conflict=change

        for reg in registers:
            stack.extend( chains[reg] )

        for reg in sidefree.keys():
            stack.extend( chains[reg] )

        stack.extend( self.assembler.stackize( self.assembler.minGadget(self.assembler.catalog['INT']['0x80']) ) )

        for x in stack:
            print x

    def test(self, test_reg):
            #=================================
            #          add and sub test
            #================================= 
            for (imme, g) in self.assembler.sub(test_reg):
                print "-",imme

            for (imme, g) in self.assembler.add(test_reg):
                print "+",imme

            #=================================
            #         movesTo test
            #=================================
            print self.assembler.movesTo(test_reg)

            #=================================
            #         store test
            #=================================
            for x in self.assembler.store(test_reg, '/bin//sh', '0xbffff0ff'):
                print x

            #=================================
            #         load test
            #=================================
            for x in self.assembler.load(test_reg, 13):
                print x
