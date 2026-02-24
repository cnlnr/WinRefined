from ime_state import monitor_ime_state
from pinyin_segmentation import start_auto_quote

listener = start_auto_quote()

for state in monitor_ime_state():
    if state is None:
         # 大写锁定
         listener.stop()
    elif state:
         # 中文输入法
         listener = start_auto_quote()
    else:
         # 英文输入法
        listener.stop()