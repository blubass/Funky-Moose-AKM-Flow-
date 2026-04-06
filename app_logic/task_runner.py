import threading
import queue
import traceback

class TaskRunner:
    def __init__(self, app):
        self.app = app
        self.queue = queue.Queue()
        self.active_tasks = 0
        self._check_queue()

    def run(self, task_func, on_success=None, on_error=None, busy_text="Arbeite..."):
        self.active_tasks += 1
        self._update_ui()
        
        def worker():
            try:
                result = task_func()
                self.queue.put(("success", result, on_success))
            except Exception as e:
                self.queue.put(("error", str(e), on_error))
                traceback.print_exc()

        threading.Thread(target=worker, daemon=True).start()
        if hasattr(self.app, 'append_log') and busy_text:
            self.app.append_log(busy_text)

    def _update_ui(self):
        if hasattr(self.app, 'update_task_indicator'):
            self.app.update_task_indicator(self.active_tasks > 0)

    def _check_queue(self):
        try:
            while True:
                status, payload, callback = self.queue.get_nowait()
                self.active_tasks = max(0, self.active_tasks - 1)
                self._update_ui()
                
                if callback:
                    try:
                        callback(payload)
                    except Exception as e:
                        traceback.print_exc()
        except queue.Empty:
            pass
        self.app.after(100, self._check_queue)

    def parse_dnd_files(self, data):
        """Intelligently parses DND strings from various OS platforms (handles braces and spacing)."""
        import re
        if not data: return []
        # Handles macOS space wrapping in curly braces
        files = re.findall(r'\{.*?\}|\S+', str(data))
        return [f.strip('{}') for f in files]
