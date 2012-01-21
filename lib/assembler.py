from stack import *
class Assembler:

    def __init__(self, gadgets):
        self.catalog = {'MOV':{},'POP':{},'SUB':{},'DEC':{},'INC':{},'ADD':{}, 'XOR':{}, 'NEG':{}, 'XCHG':{}, 'INT':{}}
        self.init_catalog(gadgets)
    
    ''' Finds gadgets to get data from stack and store at a memory location '''
    def store_array(self, memory, data, register, avoid=[]):
        stack = False
        # This one decreases
        array_memory = "0x%0.8X" % ( int(memory, 16) + (4*len(data) ) )

        # This increases
        data_memory = "0x%0.8X" % ( int(memory, 16) + (4*len(data) )+ 4 )
        
        #if self.store_data(data_memory, 'data', register, avoid) and \
        #   self.store_register(array_memory, register, avoid):
        if self.store_data(data_memory, 'data', register, avoid) and \
           self.store_register(register, '0xdeadbeef', avoid) and \
           self.load(0, register, avoid):
           
            tmpStack=Stack()
                        
            for n in range(len(data)-1,-1,-1):
                if data[n]==None:
                    tmpStack.extend( self.load(0, register, avoid) )
                    tmpStack.extend( self.store_register(register, array_memory, avoid) )
                    data[n]="NULL"
                    
                else:
                    tmpStack.extend( self.store_data(data_memory, data[n], register, avoid) )
                    tmpStack.extend( self.store_register(register, array_memory, avoid) )
        
                array_memory = "0x%0.8X" % ( int(array_memory, 16) - 4 )
                data_memory = "0x%0.8X" % ( int(data_memory, 16) + len(data[n]) + 4 )
                
            array_memory = "0x%0.8X" % ( int(array_memory, 16) + 4 )    
             
            tmpStack.add( self.minGadget(self.catalog['POP'][register], avoid), array_memory )
        
            stack=tmpStack   
                
        return stack
    
    
    ''' Finds gadgets to get data from stack and store at a memory location '''
    def store_data(self, memory, data, register, avoid=[]):
        stack = False
        for reg in self.catalog['MOV'].keys():    
            if reg[0:4]=='[{0}'.format(register):
                tmpStack=Stack()
                        
                if len(reg)==5:
                    newmemory = "0x%0.8X" % ( int(memory, 16) )
                elif int(reg[4:-1], 16):
                    newmemory = "0x%0.8X" % ( int(memory, 16) + (-1 * int(reg[4:-1], 16) ) )
                else:
                    break
                for r in self.catalog['MOV'][reg].keys():
                    if r in self.catalog['POP'].keys() and \
                       not r in avoid and \
                       register in self.catalog['POP'].keys() and \
                       self.minGadget(self.catalog['POP'][r], avoid) and \
                       self.minGadget(self.catalog['POP'][register], avoid) and \
                       self.minGadget(self.catalog['MOV'][reg][r], avoid):
                        # Can we pop data to r without touching avoid+register?
                        avoid.append(register)
                        data_store=self.minGadget(self.catalog['POP'][r], avoid )
                    
                        avoid.pop()
                        avoid.append(r)
                        data_placement=self.minGadget(self.catalog['POP'][register], avoid )
                        avoid.pop()
                        
                        tmpData = data
                        while len(tmpData)>0:
                            # Fill out data if size < 4 so they fit on stack
                            if len(tmpData)<4:
                                tmpData+= "".join( (4-len(tmpData))*["F"] )
                                
                            if data_store==False and data_placement!=False:    
                                tmpStack.add( self.minGadget(self.catalog['POP'][r], avoid), tmpData[:4] )
                                tmpStack.add( data_placement, newmemory )

                            elif data_store!=False and data_placement==False:
                                tmpStack.add( self.minGadget(self.catalog['POP'][register], avoid), newmemory )
                                tmpStack.add( data_store, tmpData[:4] )
                            else:
                                tmpStack.add( data_store, tmpData[:4] )
                                tmpStack.add( data_placement, newmemory )

                            tmpStack.add( self.minGadget(self.catalog['MOV'][reg][r], avoid) )
                        
                            newmemory = "0x%0.8X" % ( int(newmemory, 16) + 0x4 )
                            tmpData=tmpData[4:]
                        
                        # When element is saved in memory, null terminate it by pushing 0x0
                        if self.load( 0, register,  avoid ) and \
                           self.store_register( register, newmemory,  avoid ):
                           
                            tmpStack.extend( self.load( 0, register, avoid ) )
                            tmpStack.extend( self.store_register( register, "0x%0.8X" % ( int(memory, 16) + len(data) ),  avoid ) )
                        else:
                            break
                                
                        tmpStack.add( self.minGadget(self.catalog['POP'][register], avoid), memory )
                            
                        if stack==False or len(tmpStack._rop)<len(stack._rop):
                            stack=tmpStack   
                            break

        return stack
    
    
    ''' Store the value a register holds, at some memory location '''
    def store_register(self, register, memory, avoid=[]):
        stack=False
        registers = ['EAX', 'EBX', 'ECX', 'EDX', 'EDI', 'ESI']
        registers.remove(register)
        for a in avoid:
            registers.remove(a)
        
        for reg in registers:
            tmpStack=Stack()
            for r in self.catalog['MOV'].keys():
                if r[0:4]=='[{0}'.format(reg) and \
                   reg in self.catalog['POP'].keys() and \
                   register in self.catalog['MOV'][r].keys() and \
                   self.minGadget( self.catalog['POP'][reg], avoid ) and \
                   self.minGadget( self.catalog['MOV'][r][register], avoid ):

                    if len(r)==5:
                        newmemory = "0x%0.8X" % ( int(memory, 16) )
                    elif int(r[4:-1], 16):
                        newmemory = "0x%0.8X" % ( int(memory, 16) + (-1 * int(r[4:-1], 16) ) )
                    else:
                        break

                    avoid.append(register)
                    tmpStack.add( self.minGadget( self.catalog['POP'][reg], avoid ), newmemory )

                    avoid.pop()
                    tmpStack.add( self.minGadget( self.catalog['MOV'][r][register], avoid ) )
                                        
                    if stack==False or len(tmpStack._rop)<len(stack._rop):
                        stack=tmpStack   
                        break

        return stack
    

    ''' Finds gadgets to get an immediate value to a register '''    
    def load(self, immediate, register, avoid=[]):
        stack=Stack()
        reg_value=None

        # But prefore if we can xor
        if self.catalog['XOR'].has_key(register) and \
           self.catalog['XOR'][register].has_key(register) and \
           self.minGadget( self.catalog['XOR'][register][register], avoid ):
                reg_value=0
                stack.add( self.minGadget( self.catalog['XOR'][register][register], avoid ) )
                           
        # Look for values that can be loaded into register
        elif self.catalog['POP'].has_key(register) and \
             self.minGadget(self.catalog['POP'][register], avoid):
                stack.add( self.minGadget(self.catalog['POP'][register], avoid), '0xFFFFFFFF')
                reg_value=-1

        # TODO: This should be changed to not use inc and dec only
        if reg_value!=None:
            if reg_value<immediate:
                if self.catalog['INC'].has_key(register) and \
                   self.minGadget( self.catalog['INC'][register], avoid ):
                    while reg_value<immediate:
                        stack.add(  self.minGadget( self.catalog['INC'][register], avoid ) )
                        reg_value+=1
                    return stack

            elif reg_value>immediate:
                if self.catalog['DEC'].has_key(register) and \
                   self.minGadget( self.catalog['DEC'][register], avoid ):
                    while reg_value>immediate:
                        stack.add(  self.minGadget( self.catalog['DEC'][register], avoid ) )
                        reg_value-=1
                    return stack
                    
        return False
    
    
    ''' Find a syscall gadget '''
    def syscall(self, avoid=[]):
        stack=False
        if self.minGadget( self.catalog['INT']['0x80'], avoid ):
            stack=Stack()
            stack.add( self.minGadget( self.catalog['INT']['0x80'], avoid )  )
        return stack
    
    
    ''' Find the gadget with minimum sideeffects to minimize chain '''
    def minGadget(self, gadgetCollection, avoids=[]):
        avoid=[]
        for reg in avoids:
            avoid.extend([reg, "{0}L".format(reg[1]), "{0}H".format(reg[1]), "{0}X".format(reg[1])])
          
        limit = 1000
        gadget = False
        for g in gadgetCollection:
            garbage=0
            for i in g.instructions[1:]:
                if i.dest in avoid:
                    garbage=10001
                    break
                else:
                # If it does not effect main registers, use it no matter what
                    if i.type == "POP":
                        garbage+=4
                    elif i.type == 'ADD' and i.dest == 'ESP':
                        garbage+=int(i.source, 16)
                                   
            if garbage < limit:
                limit = garbage
                gadget = g

        return gadget
    
    
    ''' Categories gadgets '''    
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
    