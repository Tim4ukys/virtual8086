import database.hashtable as ht


def _check_brackets(expression):
    stack = list()
    brck = {"}": "{", "]": "[", ')': '(', '>': '<'}

    for i in expression:
        if i in brck.values():
            stack.append(i)
        elif i in brck.keys() and stack.pop() != brck[i]:
            return 0
    return 1


class CompiledProg:
    labels = ht.ht_init(8)
    lines = None

    def __init__(self, file_name):
        with open(file_name) as f:
            self.lines = [[i, s.split()] for i, s in enumerate(f.readlines(), start=1) if len(s.split())]

    def analysis(self):
        wrongs = {
            "more_uses": [], # множественное использование
            ""
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








#def check_file()

#def compile(file_name, vproc):




