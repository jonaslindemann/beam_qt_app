# -*- coding: utf-8 -*-
"""
Modul med diverse hjälpfunktioner för att hantera strängar, tal och listor.
"""

import os, sys
import ctypes


def try_float(text, default=0.0):
    try:
        return float(text)
    except ValueError:
        return default
    
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def close_console():
    if os.name != 'nt':
        return
    
    kernel32 = ctypes.WinDLL('kernel32')
    console_hwnd = kernel32.GetConsoleWindow()
    
    if console_hwnd != 0:
        # This will properly close the console window
        kernel32.FreeConsole()

