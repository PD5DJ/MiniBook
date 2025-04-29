import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import sys
import serial.tools.list_ports
import os
import configparser

SETTINGS_FILE = "settings.ini"

class RigCtlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hamlib Server")
        self.proc = None

        # Set application icon
        if os.path.exists('hamlib.ico'):
            self.root.iconbitmap('hamlib.ico')

        # Detect available serial ports
        self.serial_ports = [port.device for port in serial.tools.list_ports.comports()]
        if not self.serial_ports:
            self.serial_ports = ["No ports found"]

        # Load rig models
        self.rigs = self.load_rigs()

        # Create GUI elements
        self.create_widgets()

        # Load previously saved settings
        self.load_settings()

        # Configure column weights
        for i in range(3):
            self.root.grid_columnconfigure(i, weight=1)

        # Autostart server if enabled
        if self.autostart_var.get():
            self.status_var.set("Status: Starting server...")
            self.start_server()

    def load_rigs(self):
        """Load rig models from rigs.ini"""
        rigs = {}
        with open('rigs.ini', 'r', encoding='utf-8') as file:
            for line in file:
                if ':' in line:
                    name, number = line.strip().rsplit(':', 1)
                    rigs[name.strip()] = number.strip()
        return rigs

    def create_widgets(self):
        """Create and place all GUI elements"""
        row = 0

        # Path to rigctld.exe
        tk.Label(self.root, text="Path to rigctld.exe:").grid(row=row, column=0, sticky="w", pady=2)
        self.rigctld_path_var = tk.StringVar()
        rigctld_frame = tk.Frame(self.root)
        rigctld_frame.grid(row=row, column=1, columnspan=2, sticky="ew", pady=2)
        self.rigctld_entry = tk.Entry(rigctld_frame, textvariable=self.rigctld_path_var)
        self.rigctld_entry.pack(side="left", fill="x", expand=True)
        tk.Button(rigctld_frame, text="Browse...", command=self.browse_rigctld).pack(side="left")
        row += 1

        # Serial Port
        tk.Label(self.root, text="Serial Port:").grid(row=row, column=0, sticky="w", pady=2)
        self.serial_var = tk.StringVar()
        self.serial_combo = ttk.Combobox(self.root, textvariable=self.serial_var, values=self.serial_ports)
        self.serial_combo.grid(row=row, column=1, columnspan=2, sticky="ew", pady=2)
        row += 1

        # Baudrate
        tk.Label(self.root, text="Baudrate:").grid(row=row, column=0, sticky="w", pady=2)
        self.baud_var = tk.StringVar(value="115200")
        self.baud_combo = ttk.Combobox(self.root, textvariable=self.baud_var, values=[
            "4800", "9600", "14400", "19200", "38400", "57600", "115200"
        ])
        self.baud_combo.grid(row=row, column=1, columnspan=2, sticky="ew", pady=2)
        row += 1

        # Server Port
        tk.Label(self.root, text="Server Port:").grid(row=row, column=0, sticky="w", pady=2)
        self.port_var = tk.StringVar(value="4532")
        self.port_combo = ttk.Combobox(self.root, textvariable=self.port_var, values=["4532", "4536", "4538", "4540"])
        self.port_combo.grid(row=row, column=1, columnspan=2, sticky="ew", pady=2)
        row += 1

        # Rig Model
        tk.Label(self.root, text="Rig Model:").grid(row=row, column=0, sticky="w", pady=2)
        self.rig_var = tk.StringVar()
        self.rig_combo = ttk.Combobox(self.root, textvariable=self.rig_var, values=list(self.rigs.keys()))
        self.rig_combo.grid(row=row, column=1, columnspan=2, sticky="ew", pady=2)
        row += 1

        # Data Bits
        tk.Label(self.root, text="Data Bits:").grid(row=row, column=0, sticky="w", pady=2)
        self.databits_var = tk.StringVar(value="8")
        db_frame = tk.Frame(self.root)
        db_frame.grid(row=row, column=1, columnspan=2, sticky="w", pady=2)
        tk.Radiobutton(db_frame, text="7", variable=self.databits_var, value="7").pack(side="left")
        tk.Radiobutton(db_frame, text="8", variable=self.databits_var, value="8").pack(side="left")
        row += 1

        # Stop Bits
        tk.Label(self.root, text="Stop Bits:").grid(row=row, column=0, sticky="w", pady=2)
        self.stopbits_var = tk.StringVar(value="1")
        sb_frame = tk.Frame(self.root)
        sb_frame.grid(row=row, column=1, columnspan=2, sticky="w", pady=2)
        tk.Radiobutton(sb_frame, text="1", variable=self.stopbits_var, value="1").pack(side="left")
        tk.Radiobutton(sb_frame, text="2", variable=self.stopbits_var, value="2").pack(side="left")
        row += 1

        # Handshake
        tk.Label(self.root, text="Handshake:").grid(row=row, column=0, sticky="w", pady=2)
        self.handshake_var = tk.StringVar(value="None")
        hs_frame = tk.Frame(self.root)
        hs_frame.grid(row=row, column=1, columnspan=2, sticky="w", pady=2)
        tk.Radiobutton(hs_frame, text="None", variable=self.handshake_var, value="None").pack(side="left")
        tk.Radiobutton(hs_frame, text="RTS/CTS", variable=self.handshake_var, value="RTSCTS").pack(side="left")
        tk.Radiobutton(hs_frame, text="XON/XOFF", variable=self.handshake_var, value="XONXOFF").pack(side="left")
        row += 1

        # RTS and DTR
        tk.Label(self.root, text="RTS/DTR:").grid(row=row, column=0, sticky="w", pady=2)
        rtsdtr_frame = tk.Frame(self.root)
        rtsdtr_frame.grid(row=row, column=1, columnspan=2, sticky="w", pady=2)
        self.rts_var = tk.BooleanVar()
        self.dtr_var = tk.BooleanVar()
        tk.Checkbutton(rtsdtr_frame, text="RTS ON", variable=self.rts_var).pack(side="left")
        tk.Checkbutton(rtsdtr_frame, text="DTR ON", variable=self.dtr_var).pack(side="left")
        row += 1

        # Autostart Checkbox
        self.autostart_var = tk.BooleanVar()
        self.autostart_check = tk.Checkbutton(self.root, text="Autostart Server on startup", variable=self.autostart_var)
        self.autostart_check.grid(row=row, column=0, columnspan=3, sticky="w", pady=5)
        row += 1

        # Status Label
        self.status_var = tk.StringVar(value="Status: Server stopped")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, anchor="w", fg="red")
        self.status_label.grid(row=row, column=0, columnspan=3, sticky="ew", pady=5)
        row += 1

        # Buttons
        self.start_button = tk.Button(self.root, text="Start Server", command=self.start_server)
        self.start_button.grid(row=row, column=0, sticky="ew", pady=5)
        self.stop_button = tk.Button(self.root, text="Stop Server", command=self.stop_server)
        self.stop_button.grid(row=row, column=1, sticky="ew", pady=5)
        self.exit_button = tk.Button(self.root, text="Exit", command=self.exit_program)
        self.exit_button.grid(row=row, column=2, sticky="ew", pady=5)

    def browse_rigctld(self):
        """Browse for rigctld.exe"""
        filename = filedialog.askopenfilename(
            title="Select rigctld.exe",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.rigctld_path_var.set(filename)

    def build_command(self):
        """Build the rigctld.exe command"""
        rig_number = self.rigs.get(self.rig_var.get(), "3078")
        rts_state = "ON" if self.rts_var.get() else "OFF"
        dtr_state = "ON" if self.dtr_var.get() else "OFF"
        serial_parity = "None"
        serial_handshake = {"None": "None", "RTSCTS": "RTSCTS", "XONXOFF": "XONXOFF"}.get(self.handshake_var.get(), "None")
        executable = self.rigctld_path_var.get()

        if not os.path.exists(executable):
            raise FileNotFoundError(f"rigctld.exe not found at: {executable}")

        cmd = [
            executable,
            "-t", self.port_var.get(),
            "-m", rig_number,
            "-r", self.serial_var.get(),
            "-s", self.baud_var.get(),
            "--set-conf=data_bits={},stop_bits={},serial_parity={},serial_handshake={},dtr_state={},rts_state={}".format(
                self.databits_var.get(),
                self.stopbits_var.get(),
                serial_parity,
                serial_handshake,
                dtr_state,
                rts_state
            )
        ]
        return cmd

    def start_server(self):
        """Start the rigctld server"""
        if self.proc:
            return

        try:
            cmd = self.build_command()
            CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0
            self.proc = subprocess.Popen(cmd, creationflags=CREATE_NO_WINDOW)
            self.save_settings()
            self.status_var.set("Status: Server started")
            self.status_label.config(fg="green")
        except Exception as e:
            messagebox.showerror("Error Starting Server", str(e))
            self.status_var.set("Status: Server stopped")
            self.status_label.config(fg="red")

    def stop_server(self):
        """Stop the rigctld server"""
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
            self.proc = None
            self.status_var.set("Status: Server stopped")
            self.status_label.config(fg="red")

    def exit_program(self):
        """Ask for confirmation and exit"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            if self.proc:
                self.stop_server()
            self.root.destroy()

    def save_settings(self):
        """Save settings to settings.ini"""
        config = configparser.ConfigParser()
        config['Settings'] = {
            'rigctld_path': self.rigctld_path_var.get(),
            'serial_port': self.serial_var.get(),
            'baudrate': self.baud_var.get(),
            'server_port': self.port_var.get(),
            'rig_model': self.rig_var.get(),
            'data_bits': self.databits_var.get(),
            'stop_bits': self.stopbits_var.get(),
            'handshake': self.handshake_var.get(),
            'rts': str(self.rts_var.get()),
            'dtr': str(self.dtr_var.get()),
            'autostart': str(self.autostart_var.get())
        }
        with open(SETTINGS_FILE, 'w') as configfile:
            config.write(configfile)

    def load_settings(self):
        """Load settings from settings.ini"""
        if os.path.exists(SETTINGS_FILE):
            config = configparser.ConfigParser()
            config.read(SETTINGS_FILE)
            settings = config['Settings']
            self.rigctld_path_var.set(settings.get('rigctld_path', 'rigctld.exe'))
            self.serial_var.set(settings.get('serial_port', self.serial_ports[0]))
            self.baud_var.set(settings.get('baudrate', '115200'))
            self.port_var.set(settings.get('server_port', '4532'))
            self.rig_var.set(settings.get('rig_model', ''))
            self.databits_var.set(settings.get('data_bits', '8'))
            self.stopbits_var.set(settings.get('stop_bits', '1'))
            self.handshake_var.set(settings.get('handshake', 'None'))
            self.rts_var.set(settings.getboolean('rts', False))
            self.dtr_var.set(settings.getboolean('dtr', False))
            self.autostart_var.set(settings.getboolean('autostart', False))

if __name__ == "__main__":
    root = tk.Tk()
    app = RigCtlGUI(root)
    root.mainloop()
