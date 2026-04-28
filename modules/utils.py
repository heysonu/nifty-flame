import re
import os
import json
import time
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional


def validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_target(target: str) -> str:
    if validate_url(target):
        parsed = urlparse(target)
        return parsed.netloc
    return target


def get_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def generate_output_filename(method: str, target: str) -> str:
    timestamp = get_timestamp()
    clean_target = target.replace("://", "_").replace("/", "_").replace(".", "_")
    return f"{method}_{clean_target}_{timestamp}.md"


def read_wordlist(path: str) -> list:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def write_markdown_file(path: str, content: str, mode: str = "w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, encoding="utf-8") as f:
        f.write(content)


def append_to_markdown(path: str, content: str):
    write_markdown_file(path, content, mode="a")


def format_markdown_header(title: str, level: int = 1) -> str:
    return f"{'#' * level} {title}\n\n"


def format_markdown_table(headers: list, rows: list) -> str:
    if not rows:
        return ""

    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    for row in rows:
        table += "| " + " | ".join(str(cell) for cell in row) + " |\n"

    return table + "\n"


def format_markdown_list(items: list) -> str:
    return "\n".join(f"- {item}" for item in items) + "\n\n"


def format_markdown_code(code: str, language: str = "") -> str:
    return f"```{language}\n{code}\n```\n\n"


def is_valid_domain(domain: str) -> bool:
    pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return bool(re.match(pattern, domain))


def is_valid_ip(ip: str) -> bool:
    pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    return bool(re.match(pattern, ip))


def get_file_size(path: str) -> int:
    return os.path.getsize(path)


def ensure_dir_exists(path: str):
    os.makedirs(path, exist_ok=True)
