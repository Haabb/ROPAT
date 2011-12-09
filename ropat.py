import distorm3
import sys
import optparse
from lib import gadgetcollector

# Parse the command line arguments
usage  = 'Usage: %prog [--b16 | --b32 | --b64] <filename> <gadget length> <bss memory> <debug>'
parser = optparse.OptionParser(usage=usage)
parser.add_option(  '--b16', help='80286 decoding',
                    action='store_const', dest='dt', const=distorm3.Decode16Bits  )
parser.add_option(  '--b32', help='IA-32 decoding [default]',
                    action='store_const', dest='dt', const=distorm3.Decode32Bits  )
parser.add_option(  '--b64', help='AMD64 decoding',
                    action='store_const', dest='dt', const=distorm3.Decode64Bits  )
parser.set_defaults(dt=distorm3.Decode32Bits)
options, args = parser.parse_args(sys.argv)

if len(args) < 2:
    parser.error('missing parameter: filename')
if len(args) < 3:
    parser.error('missing parameter: gadget length\nmissing parameter: bss memory')
if len(args) < 4:
    parser.error('missing parameter: bss memory')

filename = args[1]

try:
    length = int(args[2], 10)
except ValueError:
    parser.error('invalid gadget length: %s' % args[2])
if length < 0:
    parser.error('invalid gadget length: %s' % args[2])

try:
    bss = args[3]
    int(bss, 16)
except ValueError:
    parser.error('invalid memory address: %s' % args[3])

debug=False
if len(args)==5:
    if args[4]=='True':
        debug=True

if len(args) > 5:
    parser.error('too many parameters')


gadgets = gadgetcollector.GadgetCollector(filename, length, bss, debug)

gadgets.extractGadgets(options.dt)

