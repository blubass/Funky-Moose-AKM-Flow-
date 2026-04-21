import logging
import sys
import time

class AkmLogHandler(logging.Handler):
    """Custom logging handler that pipes messages to the application UI log."""
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance

    def emit(self, record):
        try:
            msg = self.format(record)
            # Add timestamp if not already in format
            timestamp = time.strftime('%H:%M:%S')
            ui_msg = f"[{timestamp}] {msg}"
            
            # Using queue or after to ensure thread safety
            if hasattr(self.app, 'after'):
                self.app.after(0, lambda: self._write_to_ui(ui_msg))
            else:
                self._write_to_console(ui_msg)
        except Exception:
            self.handleError(record)

    def _write_to_ui(self, msg):
        if hasattr(self.app, 'log') and self.app.log:
            import tkinter as tk
            self.app.log.insert(tk.END, msg + "\n")
            self.app.log.see(tk.END)
        self._write_to_console(msg)

    def _write_to_console(self, msg):
        stream = getattr(sys, "__stderr__", None) or sys.stderr
        try:
            stream.write(msg + "\n")
            stream.flush()
        except Exception:
            pass

def setup_logging(app_instance):
    """Configures the root logger with the AKM-specific UI handler."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    # Add our UI handler
    ui_handler = AkmLogHandler(app_instance)
    formatter = logging.Formatter('%(message)s')
    ui_handler.setFormatter(formatter)
    logger.addHandler(ui_handler)
    
    logging.info("Logger System: Hochgefahren.")
