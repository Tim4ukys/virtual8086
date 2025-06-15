from vproc.memblock import *
import enum

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

    ram = Memory()

    def set_flag(self, flag : proc_flags, bit):
        self.flags.set_bit(flag.value, bit)
    def get_flag(self, flag : proc_flags):
        return self.flags.get_bit(flag.value)



