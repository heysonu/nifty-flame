import os
from pathlib import Path


class Config:
    DEFAULT_THREADS = 50
    DEFAULT_TIMEOUT = 3
    DEFAULT_OUTPUT_DIR = "output"
    DEFAULT_WORDLIST_DIR = "wordlists"
    DEFAULT_DIR_WORDLIST = "wordlists/common_dirs.txt"
    DEFAULT_SUBDOMAIN_WORDLIST = "wordlists/common_subdomains.txt"

    COMMON_PORTS = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
        1723, 3306, 3389, 5900, 8080, 8443, 8888, 9000, 9090, 10000
    ]

    TOP_PORTS = list(range(1, 1025))

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    ]

    @staticmethod
    def get_project_root():
        return Path(__file__).parent.parent

    @staticmethod
    def get_output_dir():
        output_dir = Config.get_project_root() / Config.DEFAULT_OUTPUT_DIR
        output_dir.mkdir(exist_ok=True)
        return output_dir

    @staticmethod
    def get_wordlist_dir():
        return Config.get_project_root() / Config.DEFAULT_WORDLIST_DIR

    @staticmethod
    def validate_wordlist(path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Wordlist not found: {path}")
        if not os.path.isfile(path):
            raise ValueError(f"Wordlist is not a file: {path}")
        return True
