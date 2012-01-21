from stage import *
from direct import *
from assembler import *

class Exploit:

    def __init__(self, bss, gadgets):
        self.heapLocation="0x%X" % ( int(bss, 16) )
        self.stackLocation="0x%X" % ( int(bss, 16) + 250 )
        
        self.assembler = Assembler(gadgets)
        self.direct=Direct(self.assembler, self.heapLocation)

    def write(self, string):
        action = {'EAX':{'LOAD': 4}, 'EBX':{'LOAD': 1}, 'ECX':{'STORE': string}, 'EDX':{'LOAD': len(string)}}
        direct.ROP(action)


    def exit(self):
        # EAX = 1
        # EBX = 0
        # ECX = 0
        # EDX = 0
        chains = {      'EAX': self.assembler.load('EAX', 1),
                        'EBX': self.assembler.load('EBX', 0),
                        'ECX': self.assembler.load('ECX', 0),  
                        'EDX': self.assembler.load('EDX', 0) } 