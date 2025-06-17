from vproc.v8086 import *
from vproc.comp import *

vproc = proc()
comp = CompileProg("test.asm")
comp.compile(vproc)

while True:
    s = input("Введите команду(next, show, exit): ")

    match s:
        case "next":
            vproc.next()
        case "show":
            print('Регистры общего назначения:')
            print(f"AX: {vproc.reg.ax.val:04X} | BX: {vproc.reg.bx.val:04X}")
            print(f"CX: {vproc.reg.cx.val:04X} | DX: {vproc.reg.dx.val:04X}")
            print('Индексные регистры')
            print(f"SI: {vproc.reg.si.val:04X} | DI: {vproc.reg.di.val:04X}")
            print('Указательные регистры:')
            print(f'IP: {vproc.reg.ip.val:04X}')
            print(f'BP: {vproc.reg.bp.val:04X} | SP: {vproc.reg.sp.val:04X}')
            print('Флаги:')
            print(f"{vproc.flags.val:08b}")
            print('Сегментные:')
            print(f'CS: {vproc.reg.cs.val:04X} | DS: {vproc.reg.ds.val:04X}')
            # print(f'ES: {vproc.reg.es.val:04X} | SS:')

        case "exit":
            exit()

