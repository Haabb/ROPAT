import itertools
from stack import *
import sys

class Direct:
    
    def __init__(self, assembler, memory):
        self.registers = ['EAX', 'EBX', 'ECX', 'EDX']  
        self.assembler=assembler
        self.memory=memory
        self.chain=Stack()
    
        
    def rop(self, actions):
        stack=Stack()
        self.conflict_sort(actions)
        
        for register in self.registers:
            if register in actions.keys():
                for act in actions[register].keys():
                    n = self.registers.index(register)
                    if act=='LOAD':
                        stack.extend( self.assembler.load(actions[register][act], self.registers[n], self.registers[:n] ) )
                        
                    if act=='STORE_DATA':
                        stack.extend( self.assembler.store_data(self.memory, actions[register][act], self.registers[n], self.registers[:n] ) )
                        self.memory = "0x%0.8X" % ( int(self.memory, 16) + len(actions[register][act])+4 )
                        
                    if act=='STORE_ARRAY':
                        length=8
                        for elm in actions[register][act]:
                            if elm==None:
                                length+=4
                            else:
                                length+=(16+len(elm))
                        stack.extend( self.assembler.store_array(self.memory, actions[register][act], self.registers[n], self.registers[:n] ) )
                        self.memory = "0x%0.8X" % ( int(self.memory, 16) + length)
                        
        self.chain.extend(stack)
                
        if not self.conflict_sort(actions):
            print "################################## \n \
                    Could not create full ROP chain!"
    
                    
    def syscall(self):
        if self.assembler.syscall():
            self.chain.extend(self.assembler.syscall())
        
    
    def conflict_sort(self, action):
        moves=0
        conflict=True
        while 1:
            nochange=0
            for n in range( len( self.registers )-1, -1, -1 ):    
                if self.registers[n] in action.keys():
                    for act in action[self.registers[n]].keys():
                        
                        move=False
                        if act=='LOAD':
                            if not self.assembler.load(action[self.registers[n]][act], self.registers[n], self.registers[:n] ):
                                stak=self.assembler.load( action[self.registers[n]][act], self.registers[n], self.registers[:n] )
                                move=True
                               
                        elif act=='STORE_DATA':
                            if not self.assembler.store_data("0xdeadbeef", 'data', self.registers[n], self.registers[:n]):
                               move=True
                                
                        elif act=='STORE_ARRAY':
                            if not self.assembler.store_array("0xdeadbeef", ['data','data'], self.registers[n], self.registers[:n] ):
                                move=True             
                    if move:
                        moves+=1
                        tmp = self.registers.pop(n)
                        self.registers.insert(n-1, tmp)
                    else:
                        nochange+=1
            if nochange == len( self.registers ):
                break   
                    
            if moves>50:
                return False
        return True
    