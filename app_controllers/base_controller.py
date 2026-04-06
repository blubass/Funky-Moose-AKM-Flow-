
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
