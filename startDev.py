import sys
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command

    def on_any_event(self, event):
        print(f"Change detected: {event.src_path}")
        self.restart()

    def restart(self):
        if hasattr(self, "process"):
            self.process.kill()
        self.process = subprocess.Popen(self.command)


if __name__ == "__main__":
    path = "."  # The directory to watch
    command = [sys.executable, "app.py"]  # Command to run your bot

    event_handler = ChangeHandler(command)
    event_handler.restart()  # Start the process for the first time

    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
