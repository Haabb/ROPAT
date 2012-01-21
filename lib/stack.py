from gadget import *
import binascii
import hashlib

class Stack:
    
    def __init__(self):
       self._chain=[]
       self._rop=[]
       self._debug=[]
    
    def debug(self):
        for d in self._debug:
            print d
            
    def rop(self, prefix=','):
        str = "############### ROP CHAIN: {0} bytes ################\n".format(len(self._rop)*4)
        str += "./vuln $(python -c \"print 'A'*24+'"
        for r in self._rop:
            str+=r
        str += "'\")"
        str += "\n############### ROP CHAIN ################\n"
        return str.replace(',', prefix)
              
    def add(self, gadget, value=None):
        self._chain.append( gadget )
        self.stackize(gadget, value)

    def extend(self, stack):
        if stack!=False:
            self._chain.extend(stack._chain)
            self._rop.extend(stack._rop)
            self._debug.extend(stack._debug)
        
    def littleEndian(self, str, prefix=","):
        if len(str)==7:
            str = "0{0}".format(str)
        retStr=""
        for x in range(len(str),0,-2):
            retStr += prefix
            retStr += str[x-2:x].upper()
        return retStr
        
    def hexify(self, str, prefix=","):
        retStr=""
        for x in range(0,len(str), 2):
            retStr += prefix
            retStr += str[x:x+2].upper()
        return retStr
            
        
        
    ''' Convert a gadget to stack elements '''
    def stackize(self, gadget, value=None):

        for i in range( len(gadget.instructions) ):
            if value!=None and i==1:
                if value[0:2]=='0x':
                    self._debug.append( "dd {0}".format(value) )
                    self._rop.append( "{0}".format(self.littleEndian(value[2:]) ))

                else:
                    self._debug.append( "dd '{0}'".format(value) )
                    self._rop.append( "{0}".format(self.hexify(binascii.hexlify( value ) ) ) )

            if i==0:
                self._debug.append("\ndd 0x%.8x   ; %s" % ( gadget.instructions[i].offset, gadget.instructions[i].instruction ) )
                self._rop.append("{0}".format( self.littleEndian( "%.8x" % ( gadget.instructions[i].offset) ) ) )

            elif gadget.instructions[i].type=='POP':
                self._debug.append('dd 0xdeadbeef   ; {0}'.format(gadget.instructions[i].instruction))
                self._rop.append(self.littleEndian("deadbeef"))

            elif gadget.instructions[i].type=='ADD' and gadget.instructions[i].dest=='ESP':
                val = int(gadget.instructions[i].source, 16)
                while val != 0:
                    self._debug.append('dd 0xdeadbeef   ; {0}'.format(gadget.instructions[i].instruction))
                    self._rop.append(self.littleEndian("deadbeef"))
                    val-=4
            else:
                self._debug.append('                ; {0}'.format(gadget.instructions[i].instruction))