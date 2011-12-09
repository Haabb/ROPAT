#              New assembler layout
#
#   Make a gadget chain, that stores the values on a new stack and pops them
#
#   (1)
#   Start finding the way to POP to the registers from "new stack", to
#   arrange a order of stack popping ex.
#
#   order = ['EAX', 'EDX', 'ECX', 'EBX']
#   Low index is most "side effect" free registers to POP data to
#
#   for i in order:
#       stack( action[ order[i] ] )
#
#   Action for eax:
#       
#
#   (2)
#   apply takes a dir where eax, ebx, ecx and edx i set:
#   action = {'EAX': 11, 'EBX': "/bin//sh", 'ECX': ["/bin//sh", 0], 'EDX': 0}
#
#   New stack layout - data have to be moved to here
#   0xdeadbeef  ; Pointer to gadget
#   0x0000000a  ; POP EAX
#   0x00000000  ; Side effects
#   0x00000000  ; Side effects

#   0xdeadbeef  ; Pointer to gadget
#   0x00pointer ; POP EBX
#   0x00000000  ; Side effects

#   0xdeadbeef  ; Pointer to gadget
#   0x00pointer ; POP ECX

#   0xdeadbeef  ; Pointer to gadget
#   0x00000000  ; POP EDX

#   Memory layout   - Here we store data
#

#   FUNCTIONS:
#   store_stack(value) - save value on new stack.
#   store_data(data)   - save data in memory and return address of where it's saved
#
#   
#
import itertools
import sys

class Assembler_revisited:

    def __init__(self, gadgets, memory):

        self.memory=memory
        self.memory_data="0x%X" % (int(self.memory, 16) + 297)
        self.memory_stack= "0x%X" % (int(self.memory, 16) + 256)
    
        self.catalog = {'MOV':{},'POP':{},'SUB':{},'DEC':{},'INC':{},'ADD':{}, 'XOR':{}, 'NEG':{}, 'XCHG':{}, 'INT':{}}

        self.realstack = []

        self.init_catalog(gadgets)


        self.registers = ['EAX', 'EBX', 'ECX', 'EDX', 'EDI', 'ESI']

        #
        #  TODO:    Function to determain order of fake stak popping.
        #  

        string = "Hej_lille_verden"
        self.buildFakeStack( self.suitableGadget(self.catalog['INT']['0x80'], []), None )        

        val, gadget = self.fake_pop('EBX')
        self.buildFakeStack( self.suitableGadget(gadget, []), 1 )   

        val, gadget = self.fake_pop('EDX')
        self.buildFakeStack( self.suitableGadget(gadget, []), len(string) )      

        val, gadget = self.fake_pop('ECX')
        self.buildFakeStack( self.suitableGadget(gadget, []), string )

        val, gadget = self.fake_pop('EAX')
        self.buildFakeStack( self.suitableGadget(gadget, []), 4 )


        ( val, chain ) = self.store_data('0xdeadbeef', True)
        self.realstack.extend( chain )
        if self.catalog['POP'].has_key('EBP'):
            self.realstack.extend ( self.stackize( self.suitableGadget( self.catalog['POP']['EBP'], [] ), "0x%X" % (int(self.memory_stack, 16) + 4) ) )
        
        if self.catalog['MOV'].has_key('ESP') and self.catalog['MOV']['ESP'].has_key('EBP'):
            self.realstack.extend ( self.stackize( self.suitableGadget( self.catalog['MOV']['ESP']['EBP'], [] ) ) )
            

        for x in self.realstack:
            print x



    ''' Store some data in either stack or data
        POP register, memory adress
        POP r, DATA
        MOV [register], r '''
    def store_data(self, data, stack=False):
        chain = []

        if stack==True:
            memory=self.memory_stack
        else:
            memory=self.memory_data
            
        for register in self.registers:
            for reg in self.catalog['MOV'].keys():
                if reg[0:4]=='[{0}'.format(register) and register in self.catalog['POP'].keys():
                    good=True
                    mem_add='0x0'
                    if len(reg)>5 and reg[5:7]=='0x':
                        #mem_add =  # HEX value to add/subtract from memory address
                        if int(reg[5:-1], 16) > 2000 or int(reg[5:-1], 16) < -2000:
                            good=False
                        else:
                            mem_add = reg[5:-1]
                            memory = "0x0%X" % ( int(memory, 16) + (-1 * int(mem_add, 16) ) )

                    if good==True:
                        for r in self.catalog['MOV'][reg].keys():
                            if r in self.catalog['POP'].keys(): 

                                # Popping memory address - register=address
                                chain.extend( self.stackize( self.suitableGadget(self.catalog['POP'][register], [r]), memory ) )

                                # Popping value - r=value
                                chain.extend( self.stackize( self.suitableGadget(self.catalog['POP'][r], [register]), data ) )

                                # MOV [register], r
                                chain.extend( self.stackize( self.catalog['MOV'][reg][r][0] ) )

                                if stack==True:
                                    self.memory_stack="0x%X" % (int(self.memory_stack, 16) - 4)
                                    return (self.memory_stack, chain)
                                else:
                                    # Increment address for next storing
                                    self.memory_data="0x%X" % (int(self.memory_data, 16) + 4)

                                    # Return address where data was saved and gadget chain
                                    return ("0x%X" % (int(self.memory_data, 16) - 4), chain)


    ''' Create rob chain for real stack, to put immediate value on fake stack.
        Starts by putting immediate in a register that can be loaded into an address'''
    def store_stack(self, immediate):
            chain = []
            memory=self.memory_stack
            for register in self.registers:
                for reg in self.catalog['MOV'].keys():
                    if reg[0:4]=='[{0}'.format(register) and register in self.catalog['POP'].keys():
                        good=True
                        mem_add='0x0'
                        if len(reg)>5 and reg[5:7]=='0x':
                            #mem_add =  # HEX value to add/subtract from memory address
                            if int(reg[5:-1], 16) > 2000 or int(reg[5:-1], 16) < -2000:
                                good=False
                            else:
                                mem_add = reg[5:-1]
                                memory = "0x0%X" % ( int(memory, 16) + (-1 * int(mem_add, 16) ) )
                        if good==True:
                            for r in self.catalog['MOV'][reg].keys():
                                if r in self.catalog['POP'].keys() and self.catalog['INC'].has_key(r):

                                    # Popping value - r=value
                                    chain.extend( self.stackize( self.suitableGadget(self.catalog['POP'][r], [register]), '0xFFFFFFFF' ) )
                                    
                                    value=-1
                                    while immediate>value:
                                        chain.extend( self.stackize( self.suitableGadget(self.catalog['INC'][r], [register]) ) )
                                        value+=1
        
                                    # Popping memory address - register=address
                                    chain.extend( self.stackize( self.suitableGadget(self.catalog['POP'][register], [r]), memory ) )

                                    # MOV [register], r
                                    chain.extend( self.stackize( self.catalog['MOV'][reg][r][0] ) )

                                    self.memory_stack="0x%X" % (int(self.memory_stack, 16) - 4 )

                                    return chain

    ''' Takes a gadget and analyze it from last instruction en backwards.
        - value is the value to put on fake stack
        If:
        POP: store_stack('0xDEADBEEF') '''
    def buildFakeStack(self, gadget, value):
        for instruction in gadget.instructions[-1:0:-1]:
            if instruction.type=='POP':
                (address, chain) = self.store_data('0xDEADBEEF', True)
                self.realstack.extend ( chain )# Put value on fake stack

            elif instruction.type=='ADD' and instruction.dest=='ESP':
                self.memory_stack="0x%X" % (int(self.memory_stac, 16) - int(instruction.source, 16) )

        if isinstance( value, int ):
            # Store immediate value on fake stack
            self.realstack.extend( self.store_stack(value) )

        elif isinstance( value, str ):
            for i in range(0,len(value), 4):
                if i==0:
                    (data_address, data_chain) = self.store_data(value[i:i+4])
                    (address, chain) = self.store_data(data_address, True)
                    self.realstack.extend( data_chain )
                    self.realstack.extend( chain )
                else:
                    (data_address, data_chain) = self.store_data(value[i:i+4])
                    self.realstack.extend( data_chain )
        else:
            (address, chain) = self.store_data("0x%X" % gadget.instructions[0].offset, True)
            self.realstack.extend( chain )
            
                        
            

        # Store gadget offset on fake stack
        (address, chain) = self.store_data("0x%X" % gadget.instructions[0].offset, True)
        self.realstack.extend( chain )


    ''' Finds a gadget which does not have registers in side effects '''
    def suitableGadget(self, gadgets, registers):
        g=None
        length=999
        for gadget in gadgets:
            if registers!=[]:
                for register in registers:
                    if register in self.effects(gadget):
                       suitable=False
                    else:
                        if len(gadget.instructions)<length:
                            g=gadget
                            length=len(gadget.instructions)
            else:
                if len(gadget.instructions)<length:
                    g=gadget
                    length=len(gadget.instructions)

        return g

    ''' Find side effects and returns as list '''
    def effects(self, gadget):
        lst=[]
        for instruction in gadget.instructions[1:]:
            if instruction.dest!=None:
                lst.append(instruction.dest)

        return lst

    # Only supports direct pops atm
    ''' pop returns true if data can be popped from stack and moved to register,
        either by POP REGISTER, or POP A, MOV REGISTER, A '''
    def fake_pop(self, register):
        if self.catalog['POP'].has_key(register):
            return (True, self.catalog['POP'][register])


    ''' Return a list of registers that can move data to register '''
    def movesTo(self, register, chain=[]):
        chain.append( register )
        if register in self.catalog['MOV'].keys():
            for r in self.catalog['MOV'][register].keys():
                if r in self.registers and not r in chain:
                    chain.extend( self.movesTo( r, chain ) )

        return list(set(chain))

    ''' Return gadget to move data from reg_from to reg_to '''
    def moveToFrom(self, reg_to, reg_from):
        chains = []
        possible_moves = self.movesTo(reg_to)
        possible_moves.remove(reg_to)

        if len(possible_moves) > 1:
            for lst in list(itertools.permutations(possible_moves)):
                chain=[]
                
                if self.catalog['MOV'][reg_to].has_key(lst[0]):
                    l = [reg_to]
                    l.extend(lst)
                    for i in range(len(l)-1):

                        if self.catalog['MOV'][l[i]].has_key(l[i+1]):
                            chain.append( self.catalog['MOV'][l[i]][l[i+1]][0] )

                            if l[i+1]==reg_from:
                                chains.append( list(reversed(chain)) )
                        else:
                            break

        return chains

    ''' Create the stack for a gadget 
        args:
        - gadget: the gadget to create a stack for
        - value(optional): a value to fx. pop in the first instruction '''
    def stackize(self, gadget, value=None):
        stack=[]

        for i in range( len(gadget.instructions) ):
            if value!=None and i==1:
                if value[0:2]=='0x':
                    stack.append( "dd {0}".format(value) )

                else:
                    stack.append( "dd '{0}'".format(value) )

            if i==0:
                stack.append("\ndd 0x%.8x   ; %s" % ( gadget.instructions[i].offset, gadget.instructions[i].instruction ) )

            elif gadget.instructions[i].type=='POP':
                stack.append('dd 0xdeadbeef   ; {0}'.format(gadget.instructions[i].instruction))
            
            elif gadget.instructions[i].type=='ADD' and gadget.instructions[i].dest=='ESP':
                val = int(gadget.instructions[i].source, 16)
                while val != 0:
                    stack.append('dd 0xdeadbeef   ; {0}'.format(gadget.instructions[i].instruction))
                    val-=4
            else:
                stack.append('                ; {0}'.format(gadget.instructions[i].instruction))

        return stack

    ''' Put all gadgets in catalog '''
    def init_catalog(self, gadgets):
        for g in gadgets:
            i = g.instructions[0]
            # Quaranteed dest and source types
            if i.type=='MOV' or i.type=='SUB' or i.type=='ADD' or i.type=='XOR' \
                or i.type=='XCHG':
                if i.dest in self.catalog[i.type].keys():
                    if i.source in self.catalog[i.type][i.dest].keys():
                        self.catalog[i.type][i.dest][i.source].append(g)

                    else:
                        self.catalog[i.type][i.dest][i.source] = [g]

                else:
                    self.catalog[i.type][i.dest] = {i.source: [g]}

            
            if i.type=='INC' or i.type=='DEC' or i.type=='POP' or i.type=='NEG' or i.type=='INT':
                if i.dest in self.catalog[i.type].keys():
                        self.catalog[i.type][i.dest].append(g)

                else:
                    self.catalog[i.type][i.dest] = [g]
