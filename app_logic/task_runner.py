import threading
import queue
import traceback
import logging


class TaskRunner:
    """
    Thread-safe background task executor with UI callback queue.
    All callbacks (on_success, on_error) are always dispatched on the main Tkinter thread.
    """

    def __init__(self, app):
        self.app = app
        self.queue = queue.Queue()
        self.active_tasks = 0
        self._check_queue()

    def run(self, task_func, on_success=None, on_error=None, busy_text="Arbeite..."):
        """
        Runs task_func in a background thread.
        on_success(result) and on_error(error_string) are called on the main thread.
        """
        self.active_tasks += 1
        self._update_ui()
        if busy_text:
            logging.info(busy_text)

        def _worker():
            try:
                result = task_func()
                self.queue.put(("success", result, on_success))
            except Exception as e:
                error_msg = f"{type(e).__name__}: {e}"
                logging.error(f"TaskRunner Fehler: {error_msg}")
                traceback.print_exc()
                self.queue.put(("error", error_msg, on_error))

        threading.Thread(target=_worker, daemon=True).start()

    def _update_ui(self):
        if hasattr(self.app, "update_task_indicator"):
            self.app.update_task_indicator(self.active_tasks > 0)

    def _check_queue(self):
        try:
            while True:
                status, payload, callback = self.queue.get_nowait()
                self.active_tasks = max(0, self.active_tasks - 1)
                self._update_ui()

                if status == "error" and callback is None:
                    # Default error handler: log to UI if no custom handler provided
                    from app_ui import ui_patterns
                    self.app.after(0, lambda msg=payload: self._show_default_error(msg))
                elif callback:
                    try:
                        callback(payload)
                    except Exception:
                        traceback.print_exc()

        except queue.Empty:
            pass
        self.app.after(100, self._check_queue)

    def _show_default_error(self, msg):
        """Minimal safe fallback error display when no on_error handler is set."""
        try:
            from app_ui.ui_patterns import AkmToast, FLAVOR_ERROR
            AkmToast(self.app, "FEHLER IM HINTERGRUND", color=FLAVOR_ERROR)
        except Exception:
            pass

    def parse_dnd_files(self, data):
        """Intelligently parses DND strings from various OS platforms (handles braces and spacing)."""
        import re
        if not data:
            return []
        # Handles macOS space-wrapped paths in curly braces
        files = re.findall(r'\{.*?\}|\S+', str(data))
        return [f.strip("{}") for f in files if f.strip("{}")]
