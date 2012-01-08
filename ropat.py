try:
    import distorm3
    import sys
    import optparse
    import os.path
    from lib import gadgetcollector

    # Parse the command line arguments
    usage  = 'Usage: %prog [--b16 | --b32 | --b64] <filename> <mode> <gadget length> <memory> <debug>'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(  '--b16', help='80286 decoding',
                        action='store_const', dest='dt', const=distorm3.Decode16Bits  )
    parser.add_option(  '--b32', help='IA-32 decoding [default]',
                        action='store_const', dest='dt', const=distorm3.Decode32Bits  )
    parser.add_option(  '--b64', help='AMD64 decoding',
                        action='store_const', dest='dt', const=distorm3.Decode64Bits  )
    parser.set_defaults(dt=distorm3.Decode32Bits)
    options, args = parser.parse_args(sys.argv)
    
    error_str = ""

    if len(args) < 2:
        error_str = '{0}\n{1}'.format(error_str, "missing parameter: filename")
    elif len(args) < 3:
        error_str = '{0}\n{1}'.format(error_str, "missing parameter: mode")
    elif len(args) < 4:
        error_str = '{0}\n{1}'.format(error_str, "missing parameter: gadget length")
    elif len(args) < 5:
        error_str = '{0}\n{1}'.format(error_str, "missing parameter: bss memory")
    else:
        filename = args[1]
        try:
            open(filename)
        except IOError:
            error_str = '{0}\n{1}'.format(error_str, "File {0} could not be opened".format(filename))
        
        if (args[2].lower()=='direct'):
            mode="direct"
        elif (args[2].lower()=='stage'):
            mode="stage"
        else:
            error_str = '{0}\n{1}'.format(error_str, "Invalid mode: {0}".format(args[2]))
        try:
            length = int(args[3], 10)
        except ValueError:
            error_str = '{0}\n{1}'.format(error_str, "Invalid gadget length: %s" % args[3])
        if length < 0:
            error_str = '{0}\n{1}'.format(error_str, "Invalid gadget length: %s" % args[3])

        try:
            bss = args[4]
            int(bss, 16)
        except ValueError:
            error_str = '{0}\n{1}'.format(error_str, 'invalid memory address: %s' % args[3])
            
        debug=False
        if len(args)==6:
            if args[5]=='True':
                debug=True
        
        if len(args) > 6:
            error_str = '{0}\n{1}'.format(error_str, 'too many parameters')

    if len(error_str)>0:
        parser.error(error_str)

    gadgets = gadgetcollector.GadgetCollector(filename, mode, length, bss, debug)

    gadgets.extractGadgets(options.dt)
    
except ImportError:
    print "You need diStorm3 disassembler to run this program"