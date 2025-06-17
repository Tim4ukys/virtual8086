from vproc.memblock import *

def test_word_write_get_bit():
    mem = Word()
    for i in range(16):
        assert not mem.get_bit(i)
        mem.set_bit(i, 1)
        assert mem.val == int('1' * (i + 1), 2)
        assert mem.get_bit(i)
    for i in range(16):
        mem.set_bit(i, 0)
        assert mem.val == int('1' * (16 - i - 1) + '0' * (i + 1), 2)
        assert not mem.get_bit(i)

def test_word_high_low():
    mem = Word()
    for i in range(0xff+1):
        mem.write_high(i)
        assert mem.get_high() == i
        assert mem.val == (i << 8)
    for i in range(0xff+1):
        mem.write_low(i)
        assert mem.get_low() == i
        assert mem.val == 0xff00 | i

def test_memory_write_read():
    mem = Memory(0x6)
    assert mem.write(0x0, 0xaa, SIZE.BYTE)
    assert mem.write(0x1, 0xcc_bb, SIZE.WORD)
    assert mem.write(0x3, 0xaa_dd, SIZE.BYTE)
    assert mem.write(0x4, 0xee_ff, SIZE.WORD)

    assert [mem.read(i, SIZE.BYTE) for i in range(6)] == [0xaa, 0xbb, 0xcc, 0xdd, 0xff, 0xee]
    assert [mem.read(i, SIZE.WORD) for i in range(5)] == [0xBBAA, 0xCCBB, 0xDDCC, 0xFFDD, 0xEEFF]

    assert not mem.write(0x6, 0xee, SIZE.BYTE)
    assert mem.read(0x6, SIZE.BYTE) is None
    assert not mem.write(0x5, 0xff_ff, SIZE.WORD)
    assert mem.read(0x5, SIZE.WORD) is None


def test_to_sign():
    assert to_sign(255, 1) == -1
    assert to_unsign(to_sign(250, 1), 1) == 250