#**********************************************************************************************************************************
# File          :   telspot.py
# Project       :   Telnet DX Cluster
# Description   :   DX Spider Telnet client, can be run standalone, or from within MiniBook with Spot click -> Logbook and Rigcontrol
# Date          :   27-05-2025
# Authors       :   Bjorn Pasteuning - PD5DJ
# Website       :   https://wwww.pd5dj.nl
#
# Version history
#   27-05-2025  :   1.0.0   - Initial basics running
#   28-05-2025  :   1.0.1   - All functions working
#   30-05-2025  :   1.0.2   - Add spot function added
#                           - cty.dat download added
#                           - MODES catagories expanded
#   01-06-2025  :   1.0.3   - UI layout changed, Exit button added
#**********************************************************************************************************************************

import asyncio
import json
import threading
import tkinter as tk
import tkinter.font
from tkinter import ttk, messagebox
import re
import configparser
import os
import socket
from datetime import datetime
from cty_parser import parse_cty_file
import requests

VERSION_NUMBER = ("v1.0.3")

INI_FILE        = "dxcluster.ini"
CLUSTER_FILE    = "clusters.json"
DXCC_FILE       = "cty.dat"
ctydat_url      = "https://www.country-files.com/bigcty/cty.dat"

BANDS = {
    "HF": (1.8, 30.0),
    "VHF": (30.0, 300.0),
    "UHF": (300.0, 1000.0),
    "SHF": (1000.0, 3000.0),    
    "160m": (1.8, 2.0),
    "80m": (3.5, 3.8),
    "60m": (5.3305, 5.4065),
    "40m": (7.0, 7.3),
    "30m": (10.1, 10.15),
    "20m": (14.0, 14.35),
    "17m": (18.068, 18.168),
    "15m": (21.0, 21.45),
    "12m": (24.89, 24.99),
    "10m": (28.0, 29.7),
    "6m": (50.0, 54.0),
    "4m": (70.0, 70.5),
    "40MHz": (40.66, 40.7),
    "2m": (144.0, 148.0),
    "70cm": (420.0, 450.0),
    "23cm": (1240.0, 1300.0),
    "13cm": (2300.0, 2450.0),
}


MODES = {
    "CW": [
        (1.800, 1.829),
        (3.500, 3.559),
        (7.000, 7.039),
        (10.100, 10.139),
        (14.000, 14.069),
        (18.068, 18.109),
        (21.000, 21.069),
        (24.890, 24.909),
        (28.000, 28.069),
        (50.000, 50.099),
        (70.000, 70.099),
        (144.000, 144.099),
        (432.000, 432.099),
        (1296.000, 1296.099),
        (2300.000, 2300.199),
    ],
    "FT8": [
        (1.840, 1.841),
        (3.573, 3.574),
        (7.074, 7.075),
        (10.136, 10.137),
        (14.074, 14.075),
        (18.100, 18.101),
        (21.074, 21.075),
        (24.915, 24.916),
        (28.074, 28.075),
        (50.313, 50.314),
        (70.154, 70.155),
        (144.174, 144.175),
        (432.174, 432.175),
    ],
    "FT4": [
        (3.575, 3.576),
        (7.047, 7.048),
        (14.080, 14.081),
        (21.140, 21.141),
        (50.318, 50.319),
        (144.170, 144.171),
    ],
    "DIGITAL": [
        (1.830, 1.839),
        (1.842, 1.849),
        (3.560, 3.572),
        (3.577, 3.599),
        (7.040, 7.046),
        (7.049, 7.069),
        (10.140, 10.135),
        (10.138, 10.149),
        (14.070, 14.073),
        (14.076, 14.119),
        (18.110, 18.099),
        (18.102, 18.167),
        (21.070, 21.073),
        (21.076, 21.139),
        (24.910, 24.914),
        (24.917, 24.989),
        (28.070, 28.073),
        (28.076, 28.119),
        (50.300, 50.312),
        (50.315, 50.317),
        (50.320, 50.499),
        (70.200, 70.153),
        (70.156, 70.299),
        (144.800, 144.169),
        (144.172, 144.989),
        (432.600, 432.173),
        (432.176, 432.999),
        (1296.200, 1296.499),
        (2400.000, 2402.999),
    ],
    "PHONE": [
        (1.850, 1.999),
        (3.600, 3.799),
        (7.070, 7.299),
        (14.150, 14.349),
        (21.200, 21.449),
        (28.400, 29.699),
        (50.100, 53.999),
        (70.100, 70.499),
        (144.200, 147.999),
        (430.000, 439.999),
        (1297.000, 1299.999),
        (2403.000, 2449.999),
    ],
}



class DXClusterApp:
    def __init__(self, root, rigctl_host="127.0.0.1", rigctl_port=4532, tracking_var=None, on_callsign_selected=None, get_worked_calls=None, get_worked_calls_today=None):
        self.root = root
        self.root.title(f"DX Cluster Telnet Client - {VERSION_NUMBER}")

        # MiniBook integration
        self.rigctl_host = rigctl_host
        self.rigctl_port = rigctl_port
        self.tracking_var = tracking_var
        self.on_callsign_selected = on_callsign_selected
        self.get_worked_calls = get_worked_calls
        self.get_worked_calls_today = get_worked_calls_today

        # Telnet/async setup
        self.connected = False
        self.writer = None
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

        # UI setup
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Load Hosts en DXCC
        self.hosts = []
        self.spots = []
        self.load_host_file(default=CLUSTER_FILE)

        # Checks if cty.dat is present, if not download. and parse it
        self.check_ctydat_file()

        # Tracking status label
        #self.update_tracking_status()
        
        self._last_worked_calls_today = set()
        self.schedule_worked_calls_check()

        self.restore_window_position()






    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()        






    def setup_ui(self):
# Top frame bevat beide subframes naast elkaar
        top_frame = tk.Frame(self.root)
        top_frame.pack(padx=10, pady=5, fill=tk.X)

        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=0)

        # Spot Filters Frame (links, neemt beschikbare ruimte)
        filters_frame = tk.LabelFrame(top_frame, text="Spot Filters", relief="groove", bd=2)
        filters_frame.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew")

        tk.Label(filters_frame, text="Band:").grid(row=0, column=0, sticky="e")
        self.band_var = tk.StringVar()
        bands_with_all = ["ALL"] + list(BANDS.keys())
        self.band_menu = ttk.Combobox(filters_frame, textvariable=self.band_var, values=bands_with_all, state="readonly", width=10)
        font_large = tkinter.font.Font(family="Arial", size=12)
        self.band_menu.configure(font=font_large)
        self.band_menu.grid(row=0, column=1, padx=(2, 10), sticky=tk.W)
        self.band_menu.current(0)
        self.band_menu.bind("<<ComboboxSelected>>", lambda e: self.filter_spots())

        tk.Label(filters_frame, text="Mode:").grid(row=0, column=2, sticky="e")
        self.mode_var = tk.StringVar()
        modes_with_all = ["ALL"] + list(MODES.keys())
        self.mode_menu = ttk.Combobox(filters_frame, textvariable=self.mode_var, values=modes_with_all, state="readonly", width=10)
        font_small = tkinter.font.Font(family="Arial", size=12)
        self.mode_menu.configure(font=font_small)
        self.mode_menu.grid(row=0, column=3, padx=(2, 10), sticky=tk.W)
        self.mode_menu.current(0)
        self.mode_menu.bind("<<ComboboxSelected>>", lambda e: self.filter_spots())

        # Buttons Frame (rechts, met zelfde stijl en vaste breedte)
        buttons_frame = tk.LabelFrame(top_frame, text="Actions", relief="groove", bd=2)
        buttons_frame.grid(row=0, column=1, padx=(0, 0), pady=(0, 10), sticky="nsew")
        top_frame.columnconfigure(1, weight=1)

        buttons_frame.columnconfigure(0, weight=1)  # laat linker ruimte groeien
        buttons_frame.columnconfigure(1, weight=0)  # knop blijft vaste breedte
        buttons_frame.columnconfigure(2, weight=1)  # laat rechter ruimte groeien

        # Zet Send Spot in het midden
        tk.Label(buttons_frame).grid(row=0, column=0)  # lege linkerzijde
        send_spot_btn = tk.Button(buttons_frame, text="Send Spot", command=self.open_send_spot_popup,
                                fg="white", bg="green", width=12)
        send_spot_btn.grid(row=0, column=1, pady=5)
        tk.Label(buttons_frame).grid(row=0, column=2)  # lege rechterzijde

        style = ttk.Style(self.root)
        import tkinter.font as tkfont
        default_font = tkfont.nametofont("TkHeadingFont")
        bold_font = default_font.copy()
        bold_font.configure(weight="bold")
        style.configure("Treeview.Heading", font=bold_font)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.tab_spots = tk.Frame(self.notebook)
        self.notebook.add(self.tab_spots, text="Spots")

        self.tab_clusters = tk.Frame(self.notebook)
        self.notebook.add(self.tab_clusters, text="Clusters")

        self.cluster_tree = ttk.Treeview(self.tab_clusters, columns=("prefix", "host", "port"), show="headings")
        self.cluster_tree.heading("prefix", text="Prefix")
        self.cluster_tree.heading("host", text="Host")
        self.cluster_tree.heading("port", text="Port")

        self.cluster_tree.column("prefix", width=70, anchor="center")
        self.cluster_tree.column("host", width=100, anchor="center")
        self.cluster_tree.column("port", width=70, anchor="center")

        self.cluster_tree.tag_configure('oddrow', background='white')
        self.cluster_tree.tag_configure('evenrow', background='#f0f0f0')

        self.cluster_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.cluster_tree.bind("<Double-1>", self.on_cluster_double_click)

        # Buttons for edditing
        cluster_btn_frame = tk.Frame(self.tab_clusters)
        cluster_btn_frame.pack(pady=5)

        tk.Button(cluster_btn_frame, text="➕ Add", command=self.add_cluster).pack(side=tk.LEFT, padx=5)
        tk.Button(cluster_btn_frame, text="✏️ Edit", command=self.edit_cluster).pack(side=tk.LEFT, padx=5)
        tk.Button(cluster_btn_frame, text="❌ Delete", command=self.delete_cluster).pack(side=tk.LEFT, padx=5)

        # Additional settings: Host, Login and Reconnect button
        conn_frame = tk.LabelFrame(self.tab_clusters, text="Connection")
        conn_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky="e")
        self.hostport_var = tk.StringVar()
        tk.Label(conn_frame, textvariable=self.hostport_var, width=30, anchor="w", relief="sunken").grid(row=0, column=1, padx=(2, 10), sticky=tk.W)

        tk.Label(conn_frame, text="Login:").grid(row=1, column=0, sticky="e")
        self.login_var = tk.StringVar()
        tk.Entry(conn_frame, textvariable=self.login_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=(0, 5))

        self.connect_button = tk.Button(conn_frame, text="Reconnect", command=self.reconnect)
        self.connect_button.grid(row=0, column=2, rowspan=2, padx=10, sticky="w")

        last_used = self.load_last_used_cluster()
        if last_used:
            self.hostport_var.set(last_used)

        self.root.after(100, self.reconnect)

        self.tab_output = tk.Frame(self.notebook)
        self.notebook.add(self.tab_output, text="Console")

        tree_frame = tk.Frame(self.tab_spots)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree_scrollbar = tk.Scrollbar(tree_frame)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("time", "freq", "dx", "country", "spotter", "comment"),
            show="headings",
            yscrollcommand=tree_scrollbar.set
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.config(command=self.tree.yview)

        columns = {
            "time": {"width": 30},
            "freq": {"width": 50},
            "dx": {"width": 60},
            "country": {"width": 100},
            "spotter": {"width": 50},
            "comment": {"width": 150},
        }

        for col, options in columns.items():
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor=tk.CENTER, width=options["width"])

        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#f0f0f0')
        self.tree.tag_configure('worked_today', background='#ffd9b3')
        self.tree.tag_configure('worked', background='#b3e6ff')

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Linker frame voor labels
        legend_left = tk.Frame(bottom_frame)
        legend_left.pack(side="left")

        worked_legend = tk.Label(legend_left, text="Worked before", bg="#b3e6ff", relief="ridge", borderwidth=1, width=15)
        worked_legend.pack(side="left", padx=5)

        worked_today_legend = tk.Label(legend_left, text="Worked today", bg="#ffd9b3", relief="ridge", borderwidth=1, width=15)
        worked_today_legend.pack(side="left", padx=5)

        # Rechter frame voor Exit-knop
        exit_right = tk.Frame(bottom_frame)
        exit_right.pack(side="right")

        exit_btn = tk.Button(exit_right, text="Exit", command=self.on_close, fg="black", bg="lightgrey", width=12)
        exit_btn.pack(padx=10)



        self.output = tk.Text(self.tab_output, fg="white", bg="black", height=10, width=80)
        self.output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.spot_clicked)




    def check_ctydat_file(self):
        try:
            if not os.path.exists(DXCC_FILE):
                messagebox.showinfo(title="File Not Found",
                                    message="The file cty.dat was not found. It will now be downloaded.",
                                    parent=self.root)
                self.download_ctydat_file()
            self.dxcc_data = parse_cty_file(DXCC_FILE)
        except Exception as e:
            messagebox.showerror(title="Error",
                                message=f"Error loading data: {e}",
                                parent=self.root)
            self.dxcc_data = {}


    def download_ctydat_file(self):
        try:
            response = requests.get(ctydat_url)
            response.raise_for_status()
            with open(DXCC_FILE, "wb") as f:
                f.write(response.content)
            messagebox.showinfo(title="Download",
                                message="The file cty.dat has been downloaded successfully.",
                                parent=self.root)
            self.reconnect()                                
        except Exception as e:
            messagebox.showerror(title="Download Error",
                                message=f"Failed to download file: {e}",
                                parent=self.root)





    def open_send_spot_popup(self):
        popup = SendSpotPopup(self.root, self)
        self.root.wait_window(popup)

    def send_spot(self, dx, freq, remark):
        if self.writer is None:
            self.show_centered_message("Error", "Not connected to Telnet server!", icon="error")
            return

        message = f"dx {dx} {freq} {remark}\n"

        try:
            asyncio.run_coroutine_threadsafe(self._async_send(message), self.loop)
            self.show_centered_message("Sent", f"Spot sent:\n{message}", icon="info")
        except Exception as e:
            self.show_centered_message("Error sending", str(e), icon="error")


    def show_centered_message(self, title, message, icon="info", duration=2000):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.resizable(False, False)

        # Bereken positie in midden van hoofdvenster
        self.root.update_idletasks()
        popup_width = 300
        popup_height = 100
        main_x = self.root.winfo_rootx()
        main_y = self.root.winfo_rooty()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        x = main_x + (main_width - popup_width) // 2
        y = main_y + (main_height - popup_height) // 2
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        # Icon (optioneel)
        if icon == "info":
            icon_text = "ℹ️"
        elif icon == "error":
            icon_text = "❌"
        else:
            icon_text = ""

        tk.Label(popup, text=icon_text, font=("Arial", 16)).pack(pady=(10, 0))
        tk.Label(popup, text=message, font=("Arial", 10), wraplength=280).pack(pady=5)

        # Optioneel: knop toevoegen voor handmatig sluiten
        tk.Button(popup, text="OK", command=popup.destroy).pack(pady=10)

        popup.transient(self.root)
        popup.grab_set()

        # Sluit automatisch na 'duration' milliseconden (2000 ms = 2 sec)
        popup.after(duration, popup.destroy)

        self.root.wait_window(popup)


    async def _async_send(self, message):
        if self.writer is not None:
            self.writer.write(message.encode())
            await self.writer.drain()



    def reconnect(self):
        if self.connected:
            self.disconnect()
        self.connect()

########
    def on_cluster_double_click(self, event=None):
        selected = self.cluster_tree.selection()
        if not selected:
            return
        values = self.cluster_tree.item(selected[0], "values")
        if len(values) >= 3:
            prefix, host, port = values
            if self.connected:
                self.disconnect()
            self.hostport_var.set(f"{host}:{port}")
########
    def save_clusters_to_file(self):
        try:
            with open(CLUSTER_FILE, "w", encoding="utf-8") as f:
                json.dump(self.clusters_data, f, indent=2)
            self.load_host_file()
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
########
    def add_cluster(self):
        self.edit_cluster_dialog()
########
    def edit_cluster(self):
        selected = self.cluster_tree.selection()
        if not selected:
            return
        values = self.cluster_tree.item(selected[0], "values")
        if values:
            self.edit_cluster_dialog(values, selected[0])
########
    def delete_cluster(self):
        selected = self.cluster_tree.selection()
        if not selected:
            return
        values = self.cluster_tree.item(selected[0], "values")
        if not values:
            return
        confirm = messagebox.askyesno("Delete Cluster", f"Delete cluster {values[1]}:{values[2]}?")
        if confirm:
            self.clusters_data = [c for c in self.clusters_data if not (c["host"] == values[1] and str(c["port"]) == str(values[2]))]
            self.save_clusters_to_file()
#########
    def edit_cluster_dialog(self, values=None, item_id=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Cluster" if values else "Add Cluster")

        tk.Label(dialog, text="Prefix:").grid(row=0, column=0)
        prefix_var = tk.StringVar(value=values[0] if values else "")
        tk.Entry(dialog, textvariable=prefix_var).grid(row=0, column=1)

        tk.Label(dialog, text="Host:").grid(row=1, column=0)
        host_var = tk.StringVar(value=values[1] if values else "")
        tk.Entry(dialog, textvariable=host_var).grid(row=1, column=1)

        tk.Label(dialog, text="Port:").grid(row=2, column=0)
        port_var = tk.StringVar(value=values[2] if values else "")
        tk.Entry(dialog, textvariable=port_var).grid(row=2, column=1)

        def save():
            prefix = prefix_var.get().strip()
            host = host_var.get().strip()
            try:
                port = int(port_var.get().strip())
            except ValueError:
                messagebox.showerror("Invalid", "Port must be a number")
                return

            if not host:
                messagebox.showerror("Invalid", "Host is required")
                return

            new_entry = {"prefix": prefix, "host": host, "port": port}

            if values:
                self.clusters_data = [c for c in self.clusters_data if not (c["host"] == values[1] and str(c["port"]) == str(values[2]))]
            self.clusters_data.append(new_entry)

            self.save_clusters_to_file()
            dialog.destroy()

        tk.Button(dialog, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=5)




    def update_treeview_colors(self):
        worked_calls_today = self.get_worked_calls_today() if self.get_worked_calls_today else set()
        current_worked_calls = self.get_worked_calls() if self.get_worked_calls else set()

        for i, item in enumerate(self.tree.get_children()):
            values = self.tree.item(item, "values")
            dx_call = values[2].upper()

            if dx_call in worked_calls_today:
                tag = 'worked_today'
            elif dx_call in current_worked_calls:
                tag = 'worked'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            self.tree.item(item, tags=(tag,))



    def schedule_worked_calls_check(self):
        current = self.get_worked_calls_today() if self.get_worked_calls_today else set()
        if current != self._last_worked_calls_today:
            self._last_worked_calls_today = current
            self.update_treeview_colors()
        self.root.after(10000, self.schedule_worked_calls_check)







    def load_host_file(self, default=CLUSTER_FILE):
        try:
            # Bestaat het clusterbestand niet? Maak een default aan
            if not os.path.exists(default):
                default_data = [
                    {"prefix": "PI4CC", "host": "dcx.pi4cc.nl", "port": 8000}
                ]
                with open(default, "w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=4)

            with open(default, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.hosts = []
            self.clusters_data = []

            if hasattr(self, 'cluster_tree'):
                self.cluster_tree.delete(*self.cluster_tree.get_children())

            for idx, item in enumerate(data):
                if isinstance(item, dict):
                    prefix = item.get("prefix", "")
                    host = item.get("host", "")
                    port = item.get("port", 0)
                    if host and port:
                        self.clusters_data.append({"prefix": prefix, "host": host, "port": port})
                        self.hosts.append(f"{host}:{port}")
                        if hasattr(self, 'cluster_tree'):
                            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                            self.cluster_tree.insert("", "end", values=(prefix, host, port), tags=(tag,))

            if self.hosts and not self.hostport_var.get():
                self.hostport_var.set(self.hosts[0])

        except Exception as e:
            messagebox.showerror("Host File Error", str(e))









    def save_last_used_cluster(self, host, port, login):
        import configparser
        config = configparser.ConfigParser()
        config["LAST"] = {
            "host": host,
            "port": str(port)
        }
        config["LOGIN"] = {
            "user": login
        }
        with open(INI_FILE, "w", encoding="utf-8") as f:
            config.write(f)







    def load_last_used_cluster(self):
        config = configparser.ConfigParser()
        if not os.path.exists(INI_FILE):
            return None
        config.read(INI_FILE, encoding="utf-8")

        host = config["LAST"].get("host", "")
        port = config["LAST"].get("port", "")
        login = config["LOGIN"].get("user", "")

        if host and port:
            hostport = f"{host}:{port}"
            self.hostport_var.set(hostport)
            self.login_var.set(login)
            return hostport
        return None






    def select_hostport(self, event=None):
        value = self.hostport_var.get()
        if ':' in value:
            host, port_str = value.split(':', 1)
            self.host_var = host.strip()
            try:
                port = int(port_str.strip())
                self.port_var = port
            except ValueError:
                self.port_var = None
        else:
            self.host_var = value.strip()
            self.port_var = None




    def select_host(self, event=None):
        index = self.host_menu.current()
        if index >= 0 and index < len(self.hosts):
            host = self.hosts[index]
            self.host_var.set(host["host"])
            self.port_var.set(str(host["port"]))





    def toggle_connection(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()





    def connect(self):
        hostport = self.hostport_var.get()
        login = self.login_var.get()

        if ':' not in hostport:
            messagebox.showerror("Error", "Host:Port must be in format hostname:port")
            return

        host, port_str = hostport.split(":", 1)
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return

        self.output.insert(tk.END, f"Connecting to {host}:{port}...\n")
        self.output.see(tk.END)

        future = asyncio.run_coroutine_threadsafe(self.telnet_client(host, port, login), self.loop)

        self.save_last_used_cluster(host, port, login)

        self.connected = True
        self.connect_button.config(text="Disconnect")




    def disconnect(self):
        self.output.insert(tk.END, "Disconnect requested.\n")
        self.output.see(tk.END)

        if self.writer:
            self.writer.close()
            asyncio.run_coroutine_threadsafe(self.writer.wait_closed(), self.loop)

            self.writer = None

        self.connected = False
        self.connect_button.config(text="Connect")




    async def telnet_client(self, host, port, login):
        try:
            reader, writer = await asyncio.open_connection(host, port)
            self.writer = writer
            self.output.insert(tk.END, f"Connected to {host}:{port}\n")
            self.output.see(tk.END)

            # Wait for login prompt
            prompt = await reader.readuntil(b"login:")
            self.output.insert(tk.END, prompt.decode(errors="ignore"))
            self.output.see(tk.END)

            # Send login
            writer.write((login + "\n").encode())
            await writer.drain()

            # Send SH/DX direct after login
            writer.write(b"SH/DX\n")
            await writer.drain()

            # Process incoming lines
            while True:
                line = await reader.readline()
                if not line:
                    break
                decoded = line.decode(errors="ignore").strip()
                if decoded:
                    self.output.insert(tk.END, decoded + "\n")
                    self.output.see(tk.END)
                    self.parse_spot(decoded)
        except Exception as e:
            try:
                self.output.insert(tk.END, f"Error: {e}\n")
                self.output.see(tk.END)
            except tk.TclError:
                pass
        finally:
            self.connected = False
            try:
                if self.connect_button.winfo_exists():
                    self.connect_button.config(text="Connect")
            except tk.TclError:
                pass








    def parse_spot(self, line):
        # SH/DX: starts with frequency and contains a date in the format 28-May-2025
        if re.match(r"^\d+\.\d+", line) and re.search(r"\d{1,2}-[A-Za-z]{3}-\d{4}", line):
            self.parse_shdx_line(line)
        elif line.startswith("DX de"):
            self.parse_live_line(line)
        else:
            pass





    def get_country_from_call(self, call):
        if not call:
            return ("", "")

        call = call.strip().upper()
        best_match = None
        best_prefix_len = 0

        for entry in self.dxcc_data:
            for raw_prefix in entry.prefixes:
                # Strip formatting marks: ; = ( ) * [ ]
                prefix = re.sub(r'[=;()\[\]*]', '', raw_prefix).strip().upper()

                if call.startswith(prefix) and len(prefix) > best_prefix_len:
                    best_match = entry
                    best_prefix_len = len(prefix)

        if best_match:
            return (best_match.name, best_match.continent)  # Or flag, cq_zone, etc.

        return ("", "")




    def parse_shdx_line(self, line):
        match = re.match(
            r"^(?P<freq>\d+\.\d+)\s+(?P<dx>\S+)\s+(?P<date>\d{1,2}-[A-Za-z]{3}-\d{4})\s+(?P<time>\d{4})Z\s+(?P<comment>.*?)\s*<(?P<spotter>[^>]+)>",
            line
        )
        if not match:
            return

        try:
            freq_khz = float(match.group("freq"))
            freq = f"{freq_khz / 1000:.4f}"

            dx = match.group("dx")
            date_str = match.group("date")
            time_str = match.group("time")
            comment = match.group("comment").strip()
            spotter = match.group("spotter")

            dt = datetime.strptime(f"{date_str} {time_str}", "%d-%b-%Y %H%M")
            timestr = dt.strftime("%H:%M")

            country, flag = self.get_country_from_call(dx)

            spot = {
                "freq": freq,
                "dx": dx,
                "time": timestr,
                "spotter": spotter,
                "comment": comment,
                "country": country,
                "flag": flag,
                "datetime": dt,
            }

            self.spots.append(spot)
            self.spots.sort(key=lambda s: s["datetime"] or datetime.min, reverse=True)

            self.tree.delete(*self.tree.get_children())
            for idx, spot in enumerate(self.spots):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                self.tree.insert("", "end", values=(
                    spot["time"],
                    spot["freq"],
                    spot["dx"],
                    spot.get("country", ""),
                    spot["spotter"],
                    spot["comment"]
                ), tags=(tag,))

            self.update_treeview_colors()
        except Exception as e:
            #print(f"Parse error in parse_shdx_line: {e}")
            return










    def parse_live_line(self, line):
        if not line.startswith("DX de"):
            return
        try:
            parts = line.split()
            spotter = parts[2].rstrip(":")
            freq_khz = float(parts[3])
            freq = freq_khz / 1000.0
            dx = parts[4]

            time_raw = parts[-1]
            cleaned_time = re.sub(r"[^\d]", "", time_raw)
            time = f"{cleaned_time[:2]}:{cleaned_time[2:]}" if len(cleaned_time) == 4 else ""

            comment = " ".join(parts[5:-1]) if len(parts) > 6 else ""

            freq_khz_int = int(freq * 1000)
            mode = ""

            for m, ranges in MODES.items():
                for low, high in ranges:
                    if low <= freq_khz_int <= high:
                        mode = m
                        
                        break
                if mode:
                    break

            country, flag = self.get_country_from_call(dx)

            spot = {
                "freq": freq,
                "dx": dx,
                "spotter": spotter,
                "mode": mode,
                "comment": comment,
                "time": time,
                "country": country,
                "flag": flag,
            }

            self.spots.insert(0, spot)
            if len(self.spots) > 100:
                self.spots.pop()

            self.handle_new_spot(spot)

        except Exception as e:
            print(f"Parse error in parse_live_line: {e}")



    
    def handle_new_spot(self, spot):
        if self.spot_matches_filters(spot):
            self.add_spot_to_treeview(spot)




    def add_spot_to_treeview(self, spot):
        if not self.spot_matches_filters(spot):
            return

        dx_call = spot.get("dx", "").upper()
        worked_calls_today = self.get_worked_calls_today() if self.get_worked_calls_today else set()
        current_worked_calls = self.get_worked_calls() if self.get_worked_calls else set()

        try:
            freq_str = f"{float(spot['freq']):.4f}"
        except (ValueError, TypeError):
            freq_str = spot['freq']

        if dx_call in worked_calls_today:
            tag = 'worked_today'
        elif dx_call in current_worked_calls:
            tag = 'worked'
        else:
            tag = ''

        self.tree.insert(
            "", 0,
            values=(
                spot["time"],
                freq_str,
                spot["dx"],
                spot.get("country", ""),
                spot["spotter"],
                spot["comment"]
            ),
            tags=(tag,)
        )

        children = self.tree.get_children()
        if len(children) > 100:
            self.tree.delete(children[-1])

        self.update_treeview_colors()






    def filter_spots(self):
        self.tree.delete(*self.tree.get_children())
        filtered_spots = []

        for spot in self.spots:
            if self.spot_matches_filters(spot):
                filtered_spots.append(spot)

        for row_index, spot in enumerate(filtered_spots):
            tag = 'evenrow' if row_index % 2 == 0 else 'oddrow'
            freq_str = f"{float(spot['freq']):.4f}"
            self.tree.insert("", "end", values=(
                spot["time"],
                freq_str,
                spot["dx"],
                spot.get("country", ""),
                spot["spotter"],
                spot["comment"]
            ), tags=(tag,))

        self.update_treeview_colors()

        children = self.tree.get_children()
        if children:
            self.tree.see(children[0])





    def spot_matches_filters(self, spot):
        band = self.band_var.get()
        mode = self.mode_var.get()

        try:
            freq_mhz = float(spot["freq"])
        except (ValueError, TypeError):
            return False

        # Bandfilter
        if band != "ALL":
            low, high = BANDS.get(band, (0, float("inf")))
            if not (low <= freq_mhz <= high):
                return False

        # Modefilter (based on frequency-analyses)
        if mode != "ALL":
            for m, ranges in MODES.items():
                if m == mode:
                    for low, high in ranges:
                        if low <= freq_mhz <= high:
                            return True
                    return False
            return False

        return True






    def on_close(self):
        self.connected = False
        if hasattr(self, 'writer') and self.writer is not None:
            try:
                future = asyncio.run_coroutine_threadsafe(self.disconnect_async(), self.loop)
                future.result(timeout=1)
            except Exception as e:
                print(f"Error disconnecting during closing: {e}")

        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.save_window_position(x, y)

        self.root.destroy()


    def save_window_position(self, x, y):
        config = configparser.ConfigParser()
        if os.path.exists(INI_FILE):
            config.read(INI_FILE, encoding="utf-8")
        if "WINDOW" not in config:
            config["WINDOW"] = {}
        config["WINDOW"]["x"] = str(x)
        config["WINDOW"]["y"] = str(y)
        with open(INI_FILE, "w", encoding="utf-8") as f:
            config.write(f)

    def restore_window_position(self):
        config = configparser.ConfigParser()
        if not os.path.exists(INI_FILE):
            return
        config.read(INI_FILE, encoding="utf-8")
        try:
            x = int(config["WINDOW"].get("x", "100"))
            y = int(config["WINDOW"].get("y", "100"))
            self.root.geometry(f"+{x}+{y}")
        except Exception as e:
            print(f"Error restoring window position: {e}")




    async def disconnect_async(self):
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                print(f"Error during async disconnect:{e}")
            finally:
                self.writer = None





    def update_tracking_status(self):
            if not hasattr(self, 'tracking_status_label'):
                self.tracking_status_label = ttk.Label(self.root, text="", font=("Segoe UI", 9, "bold"))
                self.tracking_status_label.pack(pady=(0, 5))
            if self.tracking_var and self.tracking_var.get():
                self.tracking_status_label.config(text="Hamlib Tracking: ✅ Enabled", foreground="green")
            else:
                self.tracking_status_label.config(text="Hamlib Tracking: ❌ Disabled", foreground="red")
            self.root.after(500, self.update_tracking_status)

    
    
    
    def spot_clicked(self, event):
            try:
                selected = self.tree.selection()
                if not selected:
                    return
                values = self.tree.item(selected[0])["values"]
                raw_freq = values[1]
                to_call = values[2]
                gui_mode = self.mode_var.get()
                hz = int(float(raw_freq) * 1_000_000)
                
                try:
                    freq_mhz = f"{float(raw_freq):.5f}"

                except ValueError:
                    freq_mhz = ""
                if gui_mode == "PHONE" or gui_mode == "ALL":
                    resolved_mode = "USB" if hz > 10000000 else "LSB"
                else:
                    resolved_mode = gui_mode
                if self.on_callsign_selected:
                    self.on_callsign_selected(to_call, freq=freq_mhz, mode=resolved_mode)
                if not (self.tracking_var and self.tracking_var.get()):
                    return
                                
                with socket.create_connection((self.rigctl_host, self.rigctl_port), timeout=2) as s:
                    s.sendall(f"F {hz}\n".encode())
                    _ = s.recv(1024)
                    if resolved_mode and resolved_mode not in ("ALL", "DIGITAL"):
                        s.sendall(f"M {resolved_mode} -1\n".encode())
                        _ = s.recv(1024)
            except Exception:
                pass


class SendSpotPopup(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("Send Spot")
        self.resizable(False, False)

        callsign_var = tk.StringVar()
        callsign_var.trace("w", lambda *args: callsign_var.set(callsign_var.get().upper()))

        self.update_idletasks()
        popup_width = 300
        popup_height = 160

        main_x = parent.winfo_rootx()
        main_y = parent.winfo_rooty()
        main_width = parent.winfo_width()
        main_height = parent.winfo_height()

        x = main_x + (main_width - popup_width) // 2
        y = main_y + (main_height - popup_height) // 2
        self.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        entry_frame = tk.Frame(self)
        entry_frame.pack(padx=10, pady=10)

        tk.Label(entry_frame, text="DX Station:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_dx = tk.Entry(entry_frame, textvariable=callsign_var)
        self.entry_dx.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(entry_frame, text="Freq (kHz):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.freq_entry = tk.Entry(entry_frame)
        self.freq_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(entry_frame, text="Remark:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.remark_entry = tk.Entry(entry_frame)
        self.remark_entry.grid(row=2, column=1, padx=5, pady=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=(0, 10))

        send_btn = tk.Button(button_frame, text="Send", command=self.send_spot, width=10, bg="red", fg="white")
        send_btn.pack(side="left", padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy, width=10, bg="lightgrey", fg="black")
        cancel_btn.pack(side="left", padx=10)

    def send_spot(self):
        dx = self.entry_dx.get().strip()
        freq = self.freq_entry.get().strip()
        remark = self.remark_entry.get().strip()

        if not dx or not freq:
            tk.messagebox.showwarning("Incomplete", "DX and frequency are required.")
            self.lift()
            self.focus_force()
            return

        if not freq.isdigit():
            tk.messagebox.showerror("Invalid input", "Frequency must consist of numbers only.")
            self.lift()
            self.focus_force()
            return

        self.app.send_spot(dx, freq, remark)
        self.destroy()









# Used when running stand alone
if __name__ == "__main__":
    root = tk.Tk()
    root.title(f"DX Cluster Telnet Client - {VERSION_NUMBER}")
    app = DXClusterApp(root)
    root.mainloop()
  



# Used when opened from MiniBook
def launch_dx_spot_viewer(
    rigctl_host="127.0.0.1",
    rigctl_port=4532,
    tracking_var=None,
    on_callsign_selected=None,
    get_worked_calls=None,
    get_worked_calls_today=None,
    parent_window=None
):
    if parent_window is None:
        parent_window = tk.Toplevel()
        parent_window.resizable(True, True)

    DXClusterApp(
        parent_window,
        rigctl_host,
        rigctl_port,
        tracking_var,
        on_callsign_selected,
        get_worked_calls,
        get_worked_calls_today
    )