import os
import shutil
import hashlib
import math
import yara
"""
This thing well eats the virus and hides it in quarantine 
"""
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
QUARANTINE_DIR = os.path.join(BASE_DIR, "quarantine")
if not os.path.exists(QUARANTINE_DIR):
    os.mkdir(QUARANTINE_DIR)

SELF_FILES = {
    "Macrophage.py",
    'Macrophage.cpython-313.pyc',
    'Macrophage.cpython-312.pyc',
    'Macrophage.cpython-314.pyc',
    "Macrophage.exe",
}

QUARANTINE_THRESHOLD = 85

rules = yara.compile(source="""
rule Suspicious_Windows_Malware {
    strings:
        $a = "CreateRemoteThread"
        $b = "WriteProcessMemory"
        $c = "VirtualAllocEx"
        $d = "cmd.exe"
        $e = "powershell"

    condition:
        any of them
}
""")

def sha256(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def entropy_score(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except (PermissionError, IOError):
        return None
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    entropy = 0
    for count in freq.values():
        p = count / len(data)
        entropy -= p * math.log2(p)
    return entropy


def compare_entropy(entropy1, entropy2):
    max_entropy = max(entropy1, entropy2)
    if max_entropy == 0:
        return 100.0
    diff = abs(entropy1 - entropy2)
    return (1 - diff / max_entropy) * 100

def is_self(file_path):
    file_path = os.path.abspath(file_path).replace("\\","/")
    if file_path.startswith(BASE_DIR):
        return True
    if "__pycache__" in file_path:
        return True
    if os.path.basename(file_path) in SELF_FILES:
        return True
    return False

def detect_virus(file_path, log_func=print):
    if not os.path.exists(file_path) or is_self(file_path):
        return False
    try:
        matches = rules.match(file_path)
        if matches:
            log_func(f"Virus detected: {file_path}")
            return True
        log_func(f"{file_path} appears clean.")
        return False
    except (PermissionError, IOError):
        log_func(f"Cannot access {file_path}, permission denied.")
        return False
    except Exception as e:
        if "could not open file" in str(e).lower():
            log_func(f"File locked by system antivirus: {file_path}")
            return "LOCKED"
        log_func(f"Scan failed: {e}")
        return False

def isolate_virus(file_path, log_func=print):
    file_path = os.path.abspath(file_path).replace("\\","/")
    if not os.path.exists(file_path) or is_self(file_path):
        return
    name = os.path.basename(file_path)
    dst = os.path.join(QUARANTINE_DIR, name + ".quarantine")
    try:
        shutil.move(file_path, dst)
        os.chmod(dst, 0o000)
        log_func(f"File quarantined: {dst}")
    except Exception as e:
        log_func(f"Failed to quarantine {file_path}: {e}")

def scan_path(path, log_func=print):
    results = []
    path = os.path.abspath(path).replace("\\","/")
    if os.path.isfile(path):
        results.append((path, detect_virus(path, log_func)))
    else:
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                results.append((full_path, detect_virus(full_path, log_func)))
    return results

def permissionMacro(file_path, log_func=print):
    isolate_virus(file_path, log_func)
