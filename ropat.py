import distorm3
import sys
import optparse
from lib import gadgetcollector

# Parse the command line arguments
usage  = 'Usage: %prog [--b16 | --b32 | --b64] filename [offset] [memory offset]'
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
filename = args[1]
offset   = 0
length   = None
if len(args) == 3:
    try:
        offset = int(args[2], 10)
    except ValueError:
        parser.error('invalid offset: %s' % args[2])
    if offset < 0:
        parser.error('invalid offset: %s' % args[2])
elif len(args) > 3:
    parser.error('too many parameters')

gadgets = gadgetcollector.GadgetCollector(filename)

gadgets.extractGadgets(offset, options.dt)

