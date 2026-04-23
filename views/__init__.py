"""Views package for the Car Key Fob application.

All PyQt6 widgets live here. Views receive references to controllers, not
models, so the user interface remains decoupled from the persistence layer.
"""

from views.main_window import MainWindow

__all__ = ["MainWindow"]
