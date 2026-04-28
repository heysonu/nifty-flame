import requests
import threading
import time
import random
from typing import List, Set, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from modules.logger import get_logger
from modules.config import Config
from modules.utils import (
    read_wordlist,
    append_to_markdown,
    format_markdown_table,
)


class DirectoryEnumerator:
    def __init__(self, target: str, wordlist_path: str, report_path: str, logger):
        self.target = target
        self.wordlist_path = wordlist_path
        self.report_path = report_path
        self.logger = logger
        self.found_dirs: Set[tuple] = set()
        self.lock = threading.Lock()

        if not target.startswith(("http://", "https://")):
            self.base_url = f"http://{target}"
        else:
            self.base_url = target

    def scan(self):
        self.logger.info("Starting directory enumeration...")

        try:
            wordlist = read_wordlist(self.wordlist_path)
        except Exception as e:
            self.logger.error(f"Failed to read wordlist: {e}")
            return

        with ThreadPoolExecutor(max_workers=Config.DEFAULT_THREADS) as executor:
            futures = {
                executor.submit(self._check_directory, word): word
                for word in wordlist
            }

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    pass

        self._write_results()

    def _check_directory(self, path: str) -> Optional[tuple]:
        if not path.startswith("/"):
            path = f"/{path}"

        url = f"{self.base_url}{path}"

        try:
            headers = {
                "User-Agent": random.choice(Config.USER_AGENTS),
            }

            response = requests.get(
                url,
                headers=headers,
                timeout=Config.DEFAULT_TIMEOUT,
                allow_redirects=True,
            )

            status_code = response.status_code
            content_length = len(response.content)
            content_type = response.headers.get("Content-Type", "unknown")

            if status_code in [200, 301, 302, 403]:
                with self.lock:
                    result = (path, status_code, content_length, content_type)
                    if result not in self.found_dirs:
                        self.found_dirs.add(result)
                        self._write_live_result(path, status_code, content_length)

                return result

        except requests.RequestException:
            pass

        time.sleep(random.uniform(0.01, 0.05))
        return None

    def _write_live_result(self, path: str, status_code: int, size: int):
        try:
            line = f"- {path} - Status: {status_code} - Size: {size} bytes\n"
            append_to_markdown(self.report_path, line)
        except Exception as e:
            self.logger.error(f"Failed to write live result: {e}")

    def _write_results(self):
        if not self.found_dirs:
            append_to_markdown(self.report_path, "*No directories found.*\n\n")
            return

        self.logger.info(f"Found {len(self.found_dirs)} directories")

        sorted_dirs = sorted(self.found_dirs, key=lambda x: x[0])

        headers = ["Path", "Status Code", "Size (bytes)", "Content-Type"]
        rows = []

        for path, status, size, content_type in sorted_dirs:
            rows.append([path, str(status), str(size), content_type])

        table = format_markdown_table(headers, rows)
        append_to_markdown(self.report_path, table)
