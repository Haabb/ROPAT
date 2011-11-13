import distorm3
from gadget import *
from instruction import *

class GadgetCollector:
    
    def __init__(self, file):
        self.file = file
        self.gadgets = []
        self.gadget_chain = []

    '''
    Find gadgets in file specified at init.
    block_length defines the number of bytes the gadget can consist of. If
    a "gadget-end" if found at index n, the gadget will be of length n.
    ''' 
    def findGadgets(self, block_length, options):
        # Read the code from the file
        try:
            fp = open(self.file, 'rb')
            code = fp.read(block_length)
            byte_count = 0

            while len(code)>0:
                iterable = distorm3.DecodeGenerator(byte_count, code, options)
                gadget_bytes = 0
                gadget = Gadget()
                for (offset, size, instruction, hexdump) in iterable:
                    inst = Instruction(hexdump, offset, instruction)

                    if inst.is_accepted()!=False:
                        end = gadget.add(inst)

                    if inst.is_end()==True:
                        gadget.output()
                        break
 
                byte_count+=1
                fp.seek(byte_count)
                code = fp.read(block_length)

        except Exception as e:
            print ('error reading file %s: %s' % (self.file, e))
