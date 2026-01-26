import os
import subprocess
import sys
import time
from multiprocessing import Process
from Cells import Macrophage

CREATED_EXES = set()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
QUARANTINE_THRESHOLD = 85

def sha256(file_path):
    import hashlib
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def entropy_score(file_path):
    import math
    with open(file_path, "rb") as f:
        data = f.read()
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

def load_antibodies(log_func=print):
    antibodies = []
    for fname in os.listdir(BASE_DIR):
        if fname.startswith("info_") and fname.endswith(".txt"):
            path = os.path.join(BASE_DIR, fname)
            with open(path, "r") as f:
                block = {}
                for line in f:
                    if line.strip() == "":
                        if block:
                            antibodies.append(block)
                            block = {}
                    else:
                        if ":" in line:
                            k, v = line.strip().split(":", 1)
                            block[k] = v
                if block:
                    antibodies.append(block)
    log_func(f"Loaded {len(antibodies)} antibody(s).")
    return antibodies
def specialized_macrophage(antibody, log_func=print):
    quarantine_dir = os.path.join(BASE_DIR, "quarantine")
    if not os.path.exists(quarantine_dir):
        return

    for root, dirs, files in os.walk(quarantine_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if Macrophage.is_self(file_path):
                continue
            if antibody.get("SHA256") and antibody["SHA256"] == sha256(file_path):
                log_func(f"Specialized Macrophage auto-isolating exact match: {file_path}")
                Macrophage.isolate_virus(file_path, log_func)
            elif antibody.get("FUZZY"):
                try:
                    score = compare_entropy(entropy_score(file_path), float(antibody["FUZZY"]))
                    if score >= QUARANTINE_THRESHOLD:
                        log_func(f"Specialized Macrophage auto-isolating similar file ({score:.1f}%): {file_path}")
                        Macrophage.isolate_virus(file_path, log_func)
                except ValueError:
                    log_func(f"Invalid FUZZY value in antibody: {antibody['FUZZY']}")
def create_antibody_exe(antibody, log_func=print, ask_permission=True):
    virus_name = antibody.get("NAME", "unknownvirus")
    if virus_name in CREATED_EXES:
        return

    CREATED_EXES.add(virus_name)
    py_name = f"antibody_for_{virus_name}.py"
    exe_name = f"antibody_for_{virus_name}.exe"
    info_file = os.path.join(BASE_DIR, f"info_{virus_name}.txt")

    approve = "n"
    if ask_permission:
        approve = input(f"Do you want to create an antibody executable for {virus_name}? (Y/n) >>> ").strip().lower()
    if approve != "y" and approve != "":
        log_func("Antibody EXE creation canceled.")
        return
    with open(py_name, "w") as f:
        f.write(f"""\
import sys
from Cells import BCell

INFO_FILE = r"{info_file}"

def main():
    antibodies = BCell.load_antibodies()
    for ab in antibodies:
        if ab.get("NAME") == "{virus_name}":
            BCell.specialized_macrophage(ab)

if __name__ == "__main__":
    main()
""")
    log_func(f"Antibody script created: {py_name}")
    log_func(f"Building EXE: {exe_name} ...")
    subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", py_name], check=True)
    time.sleep(1)

    exe_path = os.path.join("dist", exe_name)
    if os.path.exists(exe_path):
        log_func(f"Antibody EXE created at: {exe_path}")
    else:
        log_func("Failed to locate EXE. Check PyInstaller output.")

def make_antibodies(log_func=print, ask_permission=True):
    antibodies = load_antibodies(log_func)
    if not antibodies:
        log_func("No antibodies to run.")
        return
    for antibody in antibodies:
        p = Process(target=specialized_macrophage, args=(antibody, log_func))
        p.start()
        log_func(f"B-Cell generated antibody process for SHA256 {antibody.get('SHA256')} (PID {p.pid})")
        create_antibody_exe(antibody, log_func, ask_permission)
