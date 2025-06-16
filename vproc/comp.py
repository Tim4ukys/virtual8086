import database.hashtable as ht
from instructions import _remove_comments
from memblock import SIZE

def _check_brackets(expression):
    stack = list()
    brck = {"}": "{", "]": "[", ')': '(', '>': '<'}

    for i in expression:
        if i in brck.values():
            stack.append(i)
        elif i in brck.keys() and stack.pop() != brck[i]:
            return 0
    return 1

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
    if not (('A' <= text[0] <= 'Z') or ('a' <= text <= 'z')):
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
        decode = decode['d' if text[-1] not in decode else text[-1]](text)
        if decode >= 2 ** (8 * sz):
            return None
        return decode
    except ValueError:
        return None

class CompileProg:
    labels = None
    lines = None

    def __init__(self, file_name):
        with open(file_name) as f:
            self.lines = [[i, _remove_comments(s).split()] for i, s in enumerate(f.readlines(), start=1) if len(_remove_comments(s).split())]

    def analysis(self):
        wrongs = {
            "more_uses": [], # множественное использование
        }
        RESERVE_ONE = ['stack']
        RESERVE_MORE = ['org',
                        'segment',
                        'db', 'dw',
                        'resb', 'resw']
        res_check = {i: 0 for i in RESERVE_ONE}
        labels = []
        for i, s in self.lines:
            if s in RESERVE_ONE:
                if not res_check[s]:
                    res_check[s] = 1
                else:
                    wrongs["more_uses"].append(i)

    def compile(self, vproc):
        labels = ht.ht_init(2)
        vproc.reset_registers()
        vproc.reset_flags()

        # stack сюда надо засунуть
        # юзануть warnings???
        errors = []

        i = 0x100
        cur_segment = ''
        for number, s in self.lines:
            # s = [*mnemonic*, *operands*]
            # и т.п.
            add_errors = lambda err: errors.append(f"{number}: {err}")

            # first = s[0]
            if vproc.instructions.is_mnem(s[0]):
                if not vproc.reg.cs.val:
                    vproc.reg.cs.val = i
                    cur_segment = '.text'
                args = ' '.join(s[1:]).translate({ord(' '): '', ord('['): ',['}).split(',')

                # если нет операндов
                if len(args) == 0:
                    op = vproc.instructions.get_code(s[0], '')
                    if not op:
                        add_errors("некоректный аргумент")
                    else:
                        vproc.ram.write(i, op, SIZE.BYTE)
                        i += 1
                    continue
                opernds = []
                # если операндов несколько
                for i in s[1:]:
                    regs = (
                        'AX', 'BX', 'CX', 'DX',

                        'AH', 'BH', 'CH', 'DH',
                        'AL', 'BL', 'CL', 'CL',

                        'SI', 'DI', 'BP', 'SP'
                    )
                    if s[1].upper()


            elif s[0] == 'segment':
                if len(s) > 2:
                    add_errors("много текста")
                    # break
                    continue
                seg = {
                    ".text": vproc.reg.cs,
                    ".data": vproc.reg.ds,
                    ".edata": vproc.reg.es,
                    ".stack": vproc.reg.ss
                }
                if s[1] in seg:
                    if seg[s[1]]:
                        seg[s[1]].val = i
                        cur_segment = s[1]
                        # continue
                    elif s[1] == '.text':
                        add_errors("сегмент указан дважды или какие-то инструкции написаны перед ним")
                    else:
                        add_errors("сегмент указан дважды")
                else:
                    add_errors("непонятный сегмент")
                # break
            elif _is_name_var(s[0]):
                sz = {'db': SIZE.BYTE, 'dw': SIZE.WORD}
                if s[1] not in sz:
                    add_errors("ЧТО ЭТО ЗА СЛОВОО?")
                elif len(s) < 2:
                    add_errors("а сами цифры где?")
                elif cur_segment not in ['.data', '.edata']:
                    add_errors('переменные вне соответсвующих сегментов')
                else:
                    for numb in s[3:]:
                        numb = _to_number(numb, sz[s[1]].value)
                        if not numb:
                            add_errors('некорректное число в строке')
                            break
                        vproc.ram.write(i, numb, sz[s[1]])
                        i += sz[s[1]].value
                # break
            elif _is_label(s[0]):
                if len(s) > 1:
                    add_errors('слишком много слов')
                elif cur_segment != '.text':
                    add_errors('метки перехода должны быть строга в сегменте кода (.text)')
                elif ht.ht_has(labels, s[:-1]):
                    add_errors('метка уже существует')
                else:
                    ht.ht_set(labels, s[:-1], i)
                    # continue
                # break
            else:
                add_errors('непонятный символ')
                # break





