import database.hashtable as hs
import database.avl_tree as avl

class Opcode:
    def __init__(self, args, code):
        self.args = args
        self.code = code

class Mnemonic:
    opcodes = None
    def __init__(self):
        def cmp(a, b):
            if isinstance(a, str):
                return (a > b.args) - (a < b.args)
            return (a.args > b.args) - (a.args < b.args)
        self.opcodes = avl.create(cmp)
    def add_opcode(self, args, code):
        avl.insert(self.opcodes, Opcode(args, code))
    def get_opcode(self, args):
        op = avl.find(self.opcodes, args)
        return op.code if op else None


def _remove_comments(str):
    r=str
    for i in range(len(r)):
        if r[i] == ';':
            r = r[0:i]
            break
    return r


class Instructions:
    m_table = None

    def __init__(self, file='vproc/8086_table.txt'):
        self.m_table = hs.ht_init(2)
        with open(file, mode='r') as f:
            for s in f.readlines():
                op_info = _remove_comments(s).split()
                if not len(op_info):
                    continue
                op = hs.ht_get(self.m_table, op_info[1])
                if not op:
                    a = Mnemonic()
                    a.add_opcode(' '.join(op_info[2:]), op_info[0])
                    hs.ht_set(self.m_table, op_info[1], a)
                else:
                    op.add_opcode(' '.join(op_info[2:]), op_info[0])
        hs.ht_full_refresh(self.m_table)

    def is_mnem(self, text):
        return hs.ht_has(self.m_table, text.upper())

    def get_code(self, mnem, args):
        op = hs.ht_get(self.m_table, mnem)
        return op.get_opcode(args)




