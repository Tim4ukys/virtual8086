import database.hashtable as ht
from vproc.instructions import _remove_comments
from vproc.memblock import SIZE
import enum

from vproc.v8086 import registers

# решить вопрос с прописью и заглавием

ALLOWED_SYMBOLS = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789'
    '_'
)

def _is_label(text):
    return _is_name_var(text[:-1:]) and text[-1] == ":"

def _is_name_var(text):
    if not (('A' <= text[0] <= 'Z') or ('a' <= text[0] <= 'z')):
        return False
    for i in text:
        if i not in ALLOWED_SYMBOLS:
            return False
    return True

def _to_number(text, sz):
    try:
        decode = {
            'h': lambda a: int(a, 16),
            'o': lambda a: int(a, 8),
            'd': lambda a: int(a),
            'b': lambda a: int(a, 2)
        }
        if not ('0' <= text[-1] <= '9' or text[-1] in decode):
            raise ValueError
        decode = (decode['d' if '0' <= text[-1] <= '9' else text[-1]])(text[:-1])
        if decode >= 2 ** (8 * sz.value):
            return None
        return decode
    except ValueError:
        return None

# [*вот эту запись*]
def _get_pointer(text):
    if text[0] == '[' and text[-1] == ']':
        return text[1:-1]
    return None

def _get_modRm(mod, reg, rm):
    reg16 = {k: i for i, k in enumerate(['AX', 'CX', 'DX', 'BX', 'SP', 'BP', 'SI', 'DI'])}
    reg8 = {k: i for i, k in enumerate(['AX', 'CX', 'DX', 'BX', 'SP', 'BP', 'SI', 'DI'])}

    r = 0
    if mod == 11:
        r |= 0b11000000
        r |= (reg16 if reg in REG_16 else reg8)[reg] << 3
        r |= (reg16 if reg in REG_16 else reg8)[rm]
    else:
        raise RuntimeError


class CompErrors(enum.Enum):
    LOT_TEXT = "В строке есть лишние символы"
    ANY_TEXT = 'Недостаточно символов'
    UNK_SYMBOL = 'Неизвестный символ'

    SEG_UNKNOWN = 'Неизвестный сегмент'
    SEG_DOUBLE = 'Сегмент указан дважды'

    DS_UNK_TYPE = 'Неизвестный тип данных'
    DS_NOT_HOME = 'Переменные объявляются строго внутри .data'
    DS_NOT_NUMB = 'Поддерживаются только числа'

    LB_EXITS = "Эта метка уже существует. Придумайте другое название"
    LB_NOT_HOME = 'Метка должна быть только внутри .text'

    OP_UNK = "Такой команды нет. Проверьте строку, пожалуйста"


class CompileProg:
    lines = None

    def __init__(self, file_name):
        with open(file_name) as f:
            self.lines = [[i, _remove_comments(s).split()]
                          for i, s in enumerate(f.readlines(), start=1)
                          if len(_remove_comments(s).split())]

    def compile(self, vproc):
        vproc.reset_registers()
        vproc.reset_flags()

        labels = {
            '.data': dict(),
            '.text': dict(),
        }

        use_label = {}

        def reg_label(lb, addr):
            if lb not in use_label:
                use_label[lb] = [addr]
            else:
                use_label[lb].append(addr)

        i = 0x0
        cur_seg = ''

        for number, s in self.lines:
            def error(text):
                raise RuntimeError(f"Line: {number} | {text.value}")

            if s[0] == 'segment':
                if len(s) > 2:
                    error(CompErrors.LOT_TEXT)

                seg = {
                    ".text": vproc.reg.cs,
                    ".data": vproc.reg.ds,
                }
                if s[1] in seg:
                    if not seg[s[1]]:
                        i = seg[s[1]].val = (i & 0xff_f0) + 0x10
                        cur_seg = s[1]
                    else:
                        error(CompErrors.SEG_DOUBLE)
                else:
                    error(CompErrors.SEG_UNKNOWN)
            elif _is_name_var(s[0]):
                sz = {'db': SIZE.BYTE, 'dw': SIZE.WORD}
                labels['.data'][s[0]] =  i - vproc.reg.ds
                if len(s) <= 2:
                    error(CompErrors.ANY_TEXT)
                elif s[1] not in sz:
                    error(CompErrors.DS_UNK_TYPE)
                elif cur_seg not in ['.data']:
                    error(CompErrors.DS_NOT_HOME)

                for numb in s[3:]:
                    numb = _to_number(numb, sz[s[1]])
                    if not numb:
                        error(CompErrors.DS_NOT_NUMB)
                    vproc.ram.write(i, numb, sz[s[1]])
                    i += sz[s[1]].value
            elif _is_label(s[0]):
                if len(s) > 1:
                    error(CompErrors.LOT_TEXT)
                elif cur_seg != '.text':
                    error(CompErrors.LB_NOT_HOME)
                elif s[0] in labels['.text']:
                    error(CompErrors.LB_EXITS)

                labels['.text'][s[0]] = i - vproc.reg.cs
            elif vproc.instructions.is_mnem(s[0]):
                args = _get_mb_args(s[1:])
                op_type = None
                op = None
                for i in args:
                    op = vproc.instructions.get_code(s[0].upper())
                    if op is not None:
                        op_type = i
                        break
                if op is None:
                    error(CompErrors.OP_UNK)

                vproc.ram.write(i, op, SIZE.BYTE)
                op_type = op_type.split()
                if (len(op_type)==1 and _check_reg(op_type[0])) or not len(op_type):
                    i += 1
                    continue
                elif _check_reg(op_type[0]):
                    op_type = op_type[1:]

                if len(op_type) == 1:
                    match op_type[0]:
                        case "Iv":
                            vproc.ram.write(i + 1, _to_number(s[1] if _to_number(s[1], SIZE.WORD) is not None else s[2], SIZE.WORD))
                        case "Ib":
                            vproc.ram.write(i + 1, _to_number(s[1] if _to_number(s[1], SIZE.BYTE) is not None else s[2], SIZE.BYTE))
                        case "Jv":
                            reg_label(s[1], i+1)
                else:
                    op_type = ' '.join(op_type)
                    if op_type in ['Eb Gb', 'Ev	Gv', 'Gb Eb', 'Gv Ev']:
                        if _check_reg(s[1]) and _check_reg(s[2]):
                            vproc.ram.write(i+1, _get_modRm(11, s[1].upper(), s[2].upper()))
                    elif op_type in ['Eb Ib', 'Ev Iv']:
                        pass

            else:
                error(CompErrors.UNK_SYMBOL)

        for lb, addr in use_label:
            lb



REG_16 = [
    'AX', 'BX', 'CX', 'DX',
    'SI', 'DI', 'BP', 'SP'
]
REG_8 = [
    'AH', 'BH', 'CH', 'DH',
    'AL', 'BL', 'CL', 'CL'
]
def _check_reg(txt):
    return txt.upper() in REG_16 or txt.upper() in REG_8

def _get_mb_args(operands):
    if not len(operands):
        return [""]

    sz = {
        False: SIZE.WORD,
        True: SIZE.BYTE
    }

    if len(operands) == 1:
        if _check_reg(operands[0]):
            return [operands[0].upper()]
        elif _to_number(operands[0], SIZE.WORD) is not None:
            return ['Iv']
        elif _is_name_var(operands[0]):
            return ['Jv']
        else:
            return None
    elif len(operands) == 2:
        if _check_reg(operands[0]):
            if _check_reg(operands[1]):
                s = f'{operands[0].upper()} {operands[1].upper()}'
                if operands[0].upper() in REG_8 and operands[1].upper() in REG_8:
                    return [s, "Gb Eb"]
                elif operands[0].upper() in REG_16 and operands[1].upper() in REG_16:
                    return [s, 'Gv Ev']
                else:
                    return None
            elif _to_number(operands[1], SIZE.BYTE if operands[0].upper() in REG_8 else SIZE.WORD) is not None:
                return [f"{operands[0].upper()} {'Ib' if operands[0].upper() in REG_8 else 'Iv'}"]
            # elif _is_name_var(operands[1]):
            #     return "Gv M"
            elif _get_pointer(operands[1]) is not None:
                return ["Gb Eb" if operands[0].upper() in REG_8 else "Gv Ev"]
            else:
                return None
        elif _get_pointer(operands[0]) is not None and _check_reg(operands[1]):
            return ["Eb Gb" if operands[1].upper() in REG_8 else "Ev Gv"]
    return None
