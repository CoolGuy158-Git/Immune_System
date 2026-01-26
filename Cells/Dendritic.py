import os
from datetime import datetime
import hashlib
import math

"""
The Dendritic Cell:
Saves virus info in a file named after the actual virus filename
"""

def get_info_file(virus_name: str) -> str:
    safe_name = virus_name.replace(os.sep, "_")  # avoid folder slashes in filenames
    return os.path.join(os.path.dirname(__file__), f"info_{safe_name}.txt")


def sha256(file_path: str) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def entropy_score(file_path: str) -> float:
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


def collect_info(file_path: str, yara_rules_triggered: list, virus_name: str = None):
    if virus_name is None:
        virus_name = os.path.basename(file_path)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sha = sha256(file_path)
    fuzzy = entropy_score(file_path)

    info = f"[{timestamp}] Detected suspicious file: {file_path}\n"
    info += f"   SHA256: {sha}\n"
    info += f"   FUZZY: {fuzzy}\n"
    info += f"   RULES: {','.join(yara_rules_triggered)}\n\n"

    info_file = get_info_file(virus_name)

    try:
        with open(info_file, "a") as f:
            f.write(info)
        print(f"Dendritic saved info about {file_path} to {info_file}")
    except Exception as e:
        print("Failed to save info:", e)
