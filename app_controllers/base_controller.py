import functools
import traceback

class BaseController:
    """Base class for all application controllers with access to the main app instance."""
    def __init__(self, app):
        self.app = app
        self.state = app.state
        self.tasks = app.tasks
        
    def log(self, message):
        self.app.append_log(message)
    
    def toast(self, message, color=None):
        from app_ui.ui_patterns import AkmToast
        AkmToast(self.app, message, color=color)

    @staticmethod
    def action(func):
        """Enforces robust error handling and logging for controller actions."""
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                err_msg = f"SYSTEM FEHLER: {str(e)}"
                self.log(err_msg)
                print(traceback.format_exc())
                from app_ui.ui_patterns import FLAVOR_ERROR
                self.toast("AKTION FEHLGESCHLAGEN", color=FLAVOR_ERROR)
                return None
        return wrapper
