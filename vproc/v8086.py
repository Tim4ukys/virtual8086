from vproc.memblock import *
import enum
from vproc.instructions import *

# регистры
class registers:
    # Основные
    ax, bx, cx, dx = [Word() for _ in range(4)]
    # Индексные регистры
    si, di = [Word() for _ in range(2)]
    # Указатели
    bp, sp, ip = [Word() for _ in range(3)]
    # Сегментные
    cs, ds, es, ss = [Word() for _ in range(4)]

class proc_flags(enum.Enum):
    # Состояние
    carry = 0 # флаг переноса
    parity = 2 # флаг чётности (чёткости)
    auxiliary_carry = 4 # вспомогательный флаг переноса
    zero = 6
    sign = 7 # флаг знака
    overflow = 11 # злодей британец
    # Управляющие
    direction = 10 # направление (1 - увел 0 - уменьшать)

def inc_40(vproc, _):
    vproc.reg.ax.set(vproc.reg.ax.val + 1)
    return 1
def inc_41(vproc, _):
    vproc.reg.cx.set(vproc.reg.cx.val + 1)
    return 1
def inc_42(vproc, _):
    vproc.reg.dx.set(vproc.reg.dx.val + 1)
    return 1
def inc_43(vproc, _):
    vproc.reg.bx.set(vproc.reg.bx.val + 1)
    return 1

def jmp_e9(self, i):
    tmp = self.ram.read(i+1, SIZE.WORD)
    offs = to_sign(tmp, 2)
    return offs + 1


funcs = {
    0x40: inc_40,
    0x41: inc_41,
    0x42: inc_42,
    0x43: inc_43,
    0xe9: jmp_e9
}

class proc:
    reg = registers()
    flags = Word()
    instructions = Instructions()
    ram = Memory()



    def next(self):
        i = self.reg.cs.val + self.reg.ip.val
        op = self.ram.read(i, SIZE.BYTE)
        self.reg.ip.val += funcs[op](self, i)



    def _default_reg(self):
        self.reg.sp.val = 0xff_ff

    def reset_registers(self):
        for name, value in registers.__dict__.items():
            if not name.startswith('__'):
                setattr(self.reg, name, Word())
        self._default_reg()

    def reset_flags(self):
        self.flags.val = 0
    def set_flag(self, flag : proc_flags, bit):
        self.flags.set_bit(flag.value, bit)
    def get_flag(self, flag : proc_flags):
        return self.flags.get_bit(flag.value)

