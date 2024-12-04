import ctypes, platform, win32con, win32gui

def make_title_bar_dark(win_id):
    if int(platform.version().split('.')[2]) > 17763:
        dwm = ctypes.windll.dwmapi
        if dwm.DwmSetWindowAttribute(win_id, 19, ctypes.byref(ctypes.c_int(2)), 4) != 0:
            dwm.DwmSetWindowAttribute(win_id, 20, ctypes.byref(ctypes.c_int(2)), 4)

def wndProc(oldWndProc, draw_callback, hWnd, message, wParam, lParam):
    if message == win32con.WM_SIZE:
        draw_callback()
        win32gui.RedrawWindow(hWnd, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE)
    return win32gui.CallWindowProc(oldWndProc, hWnd, message, wParam, lParam)

def setup_window_rezising_refresh(win_id, callback):
    oldWndProc = win32gui.SetWindowLong(win_id, win32con.GWL_WNDPROC, lambda *args: wndProc(oldWndProc, callback, *args))