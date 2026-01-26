import threading
from queue import Queue
"""
This is the T-Cell It Basically Just Asks The User To 
Give Extra Resource To The AV
"""

class TCellManager:
    def __init__(self, max_threads=8):
        self.max_threads = max_threads
        self.queue = Queue()
        self.lock = threading.Lock()
        self.active_threads = 0

    def request_resources(self, required_threads=1):
        with self.lock:
            approved = min(required_threads, self.max_threads - self.active_threads)
            self.active_threads += approved
            return approved

    def release_resources(self, threads=1):
        with self.lock:
            self.active_threads = max(self.active_threads - threads, 0)

    def threaded_scan(self, targets, scan_func, log_func=print):
        results = []

        def worker(file_path):
            try:
                result = scan_func(file_path, log_func=log_func)
                results.append((file_path, result))
            finally:
                self.release_resources()

        threads = []
        for file_path in targets:
            approved = self.request_resources()
            if approved == 0:
                log_func("T-Cells waiting for resources...")
                while approved == 0:
                    approved = self.request_resources()
            t = threading.Thread(target=worker, args=(file_path,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        return results

