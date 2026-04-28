import socket
import threading
import time
import struct
from typing import List, Set, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from modules.logger import get_logger
from modules.config import Config
from modules.utils import (
    append_to_markdown,
    format_markdown_table,
    format_markdown_code,
)


class PortScanner:
    COMMON_SERVICES = {
        21: "ftp",
        22: "ssh",
        23: "telnet",
        25: "smtp",
        53: "domain",
        80: "http",
        110: "pop3",
        111: "rpcbind",
        135: "msrpc",
        139: "netbios-ssn",
        143: "imap",
        443: "https",
        445: "microsoft-ds",
        993: "imaps",
        995: "pop3s",
        1723: "pptp",
        3306: "mysql",
        3389: "ms-wbt-server",
        5900: "vnc",
        8080: "http-proxy",
        8443: "https-alt",
        8888: "cddbp",
        9000: "cslistener",
        9090: "zeus-admin",
        10000: "snet-sensor-mgmt",
    }

    def __init__(self, target: str, report_path: str, logger):
        self.target = target
        self.report_path = report_path
        self.logger = logger
        self.open_ports: Set[tuple] = set()
        self.lock = threading.Lock()
        self.os_info: Optional[str] = None

    def scan(self):
        self.logger.info("Starting port scanning...")

        ports = Config.TOP_PORTS

        with ThreadPoolExecutor(max_workers=Config.DEFAULT_THREADS) as executor:
            futures = {
                executor.submit(self._scan_port, port): port
                for port in ports
            }

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    pass

        self._detect_os()
        self._write_results()

    def _scan_port(self, port: int) -> Optional[tuple]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(Config.DEFAULT_TIMEOUT)

            result = sock.connect_ex((self.target, port))

            if result == 0:
                service = self.COMMON_SERVICES.get(port, "unknown")
                version = self._grab_banner(sock, port)

                with self.lock:
                    port_info = (port, service, version)
                    if port_info not in self.open_ports:
                        self.open_ports.add(port_info)
                        self._write_live_result(port, service, version)

                sock.close()
                return port_info

            sock.close()

        except Exception:
            pass

        return None

    def _grab_banner(self, sock: socket.socket, port: int) -> str:
        try:
            if port in [21, 22, 25, 110, 143, 3306, 5900]:
                sock.send(b"\r\n")
                banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
                return banner[:100] if banner else ""
            elif port in [80, 443, 8080, 8443]:
                sock.send(b"GET / HTTP/1.1\r\nHost: " + self.target.encode() + b"\r\n\r\n")
                response = sock.recv(1024).decode("utf-8", errors="ignore")
                if "Server:" in response:
                    server_line = [line for line in response.split("\n") if "Server:" in line]
                    if server_line:
                        return server_line[0].split(":")[1].strip()[:100]
                return ""
            return ""
        except Exception:
            return ""

    def _detect_os(self) -> Optional[str]:
        self.logger.info("Attempting OS detection...")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW)
            sock.settimeout(Config.DEFAULT_TIMEOUT)

            ttl_values = []
            window_sizes = []

            for port in [80, 443, 22]:
                try:
                    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_sock.settimeout(Config.DEFAULT_TIMEOUT)
                    test_sock.connect((self.target, port))

                    test_sock.send(b"GET / HTTP/1.1\r\nHost: " + self.target.encode() + b"\r\n\r\n")

                    try:
                        data = test_sock.recv(1024)
                        if data:
                            ttl_values.append(self._extract_ttl(data))
                    except:
                        pass

                    test_sock.close()
                    time.sleep(0.1)

                except:
                    pass

            if ttl_values:
                avg_ttl = sum(ttl_values) / len(ttl_values)
                self.os_info = self._guess_os_from_ttl(avg_ttl)

        except Exception as e:
            self.logger.debug(f"OS detection failed: {e}")

        return self.os_info

    def _extract_ttl(self, packet: bytes) -> int:
        try:
            if len(packet) >= 20:
                ttl = packet[8]
                return ttl
        except:
            pass
        return 64

    def _guess_os_from_ttl(self, ttl: int) -> str:
        if ttl <= 32:
            return "Windows (TTL ~32)"
        elif ttl <= 64:
            return "Linux/Unix (TTL ~64)"
        elif ttl <= 128:
            return "Windows (TTL ~128)"
        else:
            return "Unknown/Network Device (TTL ~255)"

    def _write_live_result(self, port: int, service: str, version: str):
        try:
            version_info = f" - {version}" if version else ""
            line = f"- {port}/{service}{version_info}\n"
            append_to_markdown(self.report_path, line)
        except Exception as e:
            self.logger.error(f"Failed to write live result: {e}")

    def _write_results(self):
        if not self.open_ports:
            append_to_markdown(self.report_path, "*No open ports found.*\n\n")
            return

        self.logger.info(f"Found {len(self.open_ports)} open ports")

        sorted_ports = sorted(self.open_ports, key=lambda x: x[0])

        nmap_style_output = "PORT\t\tSTATE\tSERVICE\t\tVERSION\n"
        nmap_style_output += "-" * 60 + "\n"

        for port, service, version in sorted_ports:
            version_str = version if version else ""
            nmap_style_output += f"{port}/{service}\topen\t{service}\t\t{version_str}\n"

        nmap_output = format_markdown_code(nmap_style_output, "")
        append_to_markdown(self.report_path, nmap_output)

        if self.os_info:
            os_section = f"\n**OS Detection:** {self.os_info}\n\n"
            append_to_markdown(self.report_path, os_section)

        headers = ["Port", "Service", "Version"]
        rows = []

        for port, service, version in sorted_ports:
            rows.append([str(port), service, version if version else ""])

        table = format_markdown_table(headers, rows)
        append_to_markdown(self.report_path, table)
