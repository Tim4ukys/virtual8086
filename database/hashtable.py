
class _List:
    key : str = None
    data = None
    next = None
    def __init__(self, key, data):
        self.key = key
        self.data = data

def _jenkins_hash(text : str):
    BIT_64 = 0xFFFF_FFFF_FFFF_FFFF # или лучше 32?
    hash = 0
    for i in text:
        hash = (hash + ord(i)) & BIT_64
        hash = (hash << 10) & BIT_64
        hash ^= (hash >> 6)
    hash = (hash + (hash << 3)) & BIT_64
    hash ^= (hash >> 11)
    hash = (hash + (hash << 15)) & BIT_64
    return hash

class _Table:
    size = 0
    get_key = None
    table : list = None
    def __init__(self, sz, hash_func):
        def get_key(str):
            return hash_func(str) % sz
        self.get_key = get_key
        self.size = sz
        self.table = [None for _ in range(sz)]

def _tab_empty(tab : _Table):
    for i in tab.table:
        if i:
            return False
    return True

def _tab_set(tab : _Table, key : str, data, dtor):
    k = tab.get_key(key)
    ls = tab.table[k]
    if not ls:
        tab.table[k] = _List(key, data)
        return

    while True:
        if ls.key == key:
            if dtor:
                dtor(ls.data)
            data, ls.data = ls.data, data
            return data
        if ls.next is None:
            break
        ls = ls.next

    ls.next = _List(key, data)

def _tab_get(tab : _Table, key : str):
    k = tab.get_key(key)
    ls = tab.table[k]
    while ls:
        if ls.key == key:
            return ls.data
        ls = ls.next

def _tab_delete(tab : _Table, key : str, dtor):
    k = tab.get_key(key)
    ls = tab.table[k]
    parent = None
    while ls:
        if ls.key == key:
            save_data = ls.data
            if dtor:
                dtor(ls.data)
            if parent:
                parent.next = ls.next
            else:
                tab.table[k] = ls.next
            return save_data
        ls = ls.next

class HashTable:
    tabs : list = None # самый актуальный будет в конце
    hash_func = None
    dtor = None
    count = 0

# Создать хеш таблицу
def ht_init(size, hash_func = None, destructor = None):
    ht = HashTable()
    if size <= 0:
        return
    ht.hash_func = hash_func if hash_func else _jenkins_hash
    if destructor:
        ht.dtor = destructor
    ht.tabs = list([_Table(size, ht.hash_func)])
    return ht

# Уничтожить таблицу
def ht_destroy(ht : HashTable):
    if ht.dtor:
        def dest(_, data):
            ht.dtor(data)
        ht_traverse(ht, dest)
        ht.dtor = None
    ht.tabs.clear()
    ht.hash_func = None

def _ht_remove_empty_tabs(ht : HashTable, idx):
    i = 0
    while i < idx:
        if _tab_empty(ht.tabs[i]):
            ht.tabs.remove(ht.tabs[i])
        else:
            i += 1

def _ht_refresh(ht : HashTable, key : str):
    save_data = None
    for tb in ht.tabs[0:-1]:
        save_data = _tab_delete(tb, key, ht.dtor)
        if save_data:
            break

    _ht_remove_empty_tabs(ht, len(ht.tabs) - 1)
    return save_data

# Записать в таблицу key -> data
def ht_set(ht : HashTable, key : str, data):
    save_data = _ht_refresh(ht, key)
    if not save_data and not ht_has(ht, key):
        ht.count += 1
        _ht_keep_size_normal(ht)
    tb = ht.tabs[-1]
    r = _tab_set(tb, key, data, ht.dtor)
    return save_data if save_data else r

# Получить значение по ключу. Если ключа нет в таблице, вернуть 0.
def ht_get(ht : HashTable, key : str):
    save_data = _ht_refresh(ht, key)
    if save_data:
        _tab_set(ht.tabs[-1], key, save_data, ht.dtor)
    else:
        save_data = _tab_get(ht.tabs[-1], key)
    return save_data

# Проверка существования ключа key в таблице. True - есть, False - нет.
def ht_has(ht : HashTable, key : str):
    return ht_get(ht, key) is not None

# Удалить элемент с ключом key из таблицы (если он есть)
def ht_delete(ht : HashTable, key : str):
    for tb in ht.tabs:
        sv = _tab_delete(tb, key, ht.dtor)
        if sv:
            ht.count -= 1
            _ht_keep_size_normal(ht)
            return sv

# Обход таблицы с посещением всех элементов.
def ht_traverse(ht : HashTable, f):
    for i in ht.tabs[-1].table:
        ls = i
        while ls:
            f(ls.key, ls.data)
            ls = ls.next

    for tb in ht.tabs[0:-1]:
        for i in tb.table:
            ls = i
            while ls:
                _tab_set(ht.tabs[-1], ls.key, ls.data, ht.dtor)
                f(ls.key, ls.data)
                ls = ls.next
    ht.tabs = ht.tabs[-1:]

# Изменить размер базового массива.
def _ht_resize(ht : HashTable, new_size):
    if new_size <= 0:
        return
    _ht_remove_empty_tabs(ht, len(ht.tabs))
    ht.tabs.append(_Table(new_size, ht.hash_func))

def _ht_keep_size_normal(ht : HashTable):
    k = ht.count / ht.tabs[-1].size
    norma = [0.25, 0.75]
    if k < norma[0]:
        _ht_resize(ht, ht.tabs[-1].size//2)
    elif k > norma[1]:
        _ht_resize(ht, ht.tabs[-1].size*2)

def ht_full_refresh(ht : HashTable):
    def emp(a, b):
        pass
    ht_traverse(ht, emp)
