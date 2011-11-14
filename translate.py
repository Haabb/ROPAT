class Translate:

    ''' Find gadget(s) which dataflow corresponds to command supplied.
        Badlist is a list of registers which is to be avoided using 
        suppeorts finding gadgets for:
        MOV R, R
        MOV R, VAL (BY POP)'''
    def findGadget(command, dest, source=False, bad_list):
        if command=='MOV':
            # Find a gadget to move to DEST.
            # Avoid changing values of registers in bad_list
            # Return address of gadgets with stack values + new bad_list
