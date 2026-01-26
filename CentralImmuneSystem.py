import customtkinter as ctk
from Cells import Macrophage, BCell
from tkinter import filedialog, messagebox
import threading
"""
The CIS Is The GUI Interface And The PLace Where The User Interacts With The AV
Logs Can Be Seen In The Terminal
"""
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CIS_GUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Central Immune System")
        self.geometry("800x600")

        self.output_box = ctk.CTkTextbox(self, width=780, height=400)
        self.output_box.pack(pady=10)

        self.scan_button = ctk.CTkButton(self, text="Scan Folder", command=self.scan_folder, width=100, height=100, corner_radius=50)
        self.scan_button.pack(pady=5)

        self.exit_button = ctk.CTkButton(self, text="Exit", command=self.destroy)
        self.exit_button.pack(pady=5)

    def log(self, msg):
        self.output_box.insert("end", msg + "\n")
        self.output_box.see("end")

    def scan_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Scan")
        if folder:
            threading.Thread(target=self.run_scan, args=(folder,), daemon=True).start()

    def run_scan(self, folder):
        self.log(f"Scanning {folder}...")
        # T-Cells request resources → **requires approval**
        if messagebox.askyesno("T-Cells Request", "T-Cells requesting resources for antivirus. Approve?"):
            self.log("Resources approved for T-Cells scanning.")
        else:
            self.log("Resources denied. Scan canceled.")
            return

        results = Macrophage.scan_path(folder)
        for file_path, detected in results:
            if detected:
                approve = messagebox.askyesno("Virus Detected", f"{file_path} detected. Isolate?")
                if approve:
                    Macrophage.permissionMacro(file_path)
                    self.log(f"File isolated: {file_path}")
                else:
                    self.log(f"Threat ignored: {file_path}")
        antibodies = BCell.load_antibodies()
        for antibody in antibodies:
            approve = messagebox.askyesno("B-Cell Antibody", f"Create EXE for {antibody.get('NAME', 'unknownvirus')}?")
            if approve:
                BCell.create_antibody_exe(antibody)
                self.log(f"Antibody EXE created for {antibody.get('NAME', 'unknownvirus')}")
            else:
                self.log(f"Antibody EXE skipped for {antibody.get('NAME', 'unknownvirus')}")

        self.log("Scan complete.")

if __name__ == "__main__":
    app = CIS_GUI()
    app.mainloop()
