import distorm3
from gadget import *
from instruction import *
from struct import *
from exploit import *
import hashlib

class GadgetCollector:
    
    def __init__(self, file, bss, debug):
        self.file = file
        self.length=6
        self.bss=bss
        self.gadgets = []
        self.debug=debug
    '''
    Find gadgets in file specified at init.
    block_length defines the number of bytes the gadget can consist of. If
    a "gadget-end" if found at index n, the gadget will be of length n.
    ''' 
    def extractGadgets(self, options):
        #try:
            fp = self.file
            code = fp.read(1)
            code_offset = 0
            
            while len(code)>0:
                # Is the byte a RET
                if unpack('c', code) == ("\xc3",):
                    
                    gadget_search=code_offset
                    index = 0

                    while True:
                    
                        fp.seek(gadget_search - index)
                        code = fp.read(index + 1)

                        iterable = distorm3.DecodeGenerator(gadget_search - index, code, options)

                        length = 0 # count length of instructions in gadgets.
                        gadget = Gadget()
                        for (offset, size, instruction, hexdump) in iterable:
                            inst = Instruction(hexdump, offset, instruction)
                            
                            if length > self.length or not gadget.accepted_instruction(inst):                                
                                break
                            # Add instructions to gadget
                            gadget.add(inst)
                            length+=1

                        if gadget.check():
                            self.gadgets.append(gadget)
                        
                        if length > self.length:
                                break

                        index+=1
              
                code_offset+=1  
                fp.seek(code_offset)
                code = fp.read(1) 

    def search(self, argv):
        exploit = Exploit(self.bss, self.gadgets)
        argv = argv.split(',')
        for n in range( len(argv) ):
            if argv[n]=="NULL":
                argv[n]=None
        
        exploit.execve(argv[0], argv)
        
        
        print exploit.direct.chain.rop('\\x')

        if (self.debug):
            exploit.direct.chain.debug()