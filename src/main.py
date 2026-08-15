import sys
import os
import flet as ft

# Add workspace directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.app import main

if __name__ == "__main__":
    ft.app(target=main)
