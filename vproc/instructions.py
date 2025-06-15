import database.hashtable as hs

# написать свой дописать hash table, чтобы он сам динамически менял размер

class Opcode:
    name = None
    operands = None
    def set_operands(self, text_args):
        self.operands = text_args.replace(',', '').split()

def _remove_comments(str):
    r=str
    for i in range(len(r)):
        if r[i] == ';':
            r = r[0:i]
    return r


class Instructions:
    m_table = None
    opcodes = [Opcode() for _ in range(0xff+1)]

    def __init__(self, file='vproc/8086_table.txt'):
        with open(file, mode='r') as f:
            for s in f.readline():
                op_info = _remove_comments(s).split()
                if not len(op_info):
                    continue
                i = int(op_info[0], 16)
                self.opcodes[i].name = op_info[1]


