from ime_state import monitor_ime_state
from pinyin_segmentation import start_auto_quote

listener = None

for state in monitor_ime_state():
    # 1. 优先判断大写锁定（最高优先级）
    if state is None:
        if listener is not None:
            listener.stop()
            listener = None
    # 2. 其次判断中文输入法
    elif state:
        if listener is None:
            listener = start_auto_quote()
    # 3. 最后是英文输入法
    else:
        if listener is not None:
            listener.stop()
            listener = None