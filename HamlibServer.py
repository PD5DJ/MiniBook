#**********************************************************************************************************************************
# File          :   HamlibServer.py
# Project       :   Hamlib Rigtctld.exe GUI
# Description   :   Sets a rigctld.exe server, with radio preset option
# Date          :   01-05-2025
# Authors       :   Bjorn Pasteuning - PD5DJ
# Website       :   https://wwww.pd5dj.nl
#
# Version history
#   01-05-2025  :   1.0.0   - Initial basics running
#   19-05-2025  :   1.0.1   - Preset options added
#**********************************************************************************************************************************
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import subprocess
import sys
import serial.tools.list_ports
import os
import configparser

VERSION = "v1.0.1"
SETTINGS_FILE = "settings.ini"

class RigCtlGUI:
    def __init__(self, root):
        self.root = root
        self.root.resizable(False, False)
        self.root.title("Hamlib Server | " + VERSION)
        self.proc = None

        self.serial_ports = [port.device for port in serial.tools.list_ports.comports()]
        if not self.serial_ports:
            self.serial_ports = ["No ports found"]

        self.rigs = self.load_rigs()

        self.presets = {
            "Default": {}, "ICOM 7300": {}, "FT-991A": {}, "KX2": {}, "Custom": {}
        }

        self.create_widgets()
        self.load_settings()

        for i in range(3):
            self.root.grid_columnconfigure(i, weight=1)

        if self.autostart_var.get():
            self.status_var.set("Status: Starting server...")
            self.start_server()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_program)

    def load_rigs(self):
        rigs = {}
        with open('rigs.ini', 'r', encoding='utf-8') as file:
            for line in file:
                if ':' in line:
                    name, number = line.strip().rsplit(':', 1)
                    rigs[name.strip()] = number.strip()
        return rigs

    def create_widgets(self):
        row = 0

        tk.Label(self.root, text="Path to rigctld.exe:").grid(row=row, column=0, sticky="w", pady=2)
        self.rigctld_path_var = tk.StringVar()
        rigctld_frame = tk.Frame(self.root)
        rigctld_frame.grid(row=row, column=1, columnspan=2, sticky="ew", pady=2)
        self.rigctld_entry = tk.Entry(rigctld_frame, textvariable=self.rigctld_path_var)
        self.rigctld_entry.pack(side="left", fill="x", expand=True)
        
        row += 1

        self.browse_button = tk.Button(rigctld_frame, text="Browse...", command=self.browse_rigctld)
        self.browse_button.pack(side="left")

        # Preset gerelateerde knoppen
        self.new_preset_button = tk.Button(self.root, text="New Preset", command=self.create_new_preset)
        self.new_preset_button.grid(row=row, column=0, sticky="ew", pady=2)

        self.save_preset_button = tk.Button(self.root, text="Save Preset", command=self.save_to_preset)
        self.save_preset_button.grid(row=row, column=1, sticky="ew", pady=2)

        self.delete_preset_button = tk.Button(self.root, text="Delete Preset", command=self.delete_preset)
        self.delete_preset_button.grid(row=row, column=2, sticky="ew", pady=2)
        
        row += 1

        # Preset selection
        tk.Label(self.root, text="Preset:").grid(row=row, column=0, sticky="w", pady=2)
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(self.root, textvariable=self.preset_var, values=list(self.presets.keys()), state="readonly")
        self.preset_combo.bind("<<ComboboxSelected>>", lambda e: self.load_selected_preset())
        self.preset_combo.grid(row=row, column=1, sticky="ew", pady=2)

        self.rename_preset_button = tk.Button(self.root, text="Rename", command=self.rename_preset)
        self.rename_preset_button.grid(row=row, column=2, sticky="ew", pady=2)

        row += 1

        # Serial Port
        tk.Label(self.root, text="Serial Port:").grid(row=row, column=0, sticky="w", pady=2)
        self.serial_var = tk.StringVar()
        self.serial_combo = ttk.Combobox(self.root, textvariable=self.serial_var, values=self.serial_ports)
        self.serial_combo.grid(row=row, column=1, columnspan=2, sticky="ew", pady=2)
        row += 1

        tk.Label(self.root, text="Baudrate:").grid(row=row, column=0, sticky="w", pady=2)
        self.baud_var = tk.StringVar(value="115200")
        self.baud_combo = ttk.Combobox(self.root, textvariable=self.baud_var, values=["4800", "9600", "14400", "19200", "38400", "57600", "115200"])
        self.baud_combo.grid(row=row, column=1, columnspan=2, sticky="ew", pady=2)
        row += 1

        tk.Label(self.root, text="Server Port:").grid(row=row, column=0, sticky="w", pady=2)
        self.port_var = tk.StringVar(value="4532")
        self.port_combo = ttk.Combobox(self.root, textvariable=self.port_var, values=["4532", "4536", "4538", "4540"])
        self.port_combo.grid(row=row, column=1, columnspan=2, sticky="ew", pady=2)
        row += 1

        tk.Label(self.root, text="Rig Model:").grid(row=row, column=0, sticky="w", pady=2)
        self.rig_var = tk.StringVar()
        self.rig_combo = ttk.Combobox(self.root, textvariable=self.rig_var, values=list(self.rigs.keys()))
        self.rig_combo.grid(row=row, column=1, columnspan=2, sticky="ew", pady=2)
        row += 1

        tk.Label(self.root, text="Data Bits:").grid(row=row, column=0, sticky="w", pady=2)
        self.databits_var = tk.StringVar(value="8")
        db_frame = tk.Frame(self.root)
        db_frame.grid(row=row, column=1, columnspan=2, sticky="w", pady=2)
        tk.Radiobutton(db_frame, text="7", variable=self.databits_var, value="7").pack(side="left")
        tk.Radiobutton(db_frame, text="8", variable=self.databits_var, value="8").pack(side="left")
        row += 1

        tk.Label(self.root, text="Stop Bits:").grid(row=row, column=0, sticky="w", pady=2)
        self.stopbits_var = tk.StringVar(value="1")
        sb_frame = tk.Frame(self.root)
        sb_frame.grid(row=row, column=1, columnspan=2, sticky="w", pady=2)
        tk.Radiobutton(sb_frame, text="1", variable=self.stopbits_var, value="1").pack(side="left")
        tk.Radiobutton(sb_frame, text="2", variable=self.stopbits_var, value="2").pack(side="left")
        row += 1

        tk.Label(self.root, text="Handshake:").grid(row=row, column=0, sticky="w", pady=2)
        self.handshake_var = tk.StringVar(value="None")
        hs_frame = tk.Frame(self.root)
        hs_frame.grid(row=row, column=1, columnspan=2, sticky="w", pady=2)
        tk.Radiobutton(hs_frame, text="None", variable=self.handshake_var, value="None").pack(side="left")
        tk.Radiobutton(hs_frame, text="RTS/CTS", variable=self.handshake_var, value="RTSCTS").pack(side="left")
        tk.Radiobutton(hs_frame, text="XON/XOFF", variable=self.handshake_var, value="XONXOFF").pack(side="left")
        row += 1

        tk.Label(self.root, text="RTS/DTR:").grid(row=row, column=0, sticky="w", pady=2)
        rtsdtr_frame = tk.Frame(self.root)
        rtsdtr_frame.grid(row=row, column=1, columnspan=2, sticky="w", pady=2)
        self.rts_var = tk.BooleanVar()
        self.dtr_var = tk.BooleanVar()
        tk.Checkbutton(rtsdtr_frame, text="RTS ON", variable=self.rts_var).pack(side="left")
        tk.Checkbutton(rtsdtr_frame, text="DTR ON", variable=self.dtr_var).pack(side="left")
        row += 1

        self.autostart_var = tk.BooleanVar()
        self.autostart_check = tk.Checkbutton(self.root, text="Autostart Server on startup", variable=self.autostart_var)
        self.autostart_check.grid(row=row, column=0, columnspan=3, sticky="w", pady=5)
        row += 1

        self.status_var = tk.StringVar(value="Status: Server stopped")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, anchor="w", fg="red")
        self.status_label.grid(row=row, column=0, columnspan=3, sticky="ew", pady=5)
        row += 1

        self.start_button = tk.Button(self.root, text="Start Server", command=self.start_server)
        self.start_button.grid(row=row, column=0, sticky="ew", pady=5)
        self.stop_button = tk.Button(self.root, text="Stop Server", command=self.stop_server)
        self.stop_button.grid(row=row, column=1, sticky="ew", pady=5)
        self.exit_button = tk.Button(self.root, text="Exit", command=self.exit_program)
        self.exit_button.grid(row=row, column=2, sticky="ew", pady=5)


    def disable_preset_controls(self):
        self.new_preset_button.config(state="disabled")
        self.save_preset_button.config(state="disabled")
        self.delete_preset_button.config(state="disabled")
        self.rename_preset_button.config(state="disabled")
        self.preset_combo.config(state="disabled")
        self.browse_button.config(state="disabled")

    def enable_preset_controls(self):
        self.new_preset_button.config(state="normal")
        self.save_preset_button.config(state="normal")
        self.delete_preset_button.config(state="normal")
        self.rename_preset_button.config(state="normal")
        self.preset_combo.config(state="readonly")
        self.browse_button.config(state="normal")

    def disable_all_inputs(self):
        for frame in self.root.winfo_children():
            for widget in frame.winfo_children() if isinstance(frame, tk.Frame) else [frame]:
                if isinstance(widget, (tk.Entry, ttk.Combobox, tk.Checkbutton, tk.Radiobutton)):
                    widget.configure(state="disabled")

    def enable_all_inputs(self):
        for frame in self.root.winfo_children():
            for widget in frame.winfo_children() if isinstance(frame, tk.Frame) else [frame]:
                if isinstance(widget, (tk.Entry, ttk.Combobox, tk.Checkbutton, tk.Radiobutton)):
                    widget.configure(state="normal")

    def browse_rigctld(self):
        filename = filedialog.askopenfilename(title="Select rigctld.exe", filetypes=[("Executable", "*.exe"), ("All files", "*.*")])
        if filename:
            self.rigctld_path_var.set(filename)

    def start_server(self):
        if self.proc:
            return
        try:
            cmd = self.build_command()
            CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0
            self.proc = subprocess.Popen(cmd, creationflags=CREATE_NO_WINDOW)
            self.save_settings()
            self.status_var.set("Status: Server started")
            self.status_label.config(fg="green")
            self.disable_all_inputs()
            self.disable_preset_controls()
        except Exception as e:
            messagebox.showerror("Error Starting Server", str(e))
            self.status_var.set("Status: Server stopped")
            self.status_label.config(fg="red")

    def stop_server(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
            self.proc = None
            self.status_var.set("Status: Server stopped")
            self.status_label.config(fg="red")
            self.enable_all_inputs()
            self.enable_preset_controls()


    def exit_program(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            if self.proc:
                self.stop_server()
            self.root.destroy()

    def build_command(self):
        rig_number = self.rigs.get(self.rig_var.get(), "3078")
        rts_state = "ON" if self.rts_var.get() else "OFF"
        dtr_state = "ON" if self.dtr_var.get() else "OFF"
        serial_parity = "None"
        serial_handshake = self.handshake_var.get()
        executable = self.rigctld_path_var.get()

        if not os.path.exists(executable):
            raise FileNotFoundError(f"rigctld.exe not found at: {executable}")

        return [
            executable,
            "-t", self.port_var.get(),
            "-m", rig_number,
            "-r", self.serial_var.get(),
            "-s", self.baud_var.get(),
            "--set-conf=data_bits={},stop_bits={},serial_parity={},serial_handshake={},dtr_state={},rts_state={}".format(
                self.databits_var.get(), self.stopbits_var.get(), serial_parity, serial_handshake, dtr_state, rts_state
            )
        ]

    def delete_preset(self):
        name = self.preset_var.get()
        if name not in self.presets:
            messagebox.showwarning("Delete Preset", "No valid preset selected.")
            return
        if messagebox.askyesno("Delete Preset", f"Are you sure you want to delete preset '{name}'?"):
            del self.presets[name]
            self.preset_combo['values'] = list(self.presets.keys())
            if self.presets:
                self.preset_var.set(list(self.presets.keys())[0])
            else:
                self.preset_var.set("")
            self.save_settings()
            messagebox.showinfo("Deleted", f"Preset '{name}' deleted.")

    def create_new_preset(self):
        new_name = simpledialog.askstring("New Preset", "Enter name for new preset:")
        if not new_name or new_name in self.presets:
            messagebox.showerror("Error", "Invalid or duplicate preset name.")
            return
        self.presets[new_name] = {
            'serial_port': self.serial_var.get(),
            'baudrate': self.baud_var.get(),
            'server_port': self.port_var.get(),
            'rig_model': self.rig_var.get(),
            'data_bits': self.databits_var.get(),
            'stop_bits': self.stopbits_var.get(),
            'handshake': self.handshake_var.get(),
            'rts': self.rts_var.get(),
            'dtr': self.dtr_var.get()
        }
        self.preset_combo['values'] = list(self.presets.keys())
        self.preset_var.set(new_name)
        self.save_settings()
        messagebox.showinfo("New Preset", f"Preset '{new_name}' created.")


    def save_settings(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'rigctld_path': self.rigctld_path_var.get(),
            'autostart': str(self.autostart_var.get()),
            'last_preset': self.preset_var.get()
        }
        if not config.has_section("Presets"):
            config.add_section("Presets")

        for name, p in self.presets.items():
            config["Presets"][name] = '|'.join([
                p.get("serial_port", ""), p.get("baudrate", ""), p.get("server_port", ""),
                p.get("rig_model", ""), p.get("data_bits", ""), p.get("stop_bits", ""),
                p.get("handshake", ""), str(p.get("rts", False)), str(p.get("dtr", False))
            ])

        with open(SETTINGS_FILE, 'w') as f:
            config.write(f)

    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return

        config = configparser.ConfigParser()
        config.read(SETTINGS_FILE)

        s = config['Settings']
        self.rigctld_path_var.set(s.get('rigctld_path', ''))
        self.autostart_var.set(s.getboolean('autostart', False))
        last_preset = s.get('last_preset', '')

        if 'Presets' in config:
            self.presets = {}
            for name, val in config['Presets'].items():
                parts = val.split('|')
                if len(parts) == 9:
                    self.presets[name] = {
                        'serial_port': parts[0],
                        'baudrate': parts[1],
                        'server_port': parts[2],
                        'rig_model': parts[3],
                        'data_bits': parts[4],
                        'stop_bits': parts[5],
                        'handshake': parts[6],
                        'rts': parts[7] == 'True',
                        'dtr': parts[8] == 'True'
                    }
                else:
                    print(f"⚠️ Preset '{name}' is malformed. Skipping.")

            self.preset_combo['values'] = list(self.presets.keys())

            # Zet en laad de laatst gebruikte preset
            if last_preset in self.presets:
                self.preset_var.set(last_preset)
                self.load_selected_preset()
            elif self.presets:
                fallback = list(self.presets.keys())[0]
                self.preset_var.set(fallback)
                self.load_selected_preset()


    def load_selected_preset(self):
        name = self.preset_var.get()
        if name not in self.presets:
            messagebox.showwarning("Preset", "Preset not found.")
            return
        p = self.presets[name]
        self.serial_var.set(p.get('serial_port', ''))
        self.baud_var.set(p.get('baudrate', ''))
        self.port_var.set(p.get('server_port', ''))
        self.rig_var.set(p.get('rig_model', ''))
        self.databits_var.set(p.get('data_bits', '8'))
        self.stopbits_var.set(p.get('stop_bits', '1'))
        self.handshake_var.set(p.get('handshake', 'None'))
        self.rts_var.set(p.get('rts', False))
        self.dtr_var.set(p.get('dtr', False))


    def save_to_preset(self):
        name = self.preset_var.get()
        if not name:
            messagebox.showwarning("Preset", "No preset selected")
            return
        self.presets[name] = {
            'serial_port': self.serial_var.get(),
            'baudrate': self.baud_var.get(),
            'server_port': self.port_var.get(),
            'rig_model': self.rig_var.get(),
            'data_bits': self.databits_var.get(),
            'stop_bits': self.stopbits_var.get(),
            'handshake': self.handshake_var.get(),
            'rts': self.rts_var.get(),
            'dtr': self.dtr_var.get()
        }
        self.save_settings()
        messagebox.showinfo("Preset Saved", f"Preset '{name}' saved.")

    def rename_preset(self):
        old = self.preset_var.get()
        if old not in self.presets: return
        new = simpledialog.askstring("Rename Preset", f"Enter new name for '{old}':")
        if new and new.strip() and new not in self.presets:
            self.presets[new] = self.presets.pop(old)
            self.preset_combo['values'] = list(self.presets.keys())
            self.preset_var.set(new)
            self.save_settings()

if __name__ == "__main__":
    root = tk.Tk()
    app = RigCtlGUI(root)
    root.mainloop()
