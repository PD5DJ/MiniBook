import tkinter as tk
from tkinter import ttk, messagebox
import socket
import requests
from json import loads
from datetime import datetime, timezone

class DXSummitApp:
    def __init__(self, root, rigctl_host, rigctl_port, tracking_var, on_callsign_selected=None, get_worked_calls=None, get_worked_calls_today=None):
        self.root = root
        self.rigctl_host = rigctl_host
        self.rigctl_port = rigctl_port
        self.tracking_var = tracking_var
        self.on_callsign_selected = on_callsign_selected
        self.get_worked_calls = get_worked_calls
        self.get_worked_calls_today = get_worked_calls_today

        self.connection_status_label = ttk.Label(root, text="", foreground="red")
        self.connection_status_label.pack(pady=(0, 0))




        self.root.title("DX Summit Spot Viewer")

        # GUI components
        self.mode_var = tk.StringVar(value="All")
        self.band_var = tk.StringVar(value="All")

        filter_frame = ttk.Frame(root)
        filter_frame.pack(padx=10, pady=5)

        ttk.Label(filter_frame, text="Mode:").pack(side=tk.LEFT)
        self.mode_menu = ttk.Combobox(filter_frame, textvariable=self.mode_var,
                                      values=["All", "CW", "PHONE", "DIGI"], state="readonly")
        self.mode_menu.pack(side=tk.LEFT)

        ttk.Label(filter_frame, text="Band:").pack(side=tk.LEFT, padx=(10, 0))
        self.band_menu = ttk.Combobox(filter_frame, textvariable=self.band_var,
                                      values=["All", "160", "80", "60", "40", "30", "20", "17", "15", "12", "10", "6", "2"],
                                      state="readonly")
        self.band_menu.pack(side=tk.LEFT)

        # Bold headers
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        # Treeview (instead of Listbox)
        columns = ("time", "from_call", "to_call", "country", "frequency", "info")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=20)


        # Alternate row colors
        self.tree.tag_configure('oddrow', background='#f0f0f0')
        self.tree.tag_configure('evenrow', background='white')
        self.tree.tag_configure('worked', background='#ffd9b3')  # Oranje
        self.tree.tag_configure('worked_today', background='#b3e6ff')  # Lichtblauw



        self.tree.heading("time", text="Time")
        self.tree.heading("from_call", text="Spotter")
        self.tree.heading("to_call", text="DX")
        self.tree.heading("country", text="Country")
        self.tree.heading("frequency", text="Frequency")
        self.tree.heading("info", text="Info")


        for col in columns:
            if col == "time":
                self.tree.column(col, anchor=tk.CENTER, width=80)
            elif col == "frequency":
                self.tree.column(col, anchor=tk.CENTER, width=100)
            elif col == "country":
                self.tree.column(col, anchor=tk.CENTER, width=100) 
            elif col == "info":
                self.tree.column(col, anchor=tk.W, width=200)            
            else:
                self.tree.column(col, anchor=tk.W, width=120)

        self.tree.pack(padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.spot_clicked)

        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side='bottom', fill='x', pady=(5, 10), padx=10)

        # ⬆️ Eerst de legenda bovenaan
        legend_row = ttk.Frame(bottom_frame)
        legend_row.pack(side='top', pady=(0, 5))

        worked_legend = tk.Label(legend_row, text="Worked before", bg="#ffd9b3", relief="ridge", borderwidth=1, width=15)
        worked_legend.pack(side="left", padx=5)

        worked_today_legend = tk.Label(legend_row, text="Worked today", bg="#b3e6ff", relief="ridge", borderwidth=1, width=15)
        worked_today_legend.pack(side="left", padx=5)

        new_spot_legend = tk.Label(legend_row, text="New spot", bg="white", relief="ridge", borderwidth=1, width=15)
        new_spot_legend.pack(side="left", padx=5)

        # ⬇️ Dan Last update + Tracking
        status_row = ttk.Frame(bottom_frame)
        status_row.pack(side='top')

        self.status = ttk.Label(status_row, text="Last update:")
        self.status.pack(side='left', padx=(0, 20))

        self.tracking_status_label = ttk.Label(status_row, text="", font=("Segoe UI", 9, "bold"))
        self.tracking_status_label.pack(side='left')

        self.update_tracking_status()

        # Styling voor de legenda
        font_style = ("Arial", 9)
        for lbl in (worked_legend, worked_today_legend, new_spot_legend):
            lbl.config(font=font_style, pady=2)


        # Bind dropdown changes to spot update
        self.mode_menu.bind("<<ComboboxSelected>>", lambda e: self.get_spots())
        self.band_menu.bind("<<ComboboxSelected>>", lambda e: self.get_spots())

        self.get_spots()
        self.root.after(30000, self.periodic_update)




    def update_tracking_status(self):
        if self.tracking_var and self.tracking_var.get():
            self.tracking_status_label.config(text="Hamlib Tracking: ✅ Enabled", foreground="green")
        else:
            self.tracking_status_label.config(text="Hamlib Tracking: ❌ Disabled", foreground="red")

        self.root.after(500, self.update_tracking_status)




    def get_spots(self):
        self.connection_status_label.config(text="")
        url = "http://www.dxsummit.fi/api/v1/spots"
        mode = self.mode_var.get()
        current_worked_calls = self.get_worked_calls() if self.get_worked_calls else set()
        worked_calls_today = self.get_worked_calls_today() if self.get_worked_calls_today else set()
       
       
        if mode != "All":
            url += f"?include_modes={mode}"

        try:
            r = requests.get(url, timeout=5)
            data = loads(r.text)
            self.tree.delete(*self.tree.get_children())
            seen_calls = set()

            for i in data:
                if not all(k in i for k in ["time", "de_call", "dx_call", "dx_country", "frequency"]):
                    continue
                band = self.get_band(i["frequency"])
                if self.band_var.get() != "All" and self.band_var.get() != band:
                    continue
                if i["dx_call"] in seen_calls:
                    continue
                seen_calls.add(i["dx_call"])

                time_str = i['time'][11:16]
                from_call = i['de_call']
                country = i['dx_country']
                freq = i['frequency']
                dx_call = i['dx_call'].upper()
                info = i.get("info", "")

                if dx_call in worked_calls_today:
                    tag = 'worked_today'
                elif dx_call in current_worked_calls:
                    tag = 'worked'
                else:
                    tag = 'evenrow' if len(self.tree.get_children()) % 2 == 0 else 'oddrow'


                self.tree.insert("", "end", values=(time_str, from_call, dx_call, country, freq, info), tags=(tag,))

            self.status.config(text=f"Last update: {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC")

        except Exception:
            self.connection_status_label.config(text="❌ Could not connect to DX Summit")
            return






    def spot_clicked(self, event):
        try:
            selected = self.tree.selection()
            if not selected:
                return

            values = self.tree.item(selected[0])["values"]
            raw_freq = values[4]         # bijv. 7086.0
            to_call = values[2]          # DX call
            gui_mode = self.mode_var.get()  # Mode uit combobox (kan PHONE zijn)
            hz = int(float(raw_freq) * 1000)

            # ✅ Frequentie omzetten naar MHz voor MiniBook
            try:
                freq_mhz = f"{float(raw_freq) / 1000:.5f}"
            except ValueError:
                freq_mhz = ""

            # ✅ Bereken rig-modus bij PHONE
            if gui_mode == "PHONE" or gui_mode == "All":
                resolved_mode = "USB" if hz > 10000000 else "LSB"
            else:
                resolved_mode = gui_mode

            # ✅ Altijd callsign, freq en resolved_mode naar MiniBook
            if self.on_callsign_selected:
                self.on_callsign_selected(to_call, freq=freq_mhz, mode=resolved_mode)

            # ❌ Stop als tracking UIT staat
            if not (self.tracking_var and self.tracking_var.get()):
                return

            # ✅ Alleen als tracking aan staat: rigctl aanroepen
            with socket.create_connection((self.rigctl_host, self.rigctl_port), timeout=2) as s:
                s.sendall(f"F {hz}\n".encode())
                _ = s.recv(1024)

                if resolved_mode and resolved_mode not in ("All", "DIGI"):
                    s.sendall(f"M {resolved_mode} -1\n".encode())
                    _ = s.recv(1024)

        except Exception:
            pass








    def get_band(self, freq):
        f = int(float(freq) * 1000)
        if 1800000 < f < 2000000: return "160"
        if 3500000 < f < 4000000: return "80"
        if 5330000 < f < 5406000: return "60"
        if 7000000 < f < 7300000: return "40"
        if 10100000 < f < 10150000: return "30"
        if 14000000 < f < 14350000: return "20"
        if 18068000 < f < 18168000: return "17"
        if 21000000 < f < 21450000: return "15"
        if 24890000 < f < 24990000: return "12"
        if 28000000 < f < 29700000: return "10"
        if 50000000 < f < 54000000: return "6"
        if 144000000 < f < 148000000: return "2"
        return "0"

    def periodic_update(self):
        self.get_spots()
        self.root.after(30000, self.periodic_update)


def launch_dx_spot_viewer(
    rigctl_host="127.0.0.1",
    rigctl_port=4532,
    tracking_var=None,
    on_callsign_selected=None,
    get_worked_calls=None,
    get_worked_calls_today=None,
    parent_window=None  # 👈 toegevoegd
):
    if parent_window is None:
        parent_window = tk.Toplevel()
        parent_window.resizable(False, False)

    DXSummitApp(
        parent_window,
        rigctl_host,
        rigctl_port,
        tracking_var,
        on_callsign_selected,
        get_worked_calls,
        get_worked_calls_today
    )
