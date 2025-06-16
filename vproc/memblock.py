from enum import Enum

class Word:
    val = None

    def __init__(self, val = 0):
        self.val = val & 0xff_ff
    def __int__(self):
        return self.val
    def __bool__(self):
        return bool(self.val)

    def get_high(self):
        return self.val >> 8
    def get_low(self):
        return self.val & 0xff
    def write_high(self, a):
        self.val = (a << 8) | (self.val & 0x00_ff)
    def write_low(self, a):
        self.val = a | (self.val & 0xff_00)
    def get_bit(self, bit_pos):
        return (self.val >> bit_pos) & 1
    def set_bit(self, bit_pos, bit):
        if bit:
            self.val |= (1 << bit_pos)
        else:
            self.val &= (0xff_ff ^ (1 << bit_pos))

class SIZE(Enum):
    BYTE = 1
    WORD = 2

class Memory:
    def __init__(self, sz=0xf_ff_ff):
        if sz % 2 != 0:
            sz += 1
        self.v_mem = [Word() for _ in range(sz//2)]

    def read(self, addr, sz : SIZE):
        if addr + sz.value > len(self.v_mem)*2:
            return None

        match sz:
            case SIZE.BYTE:
                w = self.v_mem[addr//2]
                return w.get_high() if addr % SIZE.WORD.value == 0 else w.get_low()
            case SIZE.WORD:
                i = addr // 2
                # h = l = 0
                if addr % SIZE.WORD.value == 0:
                    h = self.v_mem[i].get_low()
                    l = self.v_mem[i].get_high()
                else:
                    l = self.v_mem[i].get_low()
                    h = self.v_mem[i+1].get_high()
                return (h << 8) | l
        return None

    def write(self, addr, val, sz : SIZE):
        if addr + sz.value > len(self.v_mem) * 2:
            return None
        i = addr // 2

        match sz:
            case SIZE.BYTE:
                val &= 0xff
                if addr % SIZE.WORD.value == 0:
                    self.v_mem[i].val = (val << 8) | self.v_mem[i].get_low()
                else:
                    self.v_mem[i].val = val | (self.v_mem[i].val & 0xff_00)
                return True
            case SIZE.WORD:
                i = addr // 2
                w = Word(val)

                if addr % SIZE.WORD.value == 0:
                    self.v_mem[i].val = (w.get_low() << 8) | w.get_high()
                else:
                    self.v_mem[i].val = (self.v_mem[i].val & 0xff_00) | w.get_low()
                    self.v_mem[i+1].val = self.v_mem[i+1].get_low() | (val & 0xff_00)
                return True
        return False

