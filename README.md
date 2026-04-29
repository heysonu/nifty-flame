<div align="center">

# 🔥 Nifty Flame

### A Powerful Python3 Pentesting Reconnaissance Tool

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT%20License-orange.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)]()

**Nifty Flame** is a comprehensive reconnaissance tool designed for security professionals conducting authorized security assessments. It helps identify potential attack surfaces through directory enumeration, subdomain discovery, and port scanning.

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Examples](#-examples) • [Output](#-output)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Directory Enumeration** | Discover hidden directories and files with multi-threaded scanning |
| 🌐 **Subdomain Discovery** | Find subdomains via Certificate Transparency logs and DNS brute force |
| 🚪 **Port Scanning** | Scan for open ports with service detection and OS fingerprinting |
| 📝 **Live Markdown Reports** | Results saved to `.md` files with real-time updates |
| ⚡ **Multi-threaded Scanning** | Fast and efficient scanning with configurable thread counts |
| 📚 **Interactive Wordlists** | Choose custom wordlists or use built-in defaults |
| 🎨 **Color-coded Output** | Beautiful console output with colorama |
| 🎯 **Nmap-style Results** | Port scanner output resembles `nmap -sC -sV` |

---

## 🚀 Installation

### Prerequisites

- ✅ Python 3.7 or higher
- ✅ pip (Python package manager)

### Quick Start

<details>
<summary><strong>📦 Install Dependencies</strong></summary>

```bash
# Clone or navigate to the project directory
cd NewTool

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

</details>

<details>
<summary><strong>⚙️ Make Executable</strong></summary>

```bash
chmod +x nifty-flame
```

</details>

---

## 📖 Usage

### Basic Syntax

```bash
python3 nifty-flame [FLAGS] -u <target>
```

### Command Flags

| Flag | Description | Required |
|------|-------------|----------|
| `-p` | Enable port scanning | No |
| `-s` | Enable subdomain discovery | No |
| `-d` | Enable directory enumeration | No |
| `-u <target>` | Target URL or domain | **Yes** |
| `-w` | Interactive wordlist selection | No |

> **Note:** At least one scanning method (`-p`, `-s`, or `-d`) must be enabled.

---

## 💡 Examples

### 🎯 Run All Methods with Default Wordlists

```bash
python3 nifty-flame -psd -u example.com
```

### 🔧 Run Port and Subdomain Scanning Only

```bash
python3 nifty-flame -ps -u example.com
```

### 📁 Run Directory Enumeration with Custom Wordlist

```bash
python3 nifty-flame -d -u http://example.com -w
```

When `-w` is used, you'll be prompted to enter the path for the wordlist (or press Enter for default).

### 🎨 Run All Methods with Custom Wordlists

```bash
python3 nifty-flame -psd -u example.com -w
```

---

## 📊 Output

Results are automatically saved to markdown files in the `output/` directory with **live updates**:

| File | Description |
|------|-------------|
| `ports_<target>_<timestamp>.md` | Port scan results with OS detection |
| `subdomains_<target>_<timestamp>.md` | Subdomain discovery results |
| `directories_<target>_<timestamp>.md` | Directory enumeration results |

### Output Format

The port scanner output resembles nmap's `-sC -sV` style:

```text
PORT     STATE    SERVICE        VERSION
22/tcp   open     ssh            OpenSSH 8.2p1
80/tcp   open     http           nginx/1.18.0
443/tcp  open     https          nginx/1.18.0

OS Detection: Linux/Unix (TTL ~64)
```

---

## 📚 Wordlists

Default wordlists are included in the `wordlists/` directory:

| Wordlist | Entries | Description |
|----------|---------|-------------|
| `common_dirs.txt` | ~100 | Common directory names |
| `common_subdomains.txt` | ~200 | Common subdomain names |

You can provide your own wordlists using the `-w` flag.

---

## 🏗️ Project Structure

```
NewTool/
├── nifty-flame              # Main executable script
├── modules/                # Core modules
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── logger.py           # Color-coded logging
│   ├── utils.py            # Shared utilities & markdown helpers
│   ├── directory_enum.py   # Directory enumeration module
│   ├── subdomain.py        # Subdomain discovery module
│   └── port_scanner.py     # Port scanning module
├── wordlists/             # Default wordlists
│   ├── common_dirs.txt
│   └── common_subdomains.txt
├── output/                # Output directory for .md files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🔒 Security Considerations

> ⚠️ **IMPORTANT:** This tool is for **authorized security testing only**.

- ✅ Always obtain proper authorization before scanning any target
- ✅ Respect rate limits and avoid overwhelming targets
- ✅ Be aware of legal implications in your jurisdiction
- ✅ Use responsibly and ethically

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | >=2.31.0 | HTTP library for directory enumeration |
| `dnspython` | >=2.4.0 | DNS library for subdomain discovery |
| `colorama` | >=0.4.6 | Color-coded console output |
| `tqdm` | >=4.66.0 | Progress bars |

---

## 📄 License

This tool is provided for **educational and authorized security testing purposes only**.

---

## ⚖️ Disclaimer

The authors and contributors of this tool are not responsible for any misuse or illegal activities performed with this software. Users are solely responsible for ensuring they have proper authorization before using this tool on any target.

---

<div align="center">

**Made with 🔥 for Security Professionals**

[⬆ Back to Top](#-nifty-flame)

</div>
