import requests
import dns.resolver
import threading
import time
import random
from typing import Set, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from modules.config import Config
from modules.utils import (
    read_wordlist,
    append_to_markdown,
    format_markdown_table,
)


class SubdomainDiscoverer:
    def __init__(self, target: str, wordlist_path: str, report_path: str, logger):
        self.target = target
        self.wordlist_path = wordlist_path
        self.report_path = report_path
        self.logger = logger
        self.found_subdomains: Set[str] = set()
        self.lock = threading.Lock()

    def discover(self):
        self.logger.info("Starting subdomain discovery...")

        threads = []

        ct_thread = threading.Thread(target=self._certificate_transparency_search)
        threads.append(ct_thread)

        dns_thread = threading.Thread(target=self._dns_brute_force)
        threads.append(dns_thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self._write_results()

    def _certificate_transparency_search(self):
        self.logger.info("Searching Certificate Transparency logs...")

        try:
            url = f"https://crt.sh/?q=%.{self.target}&output=json"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                for entry in data:
                    name_value = entry.get("name_value", "")

                    for subdomain in name_value.split("\n"):
                        subdomain = subdomain.strip().lower()

                        if subdomain and self._is_valid_subdomain(subdomain):
                            with self.lock:
                                if subdomain not in self.found_subdomains:
                                    self.found_subdomains.add(subdomain)
                                    self._write_live_result(subdomain, "CT Log")

        except Exception as e:
            self.logger.error(f"CT log search failed: {e}")

    def _dns_brute_force(self):
        self.logger.info("Starting DNS brute force...")

        try:
            wordlist = read_wordlist(self.wordlist_path)
        except Exception as e:
            self.logger.error(f"Failed to read wordlist: {e}")
            return

        with ThreadPoolExecutor(max_workers=Config.DEFAULT_THREADS) as executor:
            futures = {
                executor.submit(self._check_subdomain, word): word
                for word in wordlist
            }

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    pass

    def _check_subdomain(self, subdomain: str) -> Optional[str]:
        full_domain = f"{subdomain}.{self.target}"

        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = Config.DEFAULT_TIMEOUT
            resolver.lifetime = Config.DEFAULT_TIMEOUT

            answers = resolver.resolve(full_domain, "A")

            if answers:
                ip = str(answers[0])

                with self.lock:
                    if full_domain not in self.found_subdomains:
                        self.found_subdomains.add(full_domain)
                        self._write_live_result(full_domain, "DNS Brute Force", ip)

                return full_domain

        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            pass
        except Exception:
            pass

        time.sleep(random.uniform(0.01, 0.05))
        return None

    def _is_valid_subdomain(self, subdomain: str) -> bool:
        if subdomain == self.target:
            return False

        if subdomain.startswith("*."):
            return False

        if subdomain.endswith(f".{self.target}"):
            return True

        return False

    def _write_live_result(self, subdomain: str, method: str, ip: str = ""):
        try:
            ip_info = f" ({ip})" if ip else ""
            line = f"- {subdomain} [{method}]{ip_info}\n"
            append_to_markdown(self.report_path, line)
        except Exception as e:
            self.logger.error(f"Failed to write live result: {e}")

    def _write_results(self):
        if not self.found_subdomains:
            append_to_markdown(self.report_path, "*No subdomains found.*\n\n")
            return

        self.logger.info(f"Found {len(self.found_subdomains)} subdomains")

        sorted_subdomains = sorted(self.found_subdomains)

        headers = ["Subdomain", "IP Address"]
        rows = []

        for subdomain in sorted_subdomains:
            try:
                resolver = dns.resolver.Resolver()
                resolver.timeout = Config.DEFAULT_TIMEOUT
                answers = resolver.resolve(subdomain, "A")
                ip = str(answers[0]) if answers else "N/A"
            except:
                ip = "N/A"

            rows.append([subdomain, ip])

        table = format_markdown_table(headers, rows)
        append_to_markdown(self.report_path, table)
