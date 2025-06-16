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


class proc:
    reg = registers()
    flags = Word()
    instructions = Instructions()
    ram = Memory()

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



