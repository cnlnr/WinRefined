import ctypes
import psutil

kernel32 = ctypes.windll.kernel32

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_ulong),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_ulong),
        ("Protect", ctypes.c_ulong),
        ("Type", ctypes.c_ulong),
    ]


def check_memory(pid, address):
    h_process = kernel32.OpenProcess(0x10, False, pid)
    mbi = MEMORY_BASIC_INFORMATION()

    res = kernel32.VirtualQueryEx(
        h_process,
        ctypes.c_void_p(address),
        ctypes.byref(mbi),
        ctypes.sizeof(mbi)
    )

    if res:
        print("内存基址:", hex(mbi.BaseAddress))
        print("保护属性 Protect:", hex(mbi.Protect))
        print("类型 Type:", hex(mbi.Type))
    else:
        print("查询失败")

    kernel32.CloseHandle(h_process)


# 调用
pid = 13500
addr = 0x15F75FC3244
check_memory(pid, addr)