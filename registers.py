class Registers:
    def __init__(EAX=0xdeadbeef, EBX=0xdeadbeef, ECX=0xdeadbeef, EDX=0xdeadbeef
                 EBP=0xdeadbeef, EIP=0xdeadbeef):
        self.EAX=[EAX]
        self.EBX=[EBX]
        self.ECX=[ECX]
        self.EDX=[EDX]
        self.EBP=[EBP]
        self.EIP=[EAX]
        self.step=0

    
    def rollback(n):
        self.step-=n
        
