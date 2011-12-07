import itertools
import sys

class Assembler:
    
    def __init__(self, gadgets):
        self.catalog = {'MOV':{},'POP':{},'SUB':{},'DEC':{},'INC':{},'ADD':{}, 'XOR':{}, 'NEG':{}, 'XCHG':{}, 'INT':{}}
        self.init_catalog(gadgets)
        self.registers = ['EAX', 'EBX', 'ECX', 'EDX', 'EDI', 'ESI']        

    def load(self, register, immediate):
        mov_values=[]
        change_gadgets=[]
        gadgets=[]
        reg_value=None


        # Find out if there is a sidefree way to load data using XOR, POP or XCHG
        if  self.catalog['XOR'].has_key(register) and \
            self.catalog['XOR'][register].has_key(register) and \
            self.sidefree( self.stackize( self.minGadget( self.catalog['XOR'][register][register]) ), register ):
            reg_value=0
            gadgets.extend( self.stackize( self.minGadget( self.catalog['XOR'][register][register] ) ) )

        elif    self.catalog['POP'].has_key(register) and \
                self.sidefree( self.stackize( self.minGadget( self.catalog['POP'][register]) ), register ) :
            gadgets.extend( self.stackize( self.minGadget(self.catalog['POP'][register]), '0xFFFFFFFF') )
            reg_value=-1
        else:
                           
            # Look for values that can be loaded into register
            if self.catalog['POP'].has_key(register) and reg_value==None:
                gadgets.extend( self.stackize( self.minGadget(self.catalog['POP'][register]), '0xFFFFFFFF') )
                reg_value=-1

            # First look if register can be cleared by xor
            if self.catalog['XOR'].has_key(register) and reg_value==None:
                if self.catalog['XOR'][register].has_key(register):
                    reg_value=0
                    gadgets.extend( self.stackize( self.minGadget( self.catalog['XOR'][register][register] ) ) )


        # if reg_value is set, use add or sub to get to immediate value
            
        # TODO: This should be changed to not use inc and dec only
        if reg_value!=None:
            if reg_value<immediate:
                if self.catalog['INC'].has_key(register):
                    while reg_value<immediate:
                        change_gadgets.extend( self.stackize( self.minGadget( self.catalog['INC'][register] ) ) )
                        reg_value+=1

            if reg_value>immediate:
                if self.catalog['DEC'].has_key(register):
                    while reg_value>immediate:
                        change_gadgets.extend( self.stackize( self.minGadget( self.catalog['DEC'][register] ) ) )
                        reg_value-=1

            gadgets.extend(change_gadgets)
            
        return gadgets


    ''' Convert a hex value to a sign int '''
    def hex2signed(self, s):
        value = long(s, 16)
        if value > sys.maxint:
            value = value - 2L*sys.maxint - 2
        assert -sys.maxint-1 <= value <= sys.maxint
        return int(value)

 

    ''' Store data at memory and have register point at it. 
        Uses self._store, to store every 4 bytes.'''
    def store(self, register, data, memory):
        chain=[]
        if self._store(register, data, memory ) == None:
            moves = self.movesTo(register)
            moves.remove(register)
            for reg in moves:
                if self._store(register, data, memory ) != None:
                    return self.store(reg, data, memory)
        else:            
            for x in range(len(data)/4):
                chain.extend( self._store(register, data[len(data)-(x+1)*4:len(data)-x*4], "0x%X" % ( int(memory, 16) - (x*4) ), "0x%X" % ( int(memory, 16)  ), (x==0)  ))

            # Push null after storage by loading -1 into already effected register, inc to 0 and use mov [register], effected
        
        return chain

    ''' Store data at memory and have register point at it '''
    def _store(self, register, data, memory, orgmemory=None, first=False):
        chain = []
        registers = ['EAX', 'EBX', 'ECX', 'EDX', 'EDI', 'ESI']

        # Does register have a MOV [register]
        for reg in self.catalog['MOV'].keys():    
            if reg[0:4]=='[{0}'.format(register):
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
                        if r in self.catalog['POP'].keys() and register in self.catalog['POP'].keys():
                            data_store=self.minGadget(self.catalog['POP'][r], [register])
                            data_placement=self.minGadget(self.catalog['POP'][register], [r])

                            # If end, push null to end of data
                            if first==True:
                                chain.extend( self.stackize( self.minGadget(self.catalog['POP'][r]), '0xFFFFFFFF' ) )
                                chain.extend( self.stackize( self.minGadget(self.catalog['INC'][r]) ) )
                                chain.extend( self.stackize( data_placement, "0x0%X" % ( int(memory, 16) - 4 ) ) )

                            if data_store==None and data_placement!=None:    
                                chain.extend( self.stackize( self.minGadget(self.catalog['POP'][r]), data ) )
                                chain.extend( self.stackize( data_placement, memory ) )

                            elif data_store!=None and data_placement==None:
                                chain.extend( self.stackize( self.minGadget(self.catalog['POP'][register]), memory ) )
                                chain.extend( self.stackize( data_store, data ) )

                            else:
                                chain.extend( self.stackize( data_placement, memory ) )
                                chain.extend( self.stackize( data_store, data ) )

                            chain.extend( self.stackize( self.minGadget(self.catalog['MOV'][reg][r]) ) )
                            
                            # Extend with one POP register more, to ensure register points to data in the end
                            if orgmemory!=None:
                                chain.extend( self.stackize( self.minGadget(self.catalog['POP'][register]), "0x0%X" % ( int(memory, 16) + ( int(mem_add, 16) ) ) ) )
                            break

                    return chain

    def minGadget(self, gadgetCollection, avoids=None):
        registers=['EAX','EBX','ECX','EDX']
        length = 1000
        gadget = None
        for g in gadgetCollection:
            sidefree=True

            # If none of the instructions affects main registers, use it no matter
            # of the length
            for i in g.instructions[1:]:
                if i.dest in registers:
                    sidefree=False
            if sidefree==True:
                return g

            if len(g.instructions)< length:
                if avoids!=None:
                    for avoid in avoids:
                        if avoid in self.stackized_sideeffects( self.stackize(g) ):
                            break
                        else:
                            length=len(g.instructions)
                            gadget=g
                            break
                        
                else:
                    length=len(g.instructions)
                    gadget=g
        return gadget


    ''' Create the stack for a gadget 
        args:
        - gadget: the gadget to create a stack for
        - value(optional): a value to fx. pop in the first instruction '''
    def stackize(self, gadget, value=None):
        stack=[]

        #print gadget
        for i in range( len(gadget.instructions) ):
            #print "Placing ", gadget.instructions[i].instruction

            if value!=None and i==1:
                #print 2
                if value[0:2]=='0x':
                    stack.append( "dd {0}".format(value) )
                else:
                    stack.append( "dd '{0}'".format(value) )

            if i==0:
                #print 1
                stack.append("\ndd 0x%.8x   ; %s" % ( gadget.instructions[i].offset, gadget.instructions[i].instruction ) )

            elif gadget.instructions[i].type=='POP':
                #print 3
                #print "POP found"
                stack.append('dd 0xdeadbeef   ; {0}'.format(gadget.instructions[i].instruction))
            
            elif gadget.instructions[i].type=='ADD' and gadget.instructions[i].dest=='ESP':
                #print 4
                val = int(gadget.instructions[i].source, 16)
                while val != 0:
                    stack.append('dd 0xdeadbeef   ; {0}'.format(gadget.instructions[i].instruction))
                    val-=4
            else:
                #print 5
                stack.append('                ; {0}'.format(gadget.instructions[i].instruction))

        return stack

    ''' Side effects of a collections of gadgets in stackize format '''
    def stackized_sideeffects(self, stack):
        registers=[]
        for elm in stack:
            if ";" in elm:
                reg = elm.split(";")[1].replace(",", "").split(" ")
                if len(reg)>2:
                    reg=reg[2]
                    if reg=='AL' or reg=='AH' or reg=='AX':
                        reg='EAX'
                    if reg=='BL' or reg=='BH' or reg=='BX':
                        reg='EBX'
                    if reg=='CL' or reg=='CH' or reg=='CX':
                        reg='ECX'
                    if reg=='DL' or reg=='DH' or reg=='DX':
                        reg='EDX'
                    registers.append(reg)
        
        return list(set(registers))

    ''' Does stack have side effects? '''
    def sidefree(self, stack, exception):
        register=['EAX', 'EBX', 'ECX', 'EDX']
        effected=self.stackized_sideeffects(stack)
        if exception in effected:
            effected.remove(exception)
        
        free=True
        for elm in effected:
            if elm in register:
                free=False

        return free

    ''' Return a list of registers that can move data to register '''
    def movesTo(self, register, chain=[]):
        chain.append( register )
        if register in self.catalog['MOV'].keys():
            for r in self.catalog['MOV'][register].keys():
                if r in self.registers and not r in chain:
                    chain.extend( self.movesTo( r, chain ) )

        if register in self.catalog['XCHG'].keys():
            for r in self.catalog['XCHG'][register].keys():
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
                            chain.append( minGadget( self.catalog['MOV'][l[i]][l[i+1]] ) )

                            if l[i+1]==reg_from:
                                chains.append( list(reversed(chain)) )
                        else:
                            break

        return chains

 
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
