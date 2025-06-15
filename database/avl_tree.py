from collections import deque

class _Node:
    def __init__(self, data):
        self.data = data

    left = None
    right = None
    data = None

# ~~~~~~~~~~~~~~~~~~~~~~

def _lr(a : _Node):
    a.right, a.left = a.left, a.right
    b = a.left
    b.left, b.right = b.right, b.left
    b.left, a.right = a.right, b.left
    a.data, b.data = b.data, a.data

def _rr(a : _Node):
    a.right, a.left = a.left, a.right
    b = a.right
    b.left, b.right = b.right, b.left
    a.left, b.right = b.right, a.left
    a.data, b.data = b.data, a.data

# ~~~~~~~~~~~~~~~~~~~~~~

class Tree:
    root = None
    cmpFunc = None

# ~~~~~~~~~~~~~~~~~~~~~~

def create(cmp_function):
    if not cmp_function:
        return None
    r = Tree()
    r.cmpFunc  = cmp_function
    return r

# ~~~~~~~~~~~~~~~~~~~~~~
def _height(tr : _Node):
    if not tr:
        return 0
    deq = deque()
    deq.append(tr)
    ans = 0
    while len(deq) > 0:
        c = len(deq)
        while c > 0:
            ch = deq.popleft()
            c -= 1
            if ch.left: deq.append(ch.left)
            if ch.right: deq.append(ch.right)
        ans += 1
    return ans


def _fix_balance(tr : _Node):
    r_height, l_height = _height(tr.right), _height(tr.left)
    balance = r_height - l_height
    if balance > 1: # lr
        b = tr.right
        if _height(b.left) > _height(b.right):
            _rr(tr.right)
        _lr(tr)
    elif balance < -1: # rr
        b = tr.left
        if _height(b.right) > _height(b.left):
            _lr(tr.left)
        _rr(tr)

def insert(tr : Tree, data):
    if not tr:
        return None
    if not tr.root:
        tr.root = _Node(data)
        return None

    # Ищу куда вставить
    ch = tr.root
    parents = list()
    while True:
        cmp = tr.cmpFunc(data, ch.data)
        if cmp == 0:
            sv_data, ch.data = ch.data, data
            return sv_data
        parents.append(ch)
        if cmp < 0:
            if not ch.left:
                ch.left = _Node(data)
                break
            else:
                ch = ch.left
        else:
            if not ch.right:
                ch.right = _Node(data)
                break
            else:
                ch = ch.right

    # Балансировка
    while parents:
        _fix_balance(parents.pop())

def delete(tr : Tree, data):
    if not tr:
        return

    ch = tr.root
    save_data = None
    parents = list()

    while True:
        if not ch:
            return None
        cmp = tr.cmpFunc(data, ch.data)
        if cmp < 0:
            parents.append(ch)
            ch = ch.left
            continue
        elif cmp > 0:
            parents.append(ch)
            ch = ch.right
            continue
        break

    save_data = ch.data

    if not ch.right and not ch.left:
        if len(parents) == 0:
            tr.root = None
        elif tr.cmpFunc(ch.data, parents[-1].data) < 0:
            parents[-1].left = None
        else:
            parents[-1].right = None
    elif not ch.right:
        ch.data, ch.left = ch.left.data, None
    elif not ch.left:
        ch.data, ch.right = ch.right.data, None
    else:
        parents.append(ch)
        min_ch = ch.right
        if not min_ch.left:
            if not min_ch.right:
                ch.data = min_ch.data
                ch.right = None
            else:
                ch.data, min_ch.data = min_ch.data, min_ch.right.data
                min_ch.right = None
        else:
            while min_ch.left:
                parents.append(min_ch)
                min_ch = min_ch.left
            if min_ch.right:
                ch.data, min_ch.data = min_ch.data, min_ch.right.data
                min_ch.right = None
            else:
                ch.data = min_ch.data
                parents[-1].left = None

    while parents:
        _fix_balance(parents.pop())
    return save_data


def foreach(tr : Tree, func):
    if not tr:
        return
    stack = []
    ch = tr.root
    while len(stack) > 0 or ch:
        while ch:
            stack.append(ch)
            ch = ch.left
        ch = stack.pop()
        func(ch.data)
        ch = ch.right

def find(tr : Tree, data):
    if not tr:
        return None
    ch = tr.root
    while ch:
        cmp = tr.cmpFunc(data, ch.data)
        if cmp == 0:
            return ch.data
        elif cmp < 0:
            ch = ch.left
        else:
            ch = ch.right
    return None

def size(tr : Tree):
    sz = 0
    if not tr:
        return sz
    stack = []
    ch = tr.root
    while len(stack) > 0 or ch:
        while ch:
            stack.append(ch)
            ch = ch.left
        ch = stack.pop()
        sz += 1
        ch = ch.right
    return sz


def clear(tr : Tree):
    if tr:
        tr.root = None
