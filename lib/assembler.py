import itertools

class Assembler:
  
  def __init__(self, gadgets):
    self.catalog = {'MOV':{},'POP':{},'SUB':{},'DEC':{},'INC':{},'ADD':{}, 'XOR':{}, 'NEG':{}}
    self.init_catalog(gadgets)
    self.registers = ['EAX', 'EBX', 'ECX', 'EDX', 'EDI', 'ESI']

  ''' Find gadgets which combined can store data in memory
    register = The register you want to point to the memory
    data = The data you want to store in memory
    memory = The address where you want to store memory (have to be writeable)
    sub = If true, the function does NOT look in other registers for store if R does not have a store.
  '''
  def store(self, register, data, memory, sub=False):
    chain = []
    nextchain = []
    stack = []

    registers = ['EAX', 'EBX', 'ECX', 'EDX', 'EDI', 'ESI']

    # Does register have a MOV [register]
    if "[{0}]".format(register) in self.catalog['MOV'].keys():

      for r in self.catalog['MOV']["[{0}]".format(register)].keys():
        if r in self.catalog['POP'].keys() and register in self.catalog['POP'].keys():
          chain.append( self.catalog['POP'][register] )
          chain.append( self.catalog['POP'][r] )
          chain.append( self.catalog['MOV']["[{0}]".format(register)][r] )
          break

    # If register has no MOV [register], try using other registers
    else:
      if sub==False and register in self.catalog['MOV'].keys():
          print "Looking in others"
          for r in self.catalog['MOV'][register].keys():
            print "Looking in {0}".format(r) 
            chain = self.store(r, data, memory, True)
    
    # If chain could not be found, look in other registers that can move to 
    '''if not setup and sub==False:
      for r in self.catalog['MOV'][register].keys():
        (setup, retrieve, store, nextchain, stack) = store(register, data, memory, True)
        if chain!=None:
          break
    elif setup:'''
    return chain

  ''' Traverse self.container to find all registers able to move data from, to "register"
      args:
      register: the register to move data to

      return a list of registers, self included '''
  def movesTo(self, register, chain=[]):
    chain.append( register )
    if register in self.catalog['MOV'].keys():
      for r in self.catalog['MOV'][register].keys():
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
  
  def null(self, register, sub=False):
    if self.catalog['XOR'].has_key(register):
      if self.catalog['XOR'][register].has_key(register):
        return self.catalog['XOR'][register][register]

    elif self.catalog['MOV'].has_key(register) and  \
         self.catalog['MOV'][register].has_key('0xffffffff') and \
         self.catalog['NEG'].has_key(register):
        return self.catalog['MOV'][register]['0xffffffff']
    
    # Look if other registers can be moved to register
    else:
        if sub==False:
            others = self.movesTo(register)
            others.remove(register)
            if others!=None:
                for reg in others:
                    if self.null(reg)!=None:
                        return self.null(reg, True)
      


  ''' Returns the sideeffects of of a gadget '''
  def sideeffects(self, gadget):
    registers = []
    for i in gadget.instructions[1:]:
      registers.append( ( i.type, i.dest) )
    return registers
 
  ''' Put all gadgets in catalog '''
  def init_catalog(self, gadgets):

    for g in gadgets:
      i = g.instructions[0]

      # Quaranteed dest and source types
      if i.type=='MOV' or i.type=='SUB' or i.type=='ADD' or i.type=='XOR':
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
