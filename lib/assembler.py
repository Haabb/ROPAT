class Assembler:
    
    def __init__(self, gadgets):
        self.gadgets = gadgets
        self.catalog = {'MOV':{},'POP':{},'PUSH':{},'SUB':{},'DEC':{},'INC':{},'ADD':{}, 'NULL':{}, 'XCHG':{}}
        #['RET','MOV','CALL','POP','PUSH', 'SUB', 'ADD', 'INC', 'DEC', 'INT', 'XOR', 'CDQ', 'XCHG' ]

    ''' Store looks for gadgets which combined can store data in memory '''
    def store(self, register, data, memory):
        chain = []
        nextchain = []
        stack = []


        registers = ['EAX', 'EBX', 'ECX', 'EDX', 'EDI', 'ESI']
        self.lookup('POP', register)
        self.lookup('MOV', "[{0}]".format(register))

        for r in self.catalog['MOV']["[{0}]".format(register)].keys():
            self.lookup('POP', r)
            if r in self.catalog['POP'].keys():
                setup = self.catalog['POP'][register]['gadget']
                retrieve = self.catalog['POP'][r]['gadget']
                store = self.catalog['MOV']["[{0}]".format(register)][r]['gadget']
                break

        stack.append( setup.output() )
        stack.append( memory )
        

        self.lookup('DEC', register)
        for i in range(4):
            nextchain.append(self.catalog['DEC'][register]['gadget'])

        while not len(data) % 4==0:
            data = "{0}A".format(data)

        for i in reversed(range(len(data) / 4)):
            stack.append( retrieve.output() )
            stack.append( data[(i*4):(i*4)+4] )
            stack.append( store.output() )
            if (i > 0):
                for n in nextchain:
                    stack.append( n.output() )



        return stack


    ''' Returns the sideeffects of of a gadget '''
    def sideeffects(self, gadget):
        registers = []
        for i in gadget.instructions[1:]:
            registers.append( ( i.type, i.dest) )
        return registers
    
    ''' Looks for at gadget where type register exist '''
    def lookup(self, type, register):
        gadgets = []
        for g in self.gadgets:
            if g.instructions[0].type==type:
                if g.instructions[0].dest==register:
                    gadgets.append(g)
        
        if not register in self.catalog[type].keys():
            self.catalog[type][register] = {}
        
        # Types where source is guaranteed
        if type=='MOV' or type=='SUB' or type=='ADD' or type=='XCHG':
            for (source, sideeffect, g) in [(g.instructions[0].source, self.sideeffects(g), g) for g in gadgets]:
                if source in self.catalog[type][register].keys():
                    if len(self.catalog[type][register][source]['sideeffects']) > len(self.sideeffects(g)):
                        self.catalog[type][register][source]['gadget'] = g
                        self.catalog[type][register][source]['sideeffects'] = self.sideeffects(g)
                    else:
                        self.catalog[type][register][source]= {'gadget': g, 'sideeffects': self.sideeffects(g)}
                else:
                    self.catalog[type][register][source]= {'gadget': g, 'sideeffects': self.sideeffects(g)}

        elif type=='POP' or type=="DEC":
            for (dest, sideeffect, g) in [(g.instructions[0].dest, self.sideeffects(g), g) for g in gadgets]:
                if 'gadget' in self.catalog[type][register].keys():
                    if len(self.catalog[type][register]['sideeffects']) > len(self.sideeffects(g)):
                        self.catalog[type][register]['sideeffects'] = self.sideeffects(g)
                        self.catalog[type][register]['gadget'] = g
                else:
                    self.catalog[type][register] = {'gadget':g,'sideeffects': self.sideeffects(g)}
