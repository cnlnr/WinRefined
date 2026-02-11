from wait_for_move_event import wait_for_move_event
from window_transparency import WindowTransparency


while True:
    is_start, hwnd = wait_for_move_event()
    if is_start:
        controller = WindowTransparency(hwnd, alpha=230, interval=0.005)
        controller.fade_to()
    else:
        try:
            controller.fade_in()
        except NameError:
            pass



