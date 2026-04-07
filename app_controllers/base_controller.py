import functools
import logging
import traceback


class BaseController:
    """
    Base class for all application controllers.
    Provides access to app, shared state, task runner, and
    utility helpers for logging, toasts, and safe error handling.
    """

    def __init__(self, app):
        self.app = app
        self.state = app.state
        self.tasks = app.tasks

    # --- LOGGING & FEEDBACK ---

    def log(self, message: str):
        """Appends a message to the application log (thread-safe via logging)."""
        logging.info(message)

    def toast(self, message: str, color=None):
        """Shows a self-dismissing toast notification on the main window."""
        from app_ui.ui_patterns import AkmToast, ACCENT
        effective_color = color or ACCENT
        AkmToast(self.app, message, color=effective_color)

    def toast_success(self, message: str):
        """Convenience: green success toast."""
        from app_ui.ui_patterns import FLAVOR_SUCCESS
        self.toast(message, color=FLAVOR_SUCCESS)

    def toast_error(self, message: str):
        """Convenience: red error toast."""
        from app_ui.ui_patterns import FLAVOR_ERROR
        self.toast(message, color=FLAVOR_ERROR)

    # --- SAFE ACTION DECORATOR ---

    @staticmethod
    def action(func):
        """
        Decorator: wraps a controller method in a try/except.
        On error: logs the full traceback, shows an error toast.
        """
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logging.error(f"Controller Fehler in {func.__name__}: {e}")
                traceback.print_exc()
                self.toast_error("AKTION FEHLGESCHLAGEN")
                return None
        return wrapper
