import distorm3
from gadget import *
from instruction import *
from struct import *
from syscall import *
from stage import *
from direct import *
import hashlib

class GadgetCollector:
    
    def __init__(self, file, type, length, bss, debug=False):
        self.file = file
        self.type = type
        self.length=length
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
            fp = open(self.file, 'rb')
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
            
            if self.type=='direct':
                assembler = Direct(self.gadgets)
                
                syscall = Syscall(assembler, self.bss)
                syscall.execve('/bin//sh')
                
            elif self.type=='stage':
                print "Stage"
                assembler = Stage(self.gadgets, self.bss)
                
            if (self.debug==True):
                print assembler.catalog
                    

        #except Exception as e:
        #    print ('error reading file %s: %s' % (self.file, e))
