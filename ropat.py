try:
    import distorm3
except ImportError:
    print "You need diStorm3 disassembler to run this program"


import sys
import argparse
import os.path
from lib import gadgetcollector

parser = argparse.ArgumentParser(description='ROPAT finds gadgets and combines \
                                to ROP-chains', prefix_chars='-')
parser.add_argument('filename', type=argparse.FileType('rb'))
parser.add_argument('memory', type=str, help="Memory location where memory is writeable. Fx. .bss")
parser.add_argument('argv', type=str, \
                    help="List of arguments as 'arg1,arg2,...,argN' where \
                    item1 is the binary and NULL is NULL. NO SPACES!")
parser.add_argument('--debug', dest='debug', action='store_true', default=False)
                    
args = parser.parse_args()


gadgets = gadgetcollector.GadgetCollector(args.filename, args.memory, args.debug)
gadgets.extractGadgets(distorm3.Decode32Bits)
gadgets.search(args.argv)