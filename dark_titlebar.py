import ctypes, platform

def make_title_bar_dark(win_id):
    if int(platform.version().split('.')[2]) > 17763:
        dwm = ctypes.windll.dwmapi
        if dwm.DwmSetWindowAttribute(win_id, 19, ctypes.byref(ctypes.c_int(2)), 4) != 0:
            dwm.DwmSetWindowAttribute(win_id, 20, ctypes.byref(ctypes.c_int(2)), 4)