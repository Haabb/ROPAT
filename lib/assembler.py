import itertools
import sys

class Assembler:
    
    def __init__(self, gadgets):
        self.catalog = {'MOV':{},'POP':{},'SUB':{},'DEC':{},'INC':{},'ADD':{}, 'XOR':{}, 'NEG':{}, 'XCHG':{}}
        self.init_catalog(gadgets)
        self.registers = ['EAX', 'EBX', 'ECX', 'EDX', 'EDI', 'ESI']        

    def load(self, register, immediate):
        gadgets=[]
        if self.catalog['MOV'].has_key(register):
            for key in self.catalog['MOV'][register].keys():
                if key[:2]=='0x':
                    gadgets.append( ( self.hex2signed(key), self.catalog['MOV'][register][key] ) )
        
        return gadgets


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
                chain.extend( self._store(register, data[len(data)-(x+1)*4:len(data)-x*4], "0x%X" % ( int(memory, 16) - (x*4) ) ) )

        return chain

    ''' Store data at memory and have register point at it '''
    def _store(self, register, data, memory):
        chain = []
        registers = ['EAX', 'EBX', 'ECX', 'EDX', 'EDI', 'ESI']

        # Does register have a MOV [register]
        for reg in self.catalog['MOV'].keys():
            if reg==register or reg[0:4]=='[{0}'.format(register):
                if len(reg)>5 and reg[5:7]=='0x':
                    mem_add = reg[5:-1] # HEX value to add/subtract from memory address
                    if int(mem_add, 16) > 2000 or int(mem_add, 16) < -2000:
                        break
                    else:
                        memory = "0x%X" % ( int(memory, 16) + (-1 * int(mem_add, 16) ) )

                for r in self.catalog['MOV'][reg].keys():
                    if r in self.catalog['POP'].keys() and register in self.catalog['POP'].keys():
                        chain.extend( self.stackize( self.minGadget(self.catalog['POP'][register]), memory ) )
                        chain.extend( self.stackize( self.minGadget(self.catalog['POP'][r]), data ) )
                        chain.extend( self.stackize( self.minGadget(self.catalog['MOV'][reg][r]) ) )
                        
                        # Extend with one POP register more, to ensure register points to data
                        chain.extend( self.stackize( self.minGadget(self.catalog['POP'][register]), memory ) )
                        break

                return chain

    ''' Finds the smallest gadget and uses it '''
    def minGadget(self, gadgetCollection):
        length = 1000
        gadget = None
        for g in gadgetCollection:
            if len(g.instructions)< length:
                length=len(g.instructions)
                gadget=g
        return gadget

    ''' Create the stack for a gadget 
        args:
        - gadget: the gadget to create a stack for
        - value(optional): a value to fx. pop'''
    def stackize(self, gadget, value=None):
        stack=[]
        for i in range( len(gadget.instructions) ):
            if i==0:
                stack.append("\ndd 0x%.8x\t; %s" % ( gadget.instructions[i].offset, gadget.instructions[i].instruction ) )

            if i==1 and value!=None:
                if value[0:2]=='0x':
                    stack.append( "dd {0}".format(value) )
                else:
                    stack.append( "dd '{0}'".format(value) )

            if gadget.instructions[i].type=='POP' and i!=0:
                stack.append('dd 0xdeadbeef\t; {0}'.format(gadget.instructions[i].instruction))
            
            # Also take care of ADD, ESP!!

        return stack




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
                            chain.append( self.catalog['MOV'][l[i]][l[i+1]] )

                            if l[i+1]==reg_from:
                                chains.append( list(reversed(chain)) )
                        else:
                            break

        return chains


    def add(self, register):
        tuple=[]
        if self.catalog['ADD'].has_key(register):
            for imme in self.catalog['ADD'][register].keys():
                if imme[0:2]=='0x':
                    tuple.append( (imme, self.catalog['ADD'][register][imme]) )

        return tuple
    
    ''' subtract finds gadgets that can subract any immediate from register 
        return (imme, gadget) tuple '''
    def sub(self, register):
        tuple=[]
        if self.catalog['SUB'].has_key(register):
            for imme in self.catalog['SUB'][register].keys():
                if imme[0:2]=='0x':
                    tuple.append( (imme, self.catalog['SUB'][register][imme]) )

        return tuple

    ''' Returns the sideeffects of of a gadget '''
    def sideeffects(self, gadget):
        registers = []
        for i in gadget.instructions[1:]:
            if i.type=='POP' or i.type=='MOV':
                registers.append( i.dest )
        return registers
 
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

            
            if i.type=='INC' or i.type=='DEC' or i.type=='POP' or i.type=='NEG':
                if i.dest in self.catalog[i.type].keys():
                        self.catalog[i.type][i.dest].append(g)

                else:
                    self.catalog[i.type][i.dest] = [g]

    ''' Looks through gadget and outputs the stack chain AFTER first instruction'''
    def stack(gadget):
        chain = []
        for i in gadget.instructions[1:]:
            if i.type=='POP':
                chain.append("dd 0xdeadbeef\t;{1}".format(i.instruction))

        return chain
