#**********************************************************************************************************************************
# File          :   MiniBook.py
# Project       :   A JSON Based logbook for portable use.
# Description   :   Logs basic contact information to json
# Date          :   18-10-2024
# Authors       :   Bjorn Pasteuning - PD5DJ
# Website       :   https://wwww.pd5dj.nl
#
# Version history
#   18-10-2024  :   1.0.0   - Initial basics running
#   20-10-2024  :   1.0.7   - Added DXCC lookup
#   20-10-2024  :   1.0.8   - If DXCC lookup file is missing, added download option
#   21-10-2024  :   1.0.9   - Basic Log viewer added
#   22-10-2024  :   1.1.0   - Search function added
#   22-10-2024  :   1.1.1   - Sorting function added
#   24-10-2024  :   1.1.2   - Scrollbar fixed in log viewer, layout changed, row color change fixed after search
#   25-10-2024  :   1.1.3   - Country column added
#   31-10-2024  :   1.1.4   - ADIF logbook process is changed in JSON
#                           - ADIF Export function added
#   01-11-2024  :   1.1.5   - Sorting fixed in logbook viewer
#                           - Locator field added to main window
#   02-11-2024  :   1.1.6   - Add flag images that matches with DXCC Entity
#                   1.1.7   - Added QSO delete option in Edit window
#                           - Improved prefix filtering
#   03-11-2024  :   1.1.8   - Yet another prefix filter improvement
#                   1.1.9   - Cosmetic improvements in main window
#                           - Major improvement prefix filter, source for dcxx.json is change to my own repo on github
#   06-11-2024  :   1.1.9a  - New Logbook structure
#                           - Configuration preferences: Station Callsign and Locator are now moved into new logbook structure
#                           - Detection/Conversion of older logbooks implemented
#   07-11-2024  :   1.1.9b  - Edit select & Delete functions changed to right-mouseclick in log viewer
#                           - Time Tracking checkbox add to menu, handy if you want to add QSO's afterwards
#   09-11-2024  :   1.1.9c  - Several bugs fixed:
#                           - If no call matched with dxcc.json then it logged the previous dxcc. Now loggin "[None]" when not found
#                           - Comboboxes, Band and Mode are now prohibited to edit manually
#                           - If you now go through all the entry fields with TAB and arrive at frequency, the cursor will be directly at the end so that it can be changed immediately
#                           - After logging, immediately move the cursor to the callsign entry
#                           - If you enter a frequency that does not match the band, adjust the band automatically and Visa Versa
#  10-11-2024   :   1.2.1   - ADIF Import added
#                           - File encoding fixed when reading ADIF files, now checking UTF-8 and LATIN-1
#                           - Comboboxes added in Edit QSO window
#                           - valid locator check added in Edit QSO window
#                           - Delete QSO button added in Edit QSO window
#  13-11-2024   :   1.2.2   - Row colors fixed when Searching/Sorting
#                           - When loading new logbook, treeview is now closed before loading. Not showing old loaded content
#  14-11-2024   :   1.2.3   - First implementation of Hamlib RigCtlD with frequency and mode readout
#                           - Error handling RigCTLD added
#                           - Locator check in Edit QSO fixed
#                           - Free port detection added, for multiple deamon instances on network
#  20-11-2024   :   1.2.3c  - Threading added for rigctld deamon
#                   1.2.3d  - Thread added for update frequency_mode
#                   1.2.4   - First implementation of WSJT-X ADIF UDP support
#  23-11-2024   :   1.2.4a  - Added posibility to connect to external rigctld server
#  24-11-2024   :   1.2.5   - Fix, When changing UDP port, it is was not updated until restart program
#                           - Confirmation on quitting program
#                           - Window position save / load added for Main and Logbook window
#  25-11-2024   :   1.2.6   - Parameters are now stored in user appdata folder
#                           - Export ADIF back to user select where to save method
#                           - Name entry added
#  01-12-2024   :   1.2.7   - More robust Config.ini handler added
#                           - Added load last logbook function upon start of MiniBook
#  19-04-2025   :   1.2.9   - Multiselect added in logbook for record deletion
#  21-04-2025   :           - Added Worked Before Frame at bottom of main window
#  27-04-2025   :   1.3.0   - MAJOR CHANGE:
#                           - Due many issues with integrating a Hamlib server, I have decided to remove all server related parts from MiniBook.
#                           - Minibook can now only connect to an external Hamlib service.
#                           - Example Batch files are added how to start a service in the background.
#                           - Fixed RST format 59/599 on mode change
#                           - Fixed manual RST edit in edit window
#                           - Fixed Date / Time entry, if incorrect format was entered logbook could not be loaded correctly anymore.
#                           - Added Satellite Entry field, names are stored in satellites.txt and can be updated with getsatnames.py
#                             Satellite fields are now imported from ADIF, and Exported to ADIF
#  01-05-2025   :   1.3.1   - QRZ Lookup added, credentials entered in preference menu.
#                           - Layout change to support QRZ Lookup, Button added for Lookup
#                             QRZ Lookup ofcourse only works with a valid QRZ Lookup subscription
#                             QRZ Lookup only works with internet connection.
#                           - Added better Callsign filtering for QRZ lookup
#  03-05-2025               - Now when pressing TAB in callsign entry a QRZ Lookup will be performed automaticly.
#  05-05-2025   :   1.3.2   - Fix in ADIF export Submode.
#                           - Export to ADIF is 3 formats, POTA, WWFF and Normal
#                           - QSO Edit window re-arranged
#                           - Openarator field added in My Station Setup
#                           - POTA and WWFF entries added in logbook window
#                           - Hamlib status and loaded logbook now moven to title bar
# 09-05-2025    :   1.3.3   - QRZ API Upload added
#                           - ADIF Import Progressbar added
#                           - Frequency Input control added, type frequency in KHZ
#                           - Added "Dupe check of today", callsign will show red on orange when already worked that day.
#                           - Fix in logbook load function, Clearing old logbook upon cancelation of loading logbook
# 13-05-2025    :   1.3.4   - Export Selected records to ADIF added in Logbook Window
#                           - Added frequency offset control, user now can shift frequecy up and down in khz with - or +, ie +15 is 15khz up
#                           - log backup function added, when opening logbooks a copy is stored in backup-logs folder with timestamp
#                           - Fix QRZ upload record, Operator field was missing
# 17-05-2025    :   1.3.5   - Added, DX Summit DX Cluster window.
#                           - Click on spot, will send frequency and mode to logbook and sent to Hamlib
# 21-05-2025    :   1.3.6   - Bulkedit added when selecting multiple records.
#                           - Duplicate QSO finder added
# 29-05-2025    :   1.3.7   - Password(s) & API Keys have show buttons
#                           - dxcc.json is replaced by cty.dat, unfortunally cty.dat does not provide dxcc entity numbers, so Flag image had to be removed.
#                           - Worked before expanded with more matching colors
# 01-06-2025    :   1.3.8   - QSO's are now processed fully in cache, minimized disk writing time.. worked b4 lookup speed up.
# 02-06-2025    :   1.3.9   - Locator lookup added. When locator is entered heading and distance always calculated from these entries.
#                           - Fix Importing ADIF Duplicate records, when selecting ignore.. no files where added at all
#                           - Fix in QRZ Lookup when entering multiple / call was not found.. i.e. DK/PD5DJ/P was not found.
# 15-06-2025    :   1.4.0   - QRZ Lookup Fix, better filtering with dashes in callsigns.
#                             When no match, it will try to retrieve first and last name using base callsign.
#                             For example: if VK/PD5DJ is not found, it will use names from PD5DJ only.
#                           - Also when callsign retrieves no qrz data, fields are wiped also.
#                           - Heading and Distance calculation improved
# 05-07-2025    :   1.4.2   - ADIF import is now be processed threaded
# 03-08-2025    :   1.4.3   - Edit QSO, time validation was HH:MM now HH:MM:SS
# 09-08-2025    :           - Added WWFF/POTA/BOTA Prefix retreive function
#                           - Added lookup for Park/Bunker names
# 10-08-2025    :           - Changed filepath structure
# 11-08-2025    :   1.4.4   - Added mapping option to view references on map
#**********************************************************************************************************************************

from datetime import datetime, timedelta, date
from pathlib import Path
from tkcalendar import DateEntry
from tkinter import filedialog, messagebox, ttk
import configparser
import csv
import html
import ipaddress
import json
import math
import logging
import os
import platform
import re
import requests
import socket
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
import urllib.parse
import webbrowser
import xml.etree.ElementTree as ET
from DXCluster import launch_dx_spot_viewer
from cty_parser import parse_cty_file

import traceback

# ------- Set True if you want to print system wide debug information -------
DEBUG               = False

VERSION_NUMBER = ("v1.4.4")

# Configuration file path
SETTINGS_FOLDER     = Path.cwd() / "settings"
DATA_FOLDER         = Path.cwd() / "data"

CONFIG_FILE         = SETTINGS_FOLDER / "minibook.ini"
DXCC_FILE           = DATA_FOLDER / "cty.dat"
WWFF_FILE           = DATA_FOLDER / "wwff_directory.csv"
POTA_FILE           = DATA_FOLDER / "all_parks.csv"
POTA_MAP_FILE       = DATA_FOLDER / "dxcc_to_pota_map.json"
BOTA_FILE           = DATA_FOLDER / "wwbota.csv"
SAT_FILE            = DATA_FOLDER / "satellites.txt"
current_json_file   = None  # logbook file


# Global variables
tree                = None  # Logviewer Tree
Logbook_Window      = None  # Logbook window open / closed
Edit_Window         = None  # Edit window open / closed
Preference_Window   = None
Station_Setup_Window= None
About_Window        = None
workedb4_window     = None
dxcc_window         = None
workedb4_tree       = None
workedb4_frame      = None
dxspotviewer_window = None

# -------- Operating mode options --------
mode_options        = ["AM", "FM", "USB", "LSB", "SSB", "CW", "CW-R", "DIG", "RTTY", "MFSK", "DYNAMIC", "JT65", "JT8", "FT8", "PSK31", "PSK64", "PSK125", "QPSK31", "PKT","OLIVIA", "SSTV", "VARA","DOMINO"]
submode_options     = ["","FT4"]
# Initialize last_passband globally, starting with a default value (e.g., 0 or your choice)
last_passband = 0

# -------- RST Sent/Received options -------
rst_options         = [str(i) for i in range(51, 60)] + ["59+10dB", "59+20dB", "59+30dB", "59+40dB"]

# will be filled later with data from cty.dat
dxcc_data = []
ctydat_url            = "https://www.country-files.com/bigcty/cty.dat"

wwff_references = {}
wwffref_url = "https://wwff.co/wwff-data/wwff_directory.csv"

pota_references = {}
pota_url = "https://pota.app/all_parks.csv"

bota_references = {}
bota_url = "https://drive.usercontent.google.com/u/0/uc?id=1wZAOObnUmJTXFYPCAAqQPHgOnT3gaMa7&export=download"

#########################################################################################
#  ___ _   _ _  _  ___ _____ ___ ___  _  _ ___ 
# | __| | | | \| |/ __|_   _|_ _/ _ \| \| / __|
# | _|| |_| | .` | (__  | |  | | (_) | .` \__ \
# |_|  \___/|_|\_|\___| |_| |___\___/|_|\_|___/
#                                              
#########################################################################################

# Set up QRZ upload log file
logging.basicConfig(
    filename='qrz_upload_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_upload_result(message):
    """Append a message to the upload log file."""
    logging.info(message)

# Functions used with dxspotview.py
def get_worked_calls():
    return {qso.get("Callsign", "").upper() for qso in qso_lines}

def get_worked_calls_today():
    today_str = date.today().isoformat()
    return {
        qso.get("Callsign", "").upper()
        for qso in qso_lines
        if qso.get("Date") == today_str
    }

def open_dxspotviewer():
    global dxspotviewer_window
    if dxspotviewer_window is not None and dxspotviewer_window.winfo_exists():
        dxspotviewer_window.lift()
        return

    dxspotviewer_window = tk.Toplevel()
    dxspotviewer_window.resizable(False, False)

    def get_last_qso_callsign():
        return callsign_var.get().strip()

    def get_current_frequency():
        return frequency_var.get().strip()

    launch_dx_spot_viewer(
        rigctl_host=hamlib_ip_var.get().strip() or "127.0.0.1",
        rigctl_port=int(hamlib_port_var.get()) if str(hamlib_port_var.get()).isdigit() else 4532,
        tracking_var=freqmode_tracking_var,
        on_callsign_selected=handle_callsign_from_spot,
        get_worked_calls=get_worked_calls,
        get_worked_calls_today=get_worked_calls_today,
        get_last_qso_callsign=get_last_qso_callsign,
        get_current_frequency=get_current_frequency,        
        parent_window=dxspotviewer_window
    )



# Function to update Title
def update_title(root, version, filename=None, status_text=None):
    parts = [f"MiniBook {version}"]
    if filename:
        parts.append(f"[{os.path.basename(filename)}]")
    if status_text:
        parts.append(status_text)
    root.title(" - ".join(parts))


# Function to reset variables and entries when logbook file failed to load.
def no_file_loaded():
    global current_json_file

    current_json_file = None # Reset the current_json_file to None
    update_title(root, VERSION_NUMBER, "Load or create logbook first!", radio_status_var.get())
    my_locator_var.set("")
    my_callsign_var.set("")
    my_operator_var.set("")
    my_location_var.set("")

    my_callsign_entry.config(textvariable=my_callsign_var)
    my_operator_entry.config(textvariable=my_operator_var)
    my_locator_entry.config(textvariable=my_locator_var)
    my_location_entry.config(textvariable=my_location_var)
    my_wwff_entry.config(textvariable=my_wwff_var)
    my_pota_entry.config(textvariable=my_pota_var)
    my_bota_entry.config(textvariable=my_bota_var)

    file_menu.entryconfig("Station setup", state="disabled")


# Function to restore fields after logging or wiping
def reset_fields():
    comment_var.set("")
    last_qso_label.config(text="")
    QRZ_status_label.config(text="")
    callsign_var.set("")
    name_var.set("")
    city_var.set("")
    zipcode_var.set("")
    address_var.set("")
    qsl_info_var.set("")
    satellite_var.set("")
    submode_var.set("")
    on_mode_change() 
    locator_var.set("")    
    callsign_entry.focus_set()
    wwff_var.set("")
    wwff_park_name_var.set("")
    pota_var.set("")
    pota_park_name_var.set("")
    bota_name_var.set("")
    bota_var.set("")



# Function to clear My Station Parameters in GUI
def clear_station_labels():
    # Clear station info StringVars
    my_callsign_var.set("")
    my_operator_var.set("")
    my_locator_var.set("")
    my_location_var.set("")
    my_wwff_var.set("")
    my_pota_var.set("")
    my_bota_var.set("")



#Checks if a given maidenhead locator is valid for example JO22LO49
def is_valid_locator(locator):
    if locator == "":
        return True
    if len(locator) < 4 or len(locator) % 2 != 0:
        return False
    # Regex pattern:
    # - [A-R]{2} : veld
    # - \d{2} : vierkant
    # - ([A-X]{2})? : optioneel subsquare
    # - (\d{2})? : optioneel extended vierkant (cijfers)
    pattern = r'^[A-R]{2}\d{2}([A-X]{2})?(\d{2})?$'
    return bool(re.match(pattern, locator, re.IGNORECASE))



#Converts Maidenhead locator to Latttitude and Longitude coordinates
def maidenhead_to_latlon(locator):
    """
    Convert Maidenhead locator (2/4/6/8 characters) to (lat, lon) at the center of the grid square.
    Returns: (latitude, longitude) as floats rounded to 6 decimals.
    """

    loc = locator.strip().upper()
    if len(loc) < 2:
        raise ValueError("Locator must be at least 2 characters")

    # basis (fields)
    lon = (ord(loc[0]) - ord('A')) * 20.0 - 180.0
    lat = (ord(loc[1]) - ord('A')) * 10.0 - 90.0

    # squares (digits)
    if len(loc) >= 4:
        lon += int(loc[2]) * 2.0
        lat += int(loc[3]) * 1.0

    # subsquares (letters A-X)
    if len(loc) >= 6:
        # 2 degrees / 24 = 5' = 0.083333333... ; 1 degree / 24 = 2.5' = 0.041666666...
        lon += (ord(loc[4]) - ord('A')) * (2.0 / 24.0)
        lat += (ord(loc[5]) - ord('A')) * (1.0 / 24.0)

    # optional extended digits (7/8 chars)
    if len(loc) >= 8:
        lon += int(loc[6]) * (2.0 / 24.0 / 10.0)
        lat += int(loc[7]) * (1.0 / 24.0 / 10.0)

    # center-offset afhankelijk van precisie
    if len(loc) >= 8:
        lon += (2.0 / 24.0 / 10.0) / 2.0
        lat += (1.0 / 24.0 / 10.0) / 2.0
    elif len(loc) >= 6:
        lon += (2.0 / 24.0) / 2.0
        lat += (1.0 / 24.0) / 2.0
    elif len(loc) >= 4:
        lon += 1.0
        lat += 0.5
    else:
        lon += 10.0
        lat += 5.0

    return round(lat, 6), round(lon, 6)
    

# Opens OpenStreetMap and shows pins on map with reference number and name, with a line showing distance in tooltip
def open_osm_map(lat_var, long_var, my_locator_var, my_callsign_var, ref, name):
    my_lat, my_lon = maidenhead_to_latlon(my_locator_var.get())
    my_callsign = my_callsign_var.get().strip().upper()

    lat = lat_var.get().strip()
    lon = long_var.get().strip()

    if lat and lon:
        ref_escaped = html.escape(ref).replace("'", "\\'")
        name_escaped = html.escape(name).replace("'", "\\'")

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <title>BOTA /POTA / WWFF reference Mapping</title>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0">

          <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
          <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

          <style>
            #map {{ height: 100vh; margin:0; padding:0; }}
            html, body {{ height: 100%; margin:0; padding:0; }}
            .leaflet-tooltip {{
                background: white;
                border: 1px solid black;
                border-radius: 4px;
                padding: 2px 5px;
                font-size: 12px;
                font-weight: bold;
            }}
          </style>
        </head>
        <body>
          <div id="map"></div>
          <script>
            var map = L.map('map').setView([{my_lat}, {my_lon}], 10);

            // Baselayers
            var osm = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
              maxZoom: 19,
              attribution: '© OpenStreetMap contributors'
            }}).addTo(map);

            var esriSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
              maxZoom: 19,
              attribution: 'Tiles © Esri'
            }});

            var esriLabels = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
              maxZoom: 19,
              attribution: 'Labels © Esri',
              pane: 'overlayPane'
            }});

            var esriHybrid = L.layerGroup([esriSat, esriLabels]);

            // Markers
            var blueIcon = L.icon({{
              iconUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png',
              shadowUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png',
              iconSize:     [25, 41],
              iconAnchor:   [12, 41],
              popupAnchor:  [1, -34],
              shadowSize:   [41, 41]
            }});

            var redIcon = L.icon({{
              iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
              shadowUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png',
              iconSize:     [25, 41],
              iconAnchor:   [12, 41],
              popupAnchor:  [1, -34],
              shadowSize:   [41, 41]
            }});

            var marker1 = L.marker([{my_lat}, {my_lon}], {{icon: blueIcon}})
                .addTo(map)
                .bindPopup('Your Location:<br><b>{my_callsign}</b>')
                .openPopup();

            var marker2 = L.marker([{lat}, {lon}], {{icon: redIcon}})
                .addTo(map)
                .bindPopup('<b>{ref_escaped}</b><br>{name_escaped}')
                .openPopup();

            var latlngs = [
                [{my_lat}, {my_lon}],
                [{lat}, {lon}]
            ];
            var polyline = L.polyline(latlngs, {{color: 'green'}}).addTo(map);

            var distance = map.distance(
                L.latLng({my_lat}, {my_lon}),
                L.latLng({lat}, {lon})
            ) / 1000;
            distance = distance.toFixed(1);

            polyline.bindTooltip(distance + ' km', {{
                permanent: true,
                direction: 'center',
                className: 'distance-tooltip'
            }}).openTooltip();

            var group = new L.featureGroup([marker1, marker2, polyline]);
            map.fitBounds(group.getBounds().pad(0.5));

            // Layer control
            var baseMaps = {{
                "OpenStreetMap": osm,
                "Satelliet": esriSat,
                "Satelliet + Labels": esriHybrid
            }};
            L.control.layers(baseMaps).addTo(map);
          </script>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            f.write(html_template)
            temp_file_path = f.name

        webbrowser.open(f"file://{temp_file_path}")

    else:
        messagebox.showwarning("No Coordinates", "No valid coordinates found.")






    


# Frequency ranges and default frequencies for each band
band_ranges = {
    "2200m": (0.1357, 0.1358),
    "160m": (1.8, 2.0),
    "80m": (3.5, 4.0),
    "60m": (5.3515, 5.3665),
    "40m": (7.0, 7.3),
    "30m": (10.1, 10.15),
    "20m": (14.0, 14.35),
    "17m": (18.068, 18.168),
    "15m": (21.0, 21.45),
    "12m": (24.89, 24.99),
    "11m": (26.0, 28.0),
    "10m": (28.0, 29.97),
    "6m": (50.0, 54.0),
    "4m": (70.0, 70.5),
    "2m": (144.0, 148.0),
    "1.25m": (220.0, 225.0),
    "70cm": (420.0, 450.0),
    "33cm": (902.0, 928.0),
    "23cm": (1200.0, 1300.0),
    "13cm": (2300.0, 2450.0),
}

# Mapping from band to default frequency
band_to_frequency = {
    "2200m": "0.1356",
    "160m": "1.8500",
    "80m": "3.6500",
    "60m": "5.3600",
    "40m": "7.0000",
    "30m": "10.1000",
    "20m": "14.0000",
    "17m": "18.1000",
    "15m": "21.0000",
    "12m": "24.8900",
    "11m": "27.0000",
    "10m": "28.0000",
    "6m": "50.0000",
    "4m": "70.0000",
    "2m": "144.0000",
	"1.25m": "220.0000",
    "70cm": "430.0000",
	"33cm": "902.0000",
    "23cm": "1296.0000",
    "13cm": "2300.0000"
}




def on_mode_change(event=None):
    selected_mode = mode_var.get().upper()
    if selected_mode in ["CW", "CW-R", "RTTY", "OLIVIA", "PSK31", "PSK64", "PSK125", "MFSK", "DOMINO", "VARA", "SSTV"]:
        rst_sent_var.set("599")
        rst_received_var.set("599")
    else:
        rst_sent_var.set(rst_options[8])
        rst_received_var.set(rst_options[8])


def download_satellites():
    try:
        urls = [
            "https://celestrak.org/NORAD/elements/amateur.txt",
            "https://celestrak.org/NORAD/elements/cubesat.txt"
        ]
        satellite_names = []
        for url in urls:
            response = requests.get(url)
            tle_data = response.text
            lines = tle_data.strip().splitlines()

            for i in range(0, len(lines), 3):
                if i + 2 >= len(lines):
                    continue
                name_line = lines[i].strip()
                if "(" in name_line and ")" in name_line:
                    name = name_line.split("(")[-1].split(")")[0].strip()
                else:
                    name = name_line.strip()
                satellite_names.append(name)

        satellite_names = sorted(set(satellite_names))

        with open("satellites.txt", "w") as f:
            for name in satellite_names:
                f.write(name + "\n")

        messagebox.showinfo("Success", "Satellites downloaded successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download satellites:\n{e}")


def load_satellite_names(filename=SAT_FILE):
    try:
        with open(filename, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("satellites.txt not found!.")
        return []



# Function to update radio status
# 0 = dummy
# 10 = connecting
# 11 = connected
# 12 = disconnected
# 20 = noradio
def gui_state_control(status):
    global radio_status_var, hamlib_ip_var, hamlib_port_var


    if status == 10:
        radio_status_var.set("Connecting...")

    elif status == 11:
        radio_status_var.set(f"Connected to {hamlib_ip_var.get()}:{hamlib_port_var.get()}")

        freq_entry.config(fg="red", state='readonly')
        band_combobox.config(state='disabled')        

    elif status == 12:
        radio_status_var.set("Disconnected")
        freq_entry.config(fg="black", state='normal')
        band_combobox.config(state='normal')
  
    elif status == 20:
        radio_status_var.set("Not available")
  
    else:  # Default to idle or unknown state
        radio_status_var.set("Idle")

    update_title(root, VERSION_NUMBER, current_json_file, radio_status_var.get())
    
    
def open_backup_folder():
    backup_dir = config.get("General", "backup_folder", fallback="").strip()
    if not backup_dir or not os.path.exists(backup_dir):
        messagebox.showwarning("Backup Folder Not Set", "No valid backup folder is set in Preferences.")
        return

    try:
        # Cross-platform folder open
        if sys.platform == "win32":
            os.startfile(backup_dir)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", backup_dir])
        else:
            subprocess.Popen(["xdg-open", backup_dir])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open the backup folder:\n{e}")


def calculate_headings(lat1, lon1, lat2, lon2):
    """
    Bereken short path en long path headings tussen twee punten (in graden).
    """
    # Convert naar radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon_rad = math.radians(lon2 - lon1)

    x = math.sin(delta_lon_rad) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon_rad)

    initial_bearing_rad = math.atan2(x, y)
    initial_bearing_deg = (math.degrees(initial_bearing_rad) + 360) % 360  # SP

    long_path = (initial_bearing_deg + 180) % 360  # LP is SP + 180°

    return round(initial_bearing_deg), round(long_path)        
    


#########################################################################################
#  _    ___   ___ ___  ___   ___  _  __     _ ___  ___  _  _ 
# | |  / _ \ / __| _ )/ _ \ / _ \| |/ /  _ | / __|/ _ \| \| |
# | |_| (_) | (_ | _ \ (_) | (_) | ' <  | || \__ \ (_) | .` |
# |____\___/ \___|___/\___/ \___/|_|\_\  \__/|___/\___/|_|\_|
#                                                            
#########################################################################################

# Function to create a new JSON file with "Station" and "Logbook" structure
def create_new_json():
    global current_json_file, Logbook_Window, logbook_window_open

    if current_json_file:
        response = messagebox.askquestion("Confirmation", "This wil close the currently loaded logbook\n\nAre you sure?")
        
        if response == 'no':
            return

    # Clear loaded json file
    no_file_loaded()

    # Check if the logbook window is open, and close it if necessary
    if Logbook_Window is not None and Logbook_Window.winfo_exists():
        # Close the logbook window
        Logbook_Window.destroy()
        Logbook_Window = None  # Reset the logbook window reference

    current_json_file = filedialog.asksaveasfilename(defaultextension=".mbk", filetypes=[("MiniBook files", "*.mbk")])
    if current_json_file:
        # Initialize JSON structure with Station and an empty Logbook
        data = {
            "Station": {
                "Callsign": "N0CALL",  # Add your default station callsign or leave blank
                "Operator": "N0CALL",
                "Locator": "AA11BB",  # Placeholder, adjust as needed
                "Location": "",
                "WWFF": "",
                "POTA": "",
                "BOTA": "",
                "QRZAPI": "",
                "QRZUpload": ""
            },
            "Logbook": []
        }
        with open(current_json_file, 'w') as file:
            json.dump(data, file, indent=4)  # Save initial structure with indentation
        update_title(root, VERSION_NUMBER, current_json_file, radio_status_var.get())

        load_station_setup()
        file_menu.entryconfig("Station setup", state="normal")

# Helper function to convert old logbook format (list) to new format (dictionary)
def convert_old_logbook(old_logbook):
    # Create a template for the new format with Station info
    new_format = {
        "Station": {
            "Callsign": "N0CALL",
            "Operator": "N0CALL",
            "Locator": "AA11BB",  # Placeholder, adjust as needed
            "Location": "",
            "WWFF": "",
            "POTA": "",
            "BOTA": "",
            "QRZAPI": "",
            "QRZUpload": ""            
        },
        "Logbook": []
    }

    # Convert each entry to the new format
    for entry in old_logbook:
        new_entry = {
            "Date": entry.get("Date", ""),
            "Time": entry.get("Time", ""),
            "Callsign": entry.get("Callsign", ""),
            "Name": entry.get("Name", ""),
            "My_Callsign": entry.get("Station_Callsign", ""),
            "My_Operator": "",
            "My_Locator": "",
            "My_Location": "",
            "My_WWFF": "",
            "MY_POTA": "",
            "MY_BOTA": "",
            "Country": entry.get("Country", ""),
            "Continent": entry.get("Continent", ""),
            "Sent": entry.get("Sent", ""),
            "Received": entry.get("Received", ""),
            "Mode": entry.get("Mode", ""),
            "Submode": "",
            "Band": entry.get("Band", ""),
            "Frequency": entry.get("Frequency", ""),
            "Locator": entry.get("Locator", ""),
            "Comment": entry.get("Comment", ""),
            "WWFF": entry.get("WWFF", ""),
            "POTA": entry.get("POTA", ""),
            "BOTA": entry.get("BOTA", ""),
            "Satellite": ""
        }
        new_format["Logbook"].append(new_entry)

    return new_format


def load_last_logbook_on_startup():
    # Check if reload is enabled in config
    reload_enabled = config.getboolean('General', 'reload_last_logbook', fallback=False)
    if not reload_enabled:
        return  # User chose not to reload last logbook on startup

    # Proceed if there's a file to load
    last_file = config.get('General', 'last_loaded_logbook', fallback=None)
    if last_file and os.path.exists(last_file):
        load_json(last_file)








# Function to load an existing JSON file
def load_json(file_to_load=None):
    global current_json_file, Logbook_Window, qso_lines

    # If a file is already loaded and no new one was passed in, confirm with user
    if current_json_file and not file_to_load:
        confirm = messagebox.askyesno("Confirm", "A file is already loaded. Do you want to load a new file?")
        if not confirm:
            reset_fields()
            return

        reset_fields()
        clear_station_labels()
        current_json_file = ""
        qso_lines = []
        workedb4_tree.delete(*workedb4_tree.get_children())
        update_title(root, VERSION_NUMBER, current_json_file, radio_status_var.get())

        if Logbook_Window:
            Logbook_Window.destroy()
            Logbook_Window = None

    # Use file passed in or ask the user to select one
    if file_to_load:
        selected_file = file_to_load
    else:
        selected_file = filedialog.askopenfilename(filetypes=[("MiniBook files", "*.mbk")])

    if not selected_file:
        return  # User cancelled

    # Check if backup folder is configured and exists BEFORE assigning current_json_file
    backup_dir = config.get("General", "backup_folder", fallback="").strip()
    if not backup_dir or not os.path.exists(backup_dir):
        if messagebox.askokcancel(
            "Backup Folder Not Set",
            "No valid backup folder is configured.\nWould you like to open Preferences now to set one?"
        ):
            root.after(100, open_preferences)
        return  # Stop loading process entirely

    # Everything is OK — now commit to using this file
    current_json_file = selected_file


    if current_json_file:
  
        # Create a backup in user-defined folder
        try:
            from datetime import datetime

            os.makedirs(backup_dir, exist_ok=True)

            # Create timestamped backup filename
            base_name = os.path.basename(current_json_file)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{timestamp}_{base_name}"
            backup_path = os.path.join(backup_dir, backup_filename)

            # Write the backup
            with open(current_json_file, 'r', encoding='utf-8') as original, open(backup_path, 'w', encoding='utf-8') as backup:
                backup.write(original.read())

            # Limit to 5 backups per unique logbook file
            MAX_BACKUPS = 5
            all_backups = [
                f for f in os.listdir(backup_dir)
                if f.endswith(base_name) and f.count("_") >= 1
            ]

            # Sort backups by timestamp (descending)
            matching_backups = sorted(all_backups, reverse=True)

            for old_file in matching_backups[MAX_BACKUPS:]:
                try:
                    os.remove(os.path.join(backup_dir, old_file))
                except Exception as e:
                    print(f"Could not remove old backup: {e}")

        except Exception as e:
            print(f"Backup failed: {e}")



############ DEBUG PART
        try:
            with open(current_json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print("----------")
                print("DEBUG: JSON file loaded successfully")

                # Handle legacy format (flat list)
                if isinstance(data, list):
                    print("DEBUG: Detected legacy format (list)")

                    convert_confirm = messagebox.askyesno("Convert Old Format", "Old Logbook format detected! Do you want to convert it to the new format?")
                    if convert_confirm:
                        print("DEBUG: User confirmed conversion")

                        data = convert_old_logbook(data)
                        new_file_path = filedialog.asksaveasfilename(defaultextension=".mbk", filetypes=[("MiniBook files", "*.mbk")])
                        if new_file_path:
                            print(f"DEBUG: Saving converted file to {new_file_path}")
                            with open(new_file_path, 'w', encoding='utf-8') as new_file:
                                json.dump(data, new_file, indent=4)
                            messagebox.showinfo("Conversion Successful", "The logbook has been converted and saved.")
                            current_json_file = new_file_path
                            update_title(root, VERSION_NUMBER, current_json_file, radio_status_var.get())
                            reset_fields()
                            load_station_setup()
                            file_menu.entryconfig("Station setup", state="normal")
                        else:
                            print("DEBUG: User cancelled saving converted file")
                            messagebox.showinfo("Save Cancelled", "The converted file was not saved.")
                            current_json_file = ""
                            no_file_loaded()
                    else:
                        print("DEBUG: User declined conversion")
                        current_json_file = ""
                        no_file_loaded()
                    return

                # Handle modern format with Station and Logbook keys
                elif isinstance(data, dict):
                    print("DEBUG: Detected modern format (dict)")
                    if "Station" in data and "Logbook" in data and isinstance(data["Logbook"], list):
                        print("DEBUG: Valid Station and Logbook keys found")
                        station_info = data["Station"]
                        if "Callsign" in station_info and "Locator" in station_info:
                            print("DEBUG: Station info contains Callsign and Locator")
                            update_title(root, VERSION_NUMBER, current_json_file, radio_status_var.get())
                            reset_fields()
                            load_station_setup()
                            file_menu.entryconfig("Station setup", state="normal")
                        else:
                            print("ERROR: Missing Callsign or Locator in Station info")
                            messagebox.showerror("Invalid Format", "Missing required fields in 'Station' section.")
                            current_json_file = ""
                            no_file_loaded()
                    else:
                        print("ERROR: Invalid structure in modern format")
                        messagebox.showerror("Invalid Format", "The file does not contain a valid logbook structure.")
                        current_json_file = ""
                        no_file_loaded()

                # Save the path to config
                if current_json_file:
                    print(f"DEBUG: Saving last loaded path: {current_json_file}")
                    config.set('General', 'last_loaded_logbook', current_json_file)
                    file_path = CONFIG_FILE
                    with open(file_path, 'w') as configfile:
                        config.write(configfile)

                    load_json_content()

        except Exception as e:
            print("ERROR: Exception during logbook loading:")
            traceback.print_exc()
            messagebox.showerror("Error", f"Could not read the file:\n{str(e)}")
            current_json_file = ""
            no_file_loaded()








def load_json_content():
    global tree, qso_count_label, qso_lines

    # Lees JSON bestand altijd in
    try:
        with open(current_json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            qso_lines = data.get("Logbook", [])
    except Exception as e:
        print(f"Error reading MiniBook file: {e}")
        qso_lines = []
        return

    # Stop hier als tree niet bestaat of al vernietigd is
    if tree is None or not tree.winfo_exists():
        return

    try:
        tree.delete(*tree.get_children())
    except Exception as e:
        print(f"Error accessing tree widget: {e}")
        return

    if not qso_lines:
        if qso_count_label and qso_count_label.winfo_exists():
            qso_count_label.config(text="Total of 0 QSO's in logbook")
        print("No QSO entries found in the MiniBook file.")
        return

    try:
        for qso in qso_lines:
            qso['DateTime'] = datetime.strptime(
                f"{qso['Date']} {qso.get('Time', '')}", '%Y-%m-%d %H:%M:%S'
            ) if qso.get('Time') else datetime.strptime(qso['Date'], '%Y-%m-%d')

        qso_lines.sort(key=lambda x: x['DateTime'], reverse=True)

        row_color = True
        qso_counter = 0

        for qso in qso_lines:
            qso_counter += 1
            tag = 'oddrow' if row_color else 'evenrow'
            row_color = not row_color

            tree.insert("", "end", values=(
                qso.get('Date', ''),
                qso.get('Time', ''),
                qso.get('Callsign', ''),
                qso.get('Name', ''),
                qso.get('Country', ''),
                qso.get('Sent', ''),
                qso.get('Received', ''),
                qso.get('Mode', ''),
                qso.get('Submode', ''),
                qso.get('Band', ''),
                qso.get('Frequency', ''),
                qso.get('Locator', ''),
                qso.get('Comment', ''),
                qso.get('WWFF', ''),
                qso.get('POTA', ''),
                qso.get('BOTA', ''),
                qso.get('My Callsign', ''),
                qso.get('My Operator', ''),
                qso.get('My Locator', ''),
                qso.get('My Location', ''),
                qso.get('My WWFF', ''),
                qso.get('My POTA', ''),
                qso.get('My BOTA', ''),
                qso.get('Satellite', '')
            ), tags=(tag,))

        if qso_count_label and qso_count_label.winfo_exists():
            qso_count_label.config(text=f"Total of {qso_counter} QSO's in logbook")

        tree.tag_configure("oddrow", background="#f0f0f0")
        tree.tag_configure("evenrow", background="white")

    except ValueError as e:
        print(f"Error processing date and time: {e}")






#########################################################################################
#  _    ___   ___ ___  ___   ___  _  __ __      _____ _  _ ___   _____      __
# | |  / _ \ / __| _ )/ _ \ / _ \| |/ / \ \    / /_ _| \| |   \ / _ \ \    / /
# | |_| (_) | (_ | _ \ (_) | (_) | ' <   \ \/\/ / | || .` | |) | (_) \ \/\/ / 
# |____\___/ \___|___/\___/ \___/|_|\_\   \_/\_/ |___|_|\_|___/ \___/ \_/\_/  
#                                                                             
#########################################################################################

# Global variables for Logbook Viewer
qso_lines = []  # This will hold QSO entries
sort_column = None  # Column currently being sorted
sort_reverse = False  # Flag for sort order

# Function to open and display the logbook in a new window
def view_logbook():
    global tree, qso_count_label, search_entry, qso_lines, column_checkboxes, Logbook_Window

    if not current_json_file:
        messagebox.showwarning("Warning", "Please first load logbook!")
        return
    
       # Check if the logbook window is already open
    if Logbook_Window is not None and Logbook_Window.winfo_exists():
        Logbook_Window.lift()  # Bring the existing window to the front
        return

    # Create a new window to display the logbook
    Logbook_Window = tk.Toplevel(root)
    Logbook_Window.title(f"MiniBook Logbook - " + os.path.basename(current_json_file))

    def close_logbook():
        global tree, Logbook_Window
        tree = None  # Reset tree to ensure it is treated as uninitialized
        save_window_geometry(Logbook_Window, "LogbookWindow")    
        Logbook_Window.destroy()
        Logbook_Window = None

    # Load saved geometry
    load_window_geometry(Logbook_Window, "LogbookWindow")

    info_frame = tk.Frame(Logbook_Window)
    info_frame.pack(fill="x", padx=10, pady=2)

    # Label to show the number of QSO's logged
    qso_count_label = tk.Label(info_frame, text="Total QSO's: 0", font=('Arial', 14))
    qso_count_label.grid(pady=2)

    separator = ttk.Separator(Logbook_Window, orient='horizontal')
    separator.pack(fill='x', pady=2)

    # Adding Menu to logbook window
    menu_bar = tk.Menu(Logbook_Window)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Import ADIF", command=import_adif)
    file_menu.add_command(label="Export to ADIF", command=export_to_adif)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=close_logbook)
    menu_bar.add_cascade(label="File", menu=file_menu)
    Logbook_Window.config(menu=menu_bar)    


    # ---------------- Frame for search entry and button ----------------
    search_frame = tk.Frame(Logbook_Window)
    search_frame.pack(pady=2)

     # Label for search entry
    search_label = tk.Label(search_frame, text="Search in log:", font=('Arial', 10))
    search_label.pack(pady=5, side='left')

    # Entry for search input
    search_entry = tk.Entry(search_frame, font=('Arial', 10))
    search_entry.pack(side='left', padx=(0, 5))

    # ----------------------- Frame for checkboxes ------------------------
    checkbox_frame = tk.Frame(Logbook_Window)
    checkbox_frame.pack(pady=2)

    # Label for search entry
    checkbox_label = tk.Label(checkbox_frame, text="Select search filter:", font=('Arial', 10))
    checkbox_label.pack(side='left')

    # Define columns for the logbook
    columns = ('Date', 'Time', 'Callsign', 'Name', 'Country', 'Sent', 'Received', 'Mode', 'Submode','Band', 'Frequency', 'Locator', 'Comment', 'WWFF', 'POTA', 'BOTA', 'My Callsign', 'My Operator', 'My Locator', 'My Location', 'My WWFF', 'My POTA', 'My BOTA')

    # Add checkboxes for each column
    column_checkboxes = {}
    for col in columns:
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(checkbox_frame, text=col, variable=var)
        checkbox.pack(side='left', padx=5)
        column_checkboxes[col] = var

    # Set Callsign checkbox to checked by default
    column_checkboxes['Callsign'].set(True)

    # Scrollbars for the Treeview
    tree_frame = tk.Frame(Logbook_Window)
    tree_frame.pack(fill='both', expand=True)

    # Scrollbars
    x_scrollbar = tk.Scrollbar(tree_frame, orient='horizontal')
    x_scrollbar.pack(side='bottom', fill='x')

    y_scrollbar = tk.Scrollbar(tree_frame, orient='vertical')
    y_scrollbar.pack(side='right', fill='y')

    # Create a style and configure the Treeview heading font
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    # Create the Treeview
    tree = ttk.Treeview(
        tree_frame, 
        columns=columns, 
        show='headings', 
        selectmode='extended',  # <-- allows for multi-select
        xscrollcommand=x_scrollbar.set, 
        yscrollcommand=y_scrollbar.set
    )
    tree.pack(fill='both', expand=True)


    # Right-click context menu for editing QSO
    def show_context_menu(event):
        item = tree.identify_row(event.y)
        if item:
            # Add to selection if not already selected
            if item not in tree.selection():
                tree.selection_add(item)

            selected_items = tree.selection()

            # Only show "Edit QSO" if exactly 1 line is selected
            if len(selected_items) == 1:
                context_menu.entryconfig("Edit QSO", state="normal")
            else:
                context_menu.entryconfig("Edit QSO", state="disabled")

            # Only show "Bulk Edit" when 2 or more lines are selected
            if len(selected_items) >= 2:
                context_menu.entryconfig("Bulk Edit", state="normal")
            else:
                context_menu.entryconfig("Bulk Edit", state="disabled")

            context_menu.post(event.x_root, event.y_root)




    def edit_qso_from_menu():
        # Open the QSO edit window (you can call your edit QSO function here)
        edit_qso(edit_qso)  # Call the edit function with the selected QSO






#    _  _ ___    _                 _     _  _  _ 
#   / \|_) _/   |_)| ||  |/    | ||_)|  / \|_|| \
#   \_X| \/__   |_)|_||__|\    |_||  |__\_/| ||_/

    def upload_qsos_to_qrz():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Select one or more QSOs to upload to QRZ.")
            return

        confirm = messagebox.askyesno("Upload to QRZ", f"Upload {len(selected_items)} selected QSO(s) to QRZ?")
        if not confirm:
            return

        # Create a new window for the progress bar
        progress_win = tk.Toplevel(Logbook_Window)
        progress_win.title("Uploading to QRZ")

        # Get the position and size of Logbook_Window
        logbook_x = Logbook_Window.winfo_rootx()
        logbook_y = Logbook_Window.winfo_rooty()
        logbook_width = Logbook_Window.winfo_width()
        logbook_height = Logbook_Window.winfo_height()

        # Calculate the center position of Logbook_Window
        center_x = logbook_x + logbook_width // 2
        center_y = logbook_y + logbook_height // 2

        # Set the position of progress_win relative to Logbook_Window
        progress_win.geometry(f"+{center_x - 100}+{center_y - 50}")  # Adjust position as needed


        progress_label = tk.Label(progress_win, text="Uploading QSOs...")
        progress_label.pack(pady=5)

        progress_bar = ttk.Progressbar(progress_win, length=250, mode='determinate', maximum=len(selected_items))
        progress_bar.pack(pady=5)

        # Counter
        progress_counter = tk.Label(progress_win, text=f"0 / {len(selected_items)} QSOs geüpload")
        progress_counter.pack(pady=5)

        progress_win.update()

        # Initialize result counts
        result_counts = {
            "✅ Uploaded successfully": 0,
            "⚠️ Duplicate QSO": 0,
            "❌ Wrong station_callsign": 0,  # <--- toegevoegd
            "❌ Other errors": 0,
            "🔍 Not found in memory (skipped)": 0
        }

        results = []

        def upload_thread():
            nonlocal result_counts, results

            for idx, item in enumerate(selected_items, start=1):
                values = tree.item(item)['values']
                matched_qso = next((qso for qso in qso_lines if 
                                    qso.get("Date") == values[0] and 
                                    qso.get("Time") == values[1] and 
                                    qso.get("Callsign") == values[2]), None)
                                    
                if matched_qso:
                    response = upload_to_qrz(matched_qso, True)
                    if response and hasattr(response, "text"):
                        text = response.text.strip()
                        if "RESULT=OK" in text:
                            result_counts["✅ Uploaded successfully"] += 1
                            matched_qso['status'] = "✅ Uploaded"
                        elif "RESULT=FAIL" in text:
                            reason = ""
                            if "REASON=" in text:
                                reason = text.split("REASON=")[-1].split("&")[0].strip().lower()

                            if "duplicate" in reason:
                                result_counts["⚠️ Duplicate QSO"] += 1
                                matched_qso['status'] = "⚠️ Duplicate"
                            elif "wrong station_callsign" in reason:
                                result_counts["❌ Wrong station_callsign"] += 1
                                matched_qso['status'] = "❌ Wrong station_callsign"
                            else:
                                result_counts["❌ Other errors"] += 1
                                matched_qso['status'] = f"❌ Other error: {reason}"
                        elif "RESULT=AUTH" in text:
                            result_counts["❌ Other errors"] += 1
                            matched_qso['status'] = "❌ Invalid API key"
                        else:
                            result_counts["❌ Other errors"] += 1
                            matched_qso['status'] = "❌ Unknown response"
                    else:
                        result_counts["❌ Other errors"] += 1
                        matched_qso['status'] = "❌ Invalid response"

                    results.append(matched_qso)
                else:
                    result_counts["🔍 Not found in memory (skipped)"] += 1




                # Update progress bar
                progress_bar['value'] = idx
                progress_counter.config(text=f"{idx} / {len(selected_items)} QSOs uploaded")
                progress_win.update()

            # After upload process is done, close the progress window and show the summary
            progress_win.destroy()

            # Show the summary message
            summary_lines = [f"{k}: {v}" for k, v in result_counts.items() if v > 0]
            summary = "\n".join(summary_lines)
            messagebox.showinfo("QRZ Upload Result", summary)

            # Log the result with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_upload_result(f"=== QRZ Upload at {timestamp} ===\n" + summary)
            for q in results:
                call = q.get('Callsign', 'Unknown')
                date = q.get('Date', 'Unknown')
                time = q.get('Time', 'Unknown')
                status = q.get('status', 'Unknown')
                log_upload_result(f"Callsign {call} @ {date} {time}: {status}")

        # Start the upload process in a separate thread
        upload_thread_instance = threading.Thread(target=upload_thread)
        upload_thread_instance.start()





#    _  __    _____ __    _  __ _  /  __
#   | \|_ |  |_  | |_    / \(_ / \   (_ 
#   |_/|__|__|__ | |__   \_X__)\_/   __)

    # Function to delete QSO from the menu
    def delete_qso_from_menu():
        global qso_lines

        selected_items = tree.selection()
        if selected_items:
            confirm = messagebox.askyesno("Delete QSO(s)", f"Are you sure you want to delete {len(selected_items)} selected QSO(s)?")
            if confirm:
                # Collect identifiers of QSOs to be deleted
                identifiers_to_delete = []
                for item in selected_items:
                    values = tree.item(item)['values']
                    identifiers_to_delete.append((
                        str(values[0]).strip(),
                        str(values[1]).strip(),
                        str(values[2]).strip().upper()
                    ))

                # Filter qso_lines at once
                qso_lines = [
                    qso for qso in qso_lines
                    if (
                        str(qso.get("Date", "")).strip(),
                        str(qso.get("Time", "")).strip(),
                        str(qso.get("Callsign", "")).strip().upper()
                    ) not in identifiers_to_delete
                ]

                # Remove selected items only after processing qso_lines
                tree.detach(*selected_items)  # prevent visual updates during delete
                for item in selected_items:
                    tree.delete(item)

                save_to_json()
                load_json_content()  # Reload everything (and update GUI in one go)
                update_worked_before_tree()

                # Show simple message that deletion is complete
                messagebox.showinfo(
                    "Delete Complete",
                    f"{len(identifiers_to_delete)} QSO(s) deleted successfully."
                )                


    # Create a context menu
    context_menu = tk.Menu(Logbook_Window, tearoff=0)
    context_menu.add_command(label="Edit QSO", command=edit_qso_from_menu)
    context_menu.add_command(label="Bulk Edit", command=open_bulk_edit_window)
    context_menu.add_command(label="Delete QSO('s)", command=delete_qso_from_menu)
    context_menu.add_command(label="Upload to QRZ", command=upload_qsos_to_qrz)
    context_menu.add_command(label="Export to ADIF (selected)", command=export_selected_to_adif)


    # Bind the right-click event to show the context menu
    tree.bind("<Button-2>" if platform.system() == "Darwin" else "<Button-3>", show_context_menu)

    # Bind double-left click event to show edit window
    tree.bind("<Double-1>", edit_qso)


    if tree is None:
        print("Treeview is not initialized immediately after creation.")

    x_scrollbar.config(command=tree.xview)
    y_scrollbar.config(command=tree.yview)

    # Define custom minimum for each column
    custom_column_widths = {
        'Date': 80,
        'Time': 60,
        'Callsign': 80,
        'Name': 60,
        'Country': 130,
        'Sent': 50,
        'Received': 50,
        'Mode': 60,
        'Submode': 60,
        'Band': 50,
        'Frequency': 80,
        'Locator': 60,
        'Comment': 150,
        'WWFF': 50,
        'POTA': 50,
        'BOTA': 50,
        'My Callsign': 80,
        'My Operator': 80,
        'My Locator': 70,
        'My Location': 120,
        'My WWFF': 50,
        'My POTA': 50,
        'My BOTA': 50,
        'Satellite': 80

    }

    # Apply custom widths to the Treeview columns
    for col in columns:
        tree.column(col, anchor='center', width=custom_column_widths.get(col, 100), minwidth=custom_column_widths.get(col, 100), stretch=True)
        tree.heading(col, text=col, anchor='center', command=lambda c=col: sort_treeview(c))

    # Function to handle column header clicks for sorting
    def sort_treeview(column):
        global sort_column, sort_reverse
        if sort_column == column:
            sort_reverse = not sort_reverse  # Toggle the sort order
        else:
            sort_column = column
            sort_reverse = False  # Default to ascending sort

        # Sort the treeview
        sorted_items = sorted(tree.get_children(), key=lambda x: tree.item(x, 'values')[columns.index(column)], reverse=sort_reverse)
        
        # Reinsert items in the sorted order and apply alternating row colors
        for index, item in enumerate(sorted_items):
            tree.move(item, '', index)  # Move items in the sorted order
            # Apply alternating colors
            tree.item(item, tags=('oddrow' if index % 2 == 0 else 'evenrow',))

        # Update the treeview to show new alternating colors
        tree.tag_configure('oddrow', background='#f0f0f0')
        tree.tag_configure('evenrow', background='white')

    # Initial load of the JSON content
    load_json_content()  








#       _  __    __ __ _  _  __   
#   |  / \/__   (_ |_ |_||_)/  |_|
#   |__\_/\_|   __)|__| || \\__| |

                    
    # Function to search the log
    def search_log():
        search_term = search_entry.get().lower()  # Get the search term and convert to lower case
        matching_entries = []  # List to hold matching entries

        # Clear the tree first
        tree.delete(*tree.get_children())

        # Go through all QSO entries to find matches
        for qso in qso_lines:
            matches = False
            for col, var in column_checkboxes.items():
                if var.get() and qso[col] and search_term in str(qso[col]).lower():
                    matches = True
                    break

            if matches:
                matching_entries.append(qso)

        # If matches found, display them
        if matching_entries:
            row_color = True
            for qso in matching_entries:
                # Insert the data into the Treeview
                tree.insert("", "end", values=(
                    qso.get('Date', ''),
                    qso.get('Time', ''),
                    qso.get('Callsign', ''),
                    qso.get('Name', ''),
                    qso.get('Country', ''),
                    qso.get('Sent', ''),
                    qso.get('Received', ''),
                    qso.get('Mode', ''),
                    qso.get('Submode', ''),
                    qso.get('Band', ''),
                    qso.get('Frequency', ''),
                    qso.get('Locator', ''),
                    qso.get('Comment', ''),
                    qso.get('WWFF', ''),
                    qso.get('POTA', ''),
                    qso.get('BOTA', ''),
                    qso.get('My Callsign', ''),
                    qso.get('My Operator', ''),
                    qso.get('My Locator', ''),
                    qso.get('My Location', ''),
                    qso.get('My WWFF', ''),
                    qso.get('My POTA', ''),
                    qso.get('My BOTA', ''),
                    qso.get('Satellite', '')
                ), tags=('oddrow' if row_color else 'evenrow',))
                row_color = not row_color

            qso_count_label.config(text=f"Total QSO's: {len(matching_entries)}")  # Update the count label

    Logbook_Window.protocol("WM_DELETE_WINDOW", lambda: close_logbook())

    # Search button
    search_button = tk.Button(search_frame, text="Search", command=search_log)
    search_button.pack(pady=5, side='left')

    find_duplicates_btn = tk.Button(search_frame,  text="Find Duplicates", command=find_duplicates)
    find_duplicates_btn.pack(side='left', padx=10)

    def close_logbook():
        global tree, Logbook_Window
        tree = None  # Reset tree to ensure it is treated as uninitialized
        save_window_geometry(Logbook_Window, "LogbookWindow")    
        Logbook_Window.destroy()
        Logbook_Window = None

    # Function to reset the log to show all entries
    def reset_view():
        load_json_content()  # Load all entries again
        search_entry.delete(0, tk.END)  # Clear the search entry

    # Reset button
    reset_button = tk.Button(search_frame, text="Reset View", command=reset_view)
    reset_button.pack(pady=5, padx=30, side='left')

    # Add a button to close the logbook window
    tk.Button(search_frame, text="Close Window", command=close_logbook).pack(pady=5, padx=30, side="right")    


    # Function to update the logbook when new QSO is logged
    def update_logbook():
        load_json_content()

    # Save a reference to the update function so we can call it later when logging a new QSO
    Logbook_Window.update_logbook = update_logbook


    
    # Set the Logbook_Window to None when it is closed
    Logbook_Window.protocol("WM_DELETE_WINDOW", close_logbook)




#    _____    _     _     _    ___ __ _ ___ __ __
#   |_  | |\|| \   | \| ||_)|   | /  |_| | |_ (_ 
#   |  _|_| ||_/   |_/|_||  |___|_\__| | | |____)

def find_duplicates():
    if not qso_lines:
        messagebox.showinfo("Duplicates", "No logbook loaded or empty.")
        return

    seen = {}
    duplicate_index_map = {}

    for idx, qso in enumerate(qso_lines):
        key = (
            qso.get("Callsign", "").strip().upper(),
            qso.get("Date", "").strip(),
            qso.get("Time", "").strip()
        )
        if key in seen:
            if key not in duplicate_index_map:
                duplicate_index_map[key] = [seen[key]]
            duplicate_index_map[key].append(idx)
        else:
            seen[key] = idx

    all_duplicate_indices = []
    for indices in duplicate_index_map.values():
        all_duplicate_indices.extend(indices)

    if not all_duplicate_indices:
        messagebox.showinfo("Duplicates", "No duplicate QSOs found.")
        return

    dup_window = tk.Toplevel(Logbook_Window)
    dup_window.title("Duplicate QSOs Found")

    tree_dup = ttk.Treeview(dup_window, columns=("Index", "Callsign", "Date", "Time", "Mode", "Frequency"), show="headings", selectmode="extended")
    tree_dup.heading("Index", text="Index")
    tree_dup.heading("Callsign", text="Callsign")
    tree_dup.heading("Date", text="Date")
    tree_dup.heading("Time", text="Time")
    tree_dup.heading("Mode", text="Mode")
    tree_dup.heading("Frequency", text="Frequency")

    for col in ("Index", "Callsign", "Date", "Time", "Mode", "Frequency"):
        tree_dup.column(col, anchor="center")
        tree_dup.heading(col, text=col, anchor="center")

    tree_dup.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tree_to_log_index = {}
    color_styles = ["lightblue", "white", "lightgreen", "lightyellow", "lightpink", "lavender", "lightgray"]

    for i, color in enumerate(color_styles):
        tag_name = f"tag_{i}"
        tree_dup.tag_configure(tag_name, background=color)
        

    for group_index, (key, indices) in enumerate(duplicate_index_map.items()):
        tag_name = f"tag_{group_index % len(color_styles)}"
        for idx in indices:
            qso = qso_lines[idx]
            iid = f"dup_{idx}"
            tree_dup.insert(
                "", "end", iid=iid,
                values=(idx, qso.get("Callsign"), qso.get("Date"), qso.get("Time"), qso.get("Mode"), qso.get("Frequency")),
                tags=(tag_name,)
            )
            tree_to_log_index[iid] = idx

    def delete_selected_duplicates():
        selected_iids = tree_dup.selection()
        if not selected_iids:
            messagebox.showwarning("No Selection", "Select records to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(selected_iids)} selected duplicates?"):
            return
        indices_to_delete = sorted([tree_to_log_index[iid] for iid in selected_iids], reverse=True)
        for i in indices_to_delete:
            try:
                del qso_lines[i]
            except IndexError:
                continue
        save_to_json()
        load_json_content()
        dup_window.destroy()
        messagebox.showinfo("Done", f"{len(indices_to_delete)} duplicates removed and saved.")



    tk.Button(dup_window, text="Delete Selected", command=delete_selected_duplicates).pack(pady=5)
    tk.Button(dup_window, text="Close", command=dup_window.destroy).pack(pady=5)





#########################################################################################
#  ___ _   _ _    _  __  ___ ___ ___ _____  __      _____ _  _ ___   _____      __
# | _ ) | | | |  | |/ / | __|   \_ _|_   _| \ \    / /_ _| \| |   \ / _ \ \    / /
# | _ \ |_| | |__| ' <  | _|| |) | |  | |    \ \/\/ / | || .` | |) | (_) \ \/\/ / 
# |___/\___/|____|_|\_\ |___|___/___| |_|     \_/\_/ |___|_|\_|___/ \___/ \_/\_/  
#                                                                                 
#########################################################################################

def open_bulk_edit_window():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showinfo("No Selection", "Select one or more QSO records first.")
        return

    edit_window = tk.Toplevel(Logbook_Window)
    edit_window.title("Bulk Edit")

    Logbook_Window.update_idletasks()
    logbook_x = Logbook_Window.winfo_rootx()
    logbook_y = Logbook_Window.winfo_rooty()
    logbook_w = Logbook_Window.winfo_width()
    logbook_h = Logbook_Window.winfo_height()

    if platform.system() == "Darwin":
        win_w = 400
        win_h = 200
    else:
        win_w = 250
        win_h = 180

    pos_x = logbook_x + (logbook_w // 2) - (win_w // 2)
    pos_y = logbook_y + (logbook_h // 2) - (win_h // 2)

    edit_window.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

    edit_window.resizable(False, False)
    edit_window.transient(Logbook_Window)
    edit_window.grab_set()

    tk.Label(edit_window, text="Field to edit:").pack(pady=5)
    field_var = tk.StringVar()
    field_combo = ttk.Combobox(edit_window, textvariable=field_var, state="readonly", font=('Arial', 10), width=20)
    field_combo['values'] = list(tree["columns"])
    field_combo.pack(pady=5)

    tk.Label(edit_window, text="New value:").pack(pady=5)
    value_entry = tk.Entry(edit_window, font=('Arial', 10), width=20)
    value_entry.pack(pady=5)

    uppercase_fields = [
        "Callsign", "Locator", "My Callsign", "My Operator", "My Locator",
        "My WWFF", "My POTA", "My BOTA", "Continent", "Mode", "Submode", "WWFF", "POTA", "BOTA"
    ]

    def apply_bulk_edit():
        field = field_var.get()
        new_value = value_entry.get().strip()

        if not field:
            messagebox.showwarning("Missing Field", "Please select a field.")
            return

        if field.lower() == "locator" and not is_valid_locator(new_value):
            messagebox.showerror("Invalid Locator", "Locator must be valid and at least 4 characters.\nExample: FN31 or JN58TD.")
            return
        if field.lower() == "date":
            try:
                datetime.strptime(new_value, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Date", "Date must be in format YYYY-MM-DD.")
                return
        if field.lower() == "time":
            try:
                datetime.strptime(new_value, "%H:%M")
            except ValueError:
                messagebox.showerror("Invalid Time", "Time must be in format HH:MM.")
                return

        if field in uppercase_fields:
            new_value = new_value.upper()

        confirm = messagebox.askyesno("Confirm Bulk Edit", f"Apply value '{new_value}' to field '{field}' for {len(selected_items)} QSO(s)?")
        if not confirm:
            return

        updated_count = 0
        for item in selected_items:
            values = list(tree.item(item, "values"))
            col_index = tree["columns"].index(field)
            values[col_index] = new_value
            tree.item(item, values=values)

            for qso in qso_lines:
                if (
                    str(qso.get("Date", "")).strip(),
                    str(qso.get("Time", "")).strip(),
                    str(qso.get("Callsign", "")).strip().upper()
                ) == (
                    str(values[0]).strip(),
                    str(values[1]).strip(),
                    str(values[2]).strip().upper()
                ):
                    qso[field] = new_value
                    updated_count += 1
                    break

        save_to_json()
        load_json_content()
        update_worked_before_tree()
        edit_window.destroy()
        messagebox.showinfo("Success", f"{updated_count} QSO(s) updated.")

    btn_frame = tk.Frame(edit_window)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Save", command=apply_bulk_edit, width=10).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Cancel", command=edit_window.destroy, width=10).pack(side="right", padx=10)








def export_selected_to_adif():
    if not tree:
        messagebox.showerror("Error", "Treeview not available.")
        return

    selected_items = tree.selection()
    if not selected_items:
        messagebox.showinfo("Export to ADIF", "No QSOs selected.")
        return

    adif_lines = []
    for item in selected_items:
        values = tree.item(item)['values']
        qso = next((q for q in qso_lines if 
                    q.get("Date") == values[0] and 
                    q.get("Time") == values[1] and 
                    q.get("Callsign") == values[2]), None)
        if not qso:
            continue

        adif_line_list = []
        def add_field(tag, value):
            if value:
                val = str(value).strip()
                adif_line_list.append(f"<{tag}:{len(val)}>{val}")

        add_field("qso_date", qso.get("Date", "").replace("-", ""))
        add_field("time_on", qso.get("Time", "").replace(":", ""))
        add_field("call", qso.get("Callsign", ""))
        add_field("name", qso.get("Name", ""))
        add_field("rst_sent", qso.get("Sent", ""))
        add_field("rst_rcvd", qso.get("Received", ""))
        add_field("mode", qso.get("Mode", ""))
        add_field("submode", qso.get("Submode", ""))
        add_field("band", qso.get("Band", ""))
        add_field("freq", qso.get("Frequency", ""))
        add_field("gridsquare", qso.get("Locator", ""))
        add_field("comment", qso.get("Comment", ""))
        add_field("station_callsign", qso.get("My Callsign", ""))
        add_field("operator", qso.get("My Operator", ""))
        add_field("country", qso.get("Country", ""))
        add_field("cont", qso.get("Continent", ""))
        add_field("sat_name", qso.get("Satellite", ""))

        if qso.get("WWFF"):
            add_field("sig", "WWFF")
            add_field("sig_info", qso.get("WWFF", ""))
        if qso.get("POTA"):
            add_field("sig", "POTA")
            add_field("sig_info", qso.get("POTA", ""))
        if qso.get("BOTA"):
            add_field("sig", "BOTA")
            add_field("sig_info", qso.get("BOTA", ""))            

        adif_lines.append(" ".join(adif_line_list) + " <EOR>\n")

    if not adif_lines:
        messagebox.showinfo("Export to ADIF", "No valid QSOs found for export.")
        return

    export_file = filedialog.asksaveasfilename(defaultextension=".adi", filetypes=[("ADIF files", "*.adi")])
    if export_file:
        try:
            with open(export_file, "w", encoding="utf-8") as f:
                f.write("Generated by MiniBook\n")
                f.write("<ADIF_VER:5>3.1.0 <PROGRAMID:8>MiniBook <EOH>\n")
                f.writelines(adif_lines)
            messagebox.showinfo("Export to ADIF", f"{len(adif_lines)} QSOs exported successfully.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save ADIF file:\n{e}")



# Function to save the QSO lines back to the JSON file
def save_to_json():
    # Load existing data
    try:
        with open(current_json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            station_info = data.get("Station", {})  # Preserve Station information
    except Exception as e:
        print(f"Error loading MiniBook file: {e}")
        return

    # Convert datetime objects back to string format before saving
    for qso in qso_lines:
        if 'DateTime' in qso:
            qso['Date'] = qso['DateTime'].strftime('%Y-%m-%d')
            qso['Time'] = qso['DateTime'].strftime('%H:%M:%S')
            del qso['DateTime']  # Remove the DateTime key before saving

    # Update the JSON structure and save
    data = {
        "Station": station_info,  # Keep the Station information intact
        "Logbook": qso_lines      # Save the updated QSO entries
    }

    try:
        with open(current_json_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.flush()
    except Exception as e:
        print(f"Error saving to MiniBook file: {e}")





#########################################################################################
#  ___ ___ ___ _____    ___  ___  ___  
# | __|   \_ _|_   _|  / _ \/ __|/ _ \ 
# | _|| |) | |  | |   | (_) \__ \ (_) |
# |___|___/___| |_|    \__\_\___/\___/ 
#
#########################################################################################

def edit_qso(event):
    global Edit_Window

    if Edit_Window is not None and Edit_Window.winfo_exists():
        Edit_Window.lift()
        return

    selected_item = tree.selection()
    if not selected_item:
        return

    selected_item_values = tree.item(selected_item, 'values')
    unique_identifier = f"{selected_item_values[2]}_{selected_item_values[0]}_{selected_item_values[1]}"

    Edit_Window = tk.Toplevel(root)
    Edit_Window.title("Edit QSO Entry")
    Edit_Window.resizable(False, False)

    # Positionering
    Logbook_Window.update_idletasks()
    logbook_x = Logbook_Window.winfo_x()
    logbook_y = Logbook_Window.winfo_y()
    logbook_width = Logbook_Window.winfo_width()
    logbook_height = Logbook_Window.winfo_height()
    edit_width = 550
    edit_height = 600 if platform.system() == "Darwin" else 550
    edit_x = logbook_x + (logbook_width - edit_width) // 2
    edit_y = logbook_y + (logbook_height - edit_height) // 2
    Edit_Window.geometry(f"{edit_width}x{edit_height}+{edit_x}+{edit_y}")
    Edit_Window.grab_set()

    fields = ['Date', 'Time', 'Callsign', 'Name', 'Country', 'Sent', 'Received', 'Mode', 'Submode', 'Band', 'Frequency', 'Locator', 'Comment', 'WWFF', 'POTA', 'BOTA', 'My Callsign', 'My Operator', 'My Locator', 'My Location', 'My WWFF', 'My POTA', 'My BOTA', 'Satellite']
    entries = {}

    original_qso = next((qso for qso in qso_lines if f"{qso['Callsign']}_{qso['Date']}_{qso['Time']}" == unique_identifier), None)
    if original_qso is None:
        print("QSO entry not found!")
        return

    form_frame = tk.Frame(Edit_Window)
    form_frame.pack(padx=10, pady=10)

    columns = 2
    rows = (len(fields) + 1) // columns

    for index, field in enumerate(fields):
        col = index // rows
        row = index % rows

        tk.Label(form_frame, text=field).grid(row=row, column=col * 2, padx=5, pady=5, sticky='w')

        if field == 'Date':
            entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
            entry.set_date(original_qso['Date'])

        elif field == 'Band':
            entry = ttk.Combobox(form_frame, values=list(band_to_frequency.keys()), state="readonly", font=('Arial', 10), width=14)
            entry.set(original_qso.get('Band', ''))

        elif field == 'Mode':
            entry = ttk.Combobox(form_frame, values=mode_options, state="readonly", font=('Arial', 10), width=14)
            entry.set(original_qso.get('Mode', ''))

        elif field == 'Submode':
            entry = ttk.Combobox(form_frame, values=submode_options, state="readonly", font=('Arial', 10), width=14)
            entry.set(original_qso.get('Submode', ''))

        elif field in ['Sent', 'Received']:
            entry = ttk.Combobox(form_frame, values=rst_options, font=('Arial', 10), width=14)
            entry.set(original_qso.get(field, ''))

        else:
            if field in ['WWFF', 'My WWFF', 'POTA', 'My POTA']:
                var = tk.StringVar()
                var.set(original_qso.get(field, ''))
                var.trace_add("write", lambda *args, v=var: v.set(v.get().upper()))
                entry = tk.Entry(form_frame, textvariable=var)
            else:
                entry = tk.Entry(form_frame)
                entry.insert(0, original_qso.get(field, ''))

        entry.grid(row=row, column=col * 2 + 1, padx=5, pady=5, sticky='w')
        entries[field] = entry

    # ─────────────── Buttons onderaan ───────────────
    button_frame = tk.Frame(Edit_Window)
    button_frame.pack(pady=10)

    def close_edit_window():
        global Edit_Window
        Edit_Window.grab_release()
        Edit_Window.destroy()
        Edit_Window = None

    def save_changes():
        original_qso['Callsign'] = entries['Callsign'].get().strip().upper()
        original_qso['Locator'] = entries['Locator'].get().strip().upper()
        original_qso['My Locator'] = entries['My Locator'].get().strip().upper()
        original_qso['My Callsign'] = entries['My Callsign'].get().strip().upper()
        original_qso['My Operator'] = entries['My Operator'].get().strip().upper()
        original_qso['Mode'] = entries['Mode'].get().strip().upper()
        original_qso['Submode'] = entries['Submode'].get().strip().upper()
        original_qso['Band'] = entries['Band'].get().strip().lower()

        locator1 = original_qso['Locator']
        locator2 = original_qso['My Locator']

        if not is_valid_locator(locator1) or not is_valid_locator(locator2):
            messagebox.showerror("Invalid Locator", "The Maidenhead locator must be at least 4 characters and valid.\nExample: FN31 or FN31TK")
            return

        # Validatie datum en tijd
        date_str = entries['Date'].get().strip()
        time_str = entries['Time'].get().strip()
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Date", "Date must be in format YYYY-MM-DD.")
            return
        try:
            datetime.strptime(time_str, '%H:%M:%S')
        except ValueError:
            messagebox.showerror("Invalid Time", "Time must be in format HH:MM.")
            return

        for field in fields:
            if field not in original_qso:
                original_qso[field] = ""
            if field not in ['Date', 'Time', 'Callsign', 'Locator', 'My Locator', 'My Callsign', 'My Operator', 'Mode', 'Submode', 'Band']:
                original_qso[field] = entries[field].get().strip()

        save_to_json()
        load_json_content()
        update_worked_before_tree()
        close_edit_window()

    # Buttons
    tk.Button(button_frame, text="Cancel", width=10, command=close_edit_window).pack(side="left", padx=10)
    tk.Button(button_frame, text="Save", width=10, command=save_changes).pack(side="right", padx=10)



def custom_duplicate_dialog(parent, total_count, duplicate_count, added_count):
    # Create a Toplevel window for the custom dialog
    dialog = tk.Toplevel(parent)
    dialog.title("Duplicate QSOs Found")
    dialog.resizable(False, False)

    # Position the dialog relative to the parent (Logbook_Window) window
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    dialog.geometry(f"+{parent_x + 50}+{parent_y + 50}")

    # Variable to store the action selected by the user
    dialog_result = tk.StringVar(value=None)  # Default to None if the dialog is closed directly

    # Instructions label showing the number of QSO entries and duplicates
    label = tk.Label(dialog, text=f"{total_count} QSO(s) found, {duplicate_count} duplicate(s) found.\n"
                                  f"{added_count} new QSO(s) added after ignoring duplicates.\n\n"
                                  "What would you like to do?", font=('Arial', 10))
    label.pack(pady=10)

    # Callback to close dialog with selected action
    def on_action(action):
        dialog_result.set(action)  # Set the result to the selected action
        dialog.destroy()

    # Buttons for different actions
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)

    # Overwrite button
    overwrite_button = tk.Button(button_frame, text="Overwrite", width=15, command=lambda: on_action("Overwrite"))
    overwrite_button.grid(row=0, column=0, padx=10)

    # Ignore button
    ignore_button = tk.Button(button_frame, text="Ignore", width=15, command=lambda: on_action("Ignore"))
    ignore_button.grid(row=0, column=1, padx=10)

    # Add button
    add_button = tk.Button(button_frame, text="Add", width=15, command=lambda: on_action("Add"))
    add_button.grid(row=1, columnspan=2, pady=5)

    # Set the dialog to close without action if the window is closed directly
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

    dialog.wait_window()  # Wait for the dialog to be closed before proceeding
    return dialog_result.get()  # Return the action selected, or None if closed




#########################################################################################
#    _   ___ ___ ___   ___ __  __ ___  ___  ___ _____ 
#   /_\ |   \_ _| __| |_ _|  \/  | _ \/ _ \| _ \_   _|
#  / _ \| |) | || _|   | || |\/| |  _/ (_) |   / | |  
# /_/ \_\___/___|_|   |___|_|  |_|_|  \___/|_|_\ |_|  
#                                                     
#########################################################################################

def import_adif():
    global current_json_file
    if not current_json_file:
        messagebox.showerror("Error", "No logbook file loaded. Please load a logbook before importing.")
        return

    adif_file = filedialog.askopenfilename(title="Select ADIF File", filetypes=[("ADIF files", "*.adi"), ("All files", "*.*")])
    if not adif_file:
        return

    # Create progress window
    progress_window = tk.Toplevel(root)
    progress_window.title("Importing ADIF")
    progress_window.geometry("400x100")
    progress_label = tk.Label(progress_window, text="Importing QSOs...")
    progress_label.pack(pady=5)
    progress_counter = tk.Label(progress_window, text="")
    progress_counter.pack()
    progress = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=5)

    def do_import():
        try:
            with open(current_json_file, "r", encoding="utf-8") as json_file:
                logbook_data = json.load(json_file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load logbook: {e}")
            progress_window.destroy()
            return

        try:
            try:
                with open(adif_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(adif_file, "r", encoding="latin-1") as f:
                    content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ADIF file: {e}")
            progress_window.destroy()
            return

        qso_records = re.split(r'<eor>', content, flags=re.IGNORECASE)
        total_qso_count = len(qso_records)
        progress["maximum"] = total_qso_count

        new_entries = []
        duplicates = []

        for i, record in enumerate(qso_records, 1):
            if not record.strip():
                continue

            sig = extract_field(record, "sig").upper()
            sig_info = extract_field(record, "sig_info")
            wwff = sig_info if sig == "WWFF" else ""
            pota = sig_info if sig == "POTA" else ""
            bota = sig_info if sig == "BOTA" else ""

            entry = {
                "Date": import_format_date(extract_field(record, "qso_date")) or "",
                "Time": import_format_time(extract_field(record, "time_on")) or "",
                "Callsign": (extract_field(record, "call") or "").upper(),
                "Name": (extract_field(record, "name") or ""),
                "My Callsign": (extract_field(record, "station_callsign") or "").upper(),
                "My Operator": (extract_field(record, "operator") or "").upper(),
                "My Locator": ("").upper(),
                "My Location": ("").upper(),
                "My WWFF": ("").upper(),
                "My POTA": ("").upper(),
                "My BOTA": ("").upper(),
                "Country": extract_field(record, "country") or "",
                "Continent": (extract_field(record, "cont") or "").upper(),
                "Sent": extract_field(record, "rst_sent") or "",
                "Received": extract_field(record, "rst_rcvd") or "",
                "Mode": extract_field(record, "mode") or "",
                "Submode": extract_field(record, "submode") or "",
                "Band": (extract_field(record, "band") or "").lower(),
                "Frequency": extract_field(record, "freq") or "",
                "Locator": (extract_field(record, "gridsquare") or "").upper(),
                "Comment": extract_field(record, "comment") or "",
                "WWFF": wwff,
                "POTA": pota,
                "BOTA": bota,
                "Satellite": extract_field(record, "sat_name") or ""
            }

            if extract_field(record, "my_sig") == "POTA":
                entry["My POTA"] = extract_field(record, "my_sig_info") or ""
                
            if extract_field(record, "my_sig") == "BOTA":
                entry["My BOTA"] = extract_field(record, "my_sig_info") or ""                

            callsign = entry["Callsign"]
            check_callsign_prefix(callsign, False)
            if country_var:
                entry["Country"] = country_var
            if continent_var:
                entry["Continent"] = continent_var

            if entry["Callsign"]:
                is_duplicate = any(
                    existing_entry["Callsign"] == entry["Callsign"] and
                    existing_entry["Date"] == entry["Date"] and
                    existing_entry["Time"] == entry["Time"]
                    for existing_entry in logbook_data["Logbook"]
                )
                if is_duplicate:
                    duplicates.append(entry)
                else:
                    new_entries.append(entry)

            # Update progress bar
            progress["value"] = i
            progress_counter.config(text=f"{i} / {total_qso_count} QSOs")
            progress_window.update_idletasks()

        progress_window.destroy()

        added_count = len(new_entries)
        action = None
        if duplicates:
            duplicate_count = len(duplicates)
            action = custom_duplicate_dialog(parent=root, total_count=total_qso_count,
                                             duplicate_count=duplicate_count, added_count=added_count)
            if action is None:
                return
            elif action == "Overwrite":
                for duplicate_entry in duplicates:
                    for idx, existing_entry in enumerate(logbook_data["Logbook"]):
                        if (existing_entry["Callsign"] == duplicate_entry["Callsign"] and
                            existing_entry["Date"] == duplicate_entry["Date"] and
                            existing_entry["Time"] == duplicate_entry["Time"]):
                            logbook_data["Logbook"][idx] = duplicate_entry
                            break
            elif action == "Add":
                new_entries.extend(duplicates)
                added_count = len(new_entries)

        logbook_data["Logbook"].extend(new_entries)

        try:
            with open(current_json_file, "w", encoding="utf-8") as json_file:
                json.dump(logbook_data, json_file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save logbook: {e}")
            return

        for window in root.winfo_children():
            if isinstance(window, tk.Toplevel) and hasattr(window, 'update_logbook'):
                window.update_logbook()

        message = f"{added_count} new QSO(s) added to the logbook."
        if duplicates and action:
            message = f"{len(duplicates)} duplicate QSO(s) processed. {added_count} new QSO(s) added."
        messagebox.showinfo("Import ADIF", message)

    # Start the import in a background thread
    threading.Thread(target=do_import).start()



def extract_field(record, field_name):
    """
    Extract a field's value from the ADIF record in the format <FIELD_NAME:length>value.
    """
    # Search for the field in a case-insensitive manner with an optional length attribute
    pattern = rf"<{field_name}:(\d+)>([^<]*)"
    match = re.search(pattern, record, re.IGNORECASE)
    if match:
        return match.group(2).strip()  # Extract the value and remove any surrounding whitespace
    return ""  # Return an empty string if the field is not found

def import_format_date(date_str):
    # Convert date from ADIF format (yyyymmdd) to yyyy-mm-dd
    if date_str and len(date_str) == 8:
        return datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
    return None

def import_format_time(time_str):
    # Convert time from ADIF format (HHMMSS) to HH:MM:SS
    if time_str and len(time_str) >= 4:
        try:
            return datetime.strptime(time_str[:6], "%H%M%S").strftime("%H:%M:%S")
        except ValueError:
            pass  # Ignore formatting if time is invalid
    return None


#########################################################################################
#    _   ___ ___ ___   _____  _____  ___  ___ _____ 
#   /_\ |   \_ _| __| | __\ \/ / _ \/ _ \| _ \_   _|
#  / _ \| |) | || _|  | _| >  <|  _/ (_) |   / | |  
# /_/ \_\___/___|_|   |___/_/\_\_|  \___/|_|_\ |_|  
#                                                   
#########################################################################################

# Function to escape invalid characters
def escape_invalid_characters(text):
    # Remove or replace problematic characters (non-ASCII)
    # Here we replace Unicode characters outside the typical ASCII range with a placeholder or remove them.
    # For example, replace \ub250 (and others like it) with an empty string or another character.
    
    # Replace specific unwanted Unicode characters (e.g., \ub250) with a placeholder like "?"
    text = re.sub(r'[\u0080-\uFFFF]', '?', text)  # Replace non-ASCII characters with '?'
    
    return text

# Function to ask the user to select the log type (POTA, WWFF, General)
def get_log_type():
    # Create a new window for log type selection
    log_type_window = tk.Toplevel(Logbook_Window)
    log_type_window.title("Select Log Type")
    
    # Variable to store the selected log type
    selected_log_type = tk.StringVar(value="")

    def set_log_type(log_type):
        selected_log_type.set(log_type)
        log_type_window.destroy()  # Close the log type selection window
    
    # Add the label text asking "How would you like to export?"
    label = tk.Label(log_type_window, text="How would you like to export?")
    label.pack(pady=10)

    # Create buttons for each log type
    tk.Button(log_type_window, text="POTA", command=lambda: set_log_type("POTA")).pack(pady=5)
    tk.Button(log_type_window, text="BOTA", command=lambda: set_log_type("BOTA")).pack(pady=5)
    tk.Button(log_type_window, text="WWFF", command=lambda: set_log_type("WWFF")).pack(pady=5)
    tk.Button(log_type_window, text="Normal", command=lambda: set_log_type("Normal")).pack(pady=5)

    # Position the window in the center of the parent window with top alignment
    parent_x = Logbook_Window.winfo_rootx()  # Get the x position of the parent window
    parent_y = Logbook_Window.winfo_rooty()  # Get the y position of the parent window
    parent_width = Logbook_Window.winfo_width()  # Width of the parent window
    parent_height = Logbook_Window.winfo_height()  # Height of the parent window

    # Calculate the position for the new window
    window_width = 200
    window_height = 150
    new_x = parent_x + (parent_width // 2) - (window_width // 2)
    new_y = parent_y  # Align to the top of the parent window

    # Set the geometry of the log type window
    log_type_window.geometry(f"{window_width}x{window_height}+{new_x}+{new_y}")
    
    # Wait until the user closes the log_type_window and make sure the value is updated
    log_type_window.grab_set()  # Prevent interaction with other windows while the dialog is open
    log_type_window.wait_window()  # Pause execution until the window is closed
    
    return selected_log_type.get()  # Return the selected log type


# Function to export JSON log file to ADIF format
def export_to_adif():
    global current_json_file, qso_lines

    if not current_json_file or not qso_lines:
        messagebox.showwarning("Warning", "No logbook file loaded or no QSO entries to export!")
        return

    # Ask the user for the log type (POTA, WWFF, Normal)
    log_type = get_log_type()
    if not log_type:
        return  # User canceled the selection

    # Ask the user for the output ADIF file location
    adif_file = filedialog.asksaveasfilename(defaultextension=".adi", filetypes=[("ADIF files", "*.adi")])
    if not adif_file:
        return  # User canceled the save dialog    

    try:
        # Write the ADIF file
        with open(adif_file, 'w', encoding='utf-8') as file:
            for qso in qso_lines:
                # Prepare the ADIF record from the JSON data
                adif_record = []
                operator = escape_invalid_characters(qso.get('My Operator', ''))
                mycallsign = escape_invalid_characters(qso.get('My Callsign', ''))
                callsign = escape_invalid_characters(qso.get('Callsign', ''))
                name = escape_invalid_characters(qso.get('Name', ''))
                date = export_format_date(qso.get('Date', ''))
                time = export_format_time(qso.get('Time', ''))
                mode = escape_invalid_characters(qso.get('Mode', ''))
                submode = escape_invalid_characters(qso.get('Submode', ''))
                band = escape_invalid_characters(qso.get('Band', ''))
                frequency = escape_invalid_characters(qso.get('Frequency', ''))
                sent = escape_invalid_characters(qso.get('Sent', ''))
                received = escape_invalid_characters(qso.get('Received', ''))
                comment = escape_invalid_characters(qso.get('Comment', ''))
                wwff = escape_invalid_characters(qso.get('WWFF', ''))
                pota = escape_invalid_characters(qso.get('POTA', ''))
                bota = escape_invalid_characters(qso.get('BOTA', ''))
                my_pota = escape_invalid_characters(qso.get('My POTA', ''))
                my_bota = escape_invalid_characters(qso.get('My BOTA', ''))
                locator = escape_invalid_characters(qso.get('Locator', ''))
                satellite = escape_invalid_characters(qso.get('Satellite', ''))


                # Append the formatted fields to the record
                adif_record.append(f"<band:{len(band)}>{band}")
                adif_record.append(f"<call:{len(callsign)}>{callsign}")
                adif_record.append(f"<comment:{len(comment)}>{comment}")
                adif_record.append(f"<freq:{len(frequency)}>{frequency}")
                adif_record.append(f"<mode:{len(mode)}>{mode}")
                adif_record.append(f"<submode:{len(submode)}>{submode}")
                adif_record.append(f"<rst_rcvd:{len(received)}>{received}")
                adif_record.append(f"<rst_sent:{len(sent)}>{sent}")
                adif_record.append(f"<time_off:{len(time)}>{time}")
                adif_record.append(f"<time_on:{len(time)}>{time}")
                adif_record.append(f"<qso_date:{len(date)}>{date}")
                adif_record.append(f"<operator:{len(operator)}>{operator}")
                adif_record.append(f"<station_callsign:{len(mycallsign)}>{mycallsign}")
                adif_record.append(f"<gridsquare:{len(locator)}>{locator}")
                adif_record.append(f"<sat_name:{len(satellite)}>{satellite}")
                adif_record.append(f"<name:{len(name)}>{name}")

                # Determine the log type: WWFF, POTA, or Normal
                if log_type == "WWFF" and wwff:
                    activation = "WWFF"
                    adif_record.append(f"<sig:{len(activation)}>{activation}")
                    adif_record.append(f"<sig_info:{len(wwff)}>{wwff}")                    
                elif log_type == "POTA" and pota:
                    activation = "POTA"
                    adif_record.append(f"<sig:{len(activation)}>{activation}")
                    adif_record.append(f"<sig_info:{len(pota)}>{pota}")
                    adif_record.append(f"<my_sig:{len(activation)}>{activation}")
                    adif_record.append(f"<my_sig_info:{len(my_pota)}>{my_pota}") 
                elif log_type == "BOTA" and bota:
                    activation = "BOTA"
                    adif_record.append(f"<sig:{len(activation)}>{activation}")
                    adif_record.append(f"<sig_info:{len(bota)}>{bota}")
                    adif_record.append(f"<my_sig:{len(activation)}>{activation}")
                    adif_record.append(f"<my_sig_info:{len(my_bota)}>{my_bota}") 
                # Join the ADIF record and append EOR
                file.write(" ".join(adif_record) + " <EOR>\n")

        messagebox.showinfo("Success", "Exported to ADIF format successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export to ADIF: {e}")


# Function to open the export folder
def open_export_folder(folder_path):
    try:
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{folder_path}"')
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", folder_path])
        else:  # Linux
            subprocess.Popen(["xdg-open", folder_path])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open folder: {e}")


# Function to convert date and time to ADIF format
def export_format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Adjust format as necessary
        return date_obj.strftime('%Y%m%d')  # Convert to 'YYYYMMDD'
    except ValueError:
        return ''  # Return empty string if parsing fails

def export_format_time(time_str):
    try:
        time_obj = datetime.strptime(time_str, '%H:%M:%S')  # Adjust format as necessary
        return time_obj.strftime('%H%M%S')  # Convert to 'HHMMSS'
    except ValueError:
        return ''  # Return empty string if parsing fails






#########################################################################################
#   ___  ___  ___    _    ___   ___  ___ ___ _  _  ___ 
#  / _ \/ __|/ _ \  | |  / _ \ / __|/ __|_ _| \| |/ __|
# | (_) \__ \ (_) | | |_| (_) | (_ | (_ || || .` | (_ |
#  \__\_\___/\___/  |____\___/ \___|\___|___|_|\_|\___|
#                                                      
#########################################################################################


# Function to log QSO
def log_qso():
    global qso_lines

    if not current_json_file:
        messagebox.showwarning("Warning", "No logbook file loaded!")
        return

    # Strict format checks for date and time
    date_str = date_var.get()
    time_str = time_var.get()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
        messagebox.showerror("Date Format Error", "Date must be in YYYY-MM-DD format (e.g., 2025-04-22)")
        return

    if not re.fullmatch(r"\d{2}:\d{2}:\d{2}", time_str):
        messagebox.showerror("Time Format Error", "Time must be in HH:MM:SS format (e.g., 17:17:00)")
        return

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Invalid Date", "Date is not valid (e.g., 2025-02-30 is not a real date).")
        return

    try:
        datetime.strptime(time_str, "%H:%M:%S")
    except ValueError:
        messagebox.showerror("Invalid Time", "Time is not valid (e.g., 25:00:00 is not a real time).")
        return

    # Get values from form
    callsign = callsign_var.get().strip()
    if not callsign:
        messagebox.showwarning("Warning", "Log may not be empty!")
        reset_fields()
        return

    # Build QSO entry
    qso_entry = {
        "Date": date_str,
        "Time": time_str,
        "Callsign": callsign,
        "Name": name_var.get().strip(),
        "My Callsign": my_callsign_var.get().upper(),
        "My Operator": my_operator_var.get().upper(),
        "My Locator": my_locator_var.get().upper(),
        "My Location": my_location_var.get(),
        "My WWFF": my_wwff_var.get(),
        "My POTA": my_pota_var.get(),
        "My BOTA": my_bota_var.get(),
        "Country": country_var,
        "Continent": continent_var,
        "Sent": rst_sent_var.get(),
        "Received": rst_received_var.get(),
        "Mode": mode_var.get(),
        "Submode": submode_var.get(),
        "Band": band_var.get(),
        "Frequency": "",
        "Locator": locator_var.get().strip(),
        "Comment": comment_var.get().strip(),
        "WWFF": wwff_var.get().strip(),
        "POTA": pota_var.get().strip(),
        "BOTA": bota_var.get().strip(),
        "Satellite": satellite_var.get().strip()
    }

    # Validate frequency
    freq_input = frequency_var.get()
    if freq_input:
        try:
            qso_entry["Frequency"] = f"{float(freq_input):.6f}"
        except ValueError:
            messagebox.showerror("Invalid input", "Enter a valid decimal number for the frequency.")
            return

    # Validate locator
    if not is_valid_locator(qso_entry["Locator"]):
        messagebox.showerror("Invalid Locator", "The Maidenhead locator must be at least 4 characters and valid.\nExample: FN31 or FN31TK")
        return

    # Append to cache
    qso_lines.append(qso_entry)

    # Save cache to file
    save_to_json()

    # UI updates
    reset_fields()
    last_qso_label.config(
        text=f"Last QSO with {callsign} at {time_str} on {qso_entry['Frequency']}MHz in {qso_entry['Mode']}"
    )

    # Refresh logbook viewer if open
    for window in root.winfo_children():
        if isinstance(window, tk.Toplevel) and hasattr(window, 'update_logbook'):
            window.update_logbook()

    # Optional: QRZ upload
    if upload_qrz_var.get():
        threading.Thread(target=upload_to_qrz, args=(qso_entry, False), daemon=True).start()




#########################################################################################
#   ___  ___  ____  _   _ ___ _    ___   _   ___  
#  / _ \| _ \|_  / | | | | _ \ |  / _ \ /_\ |   \ 
# | (_) |   / / /  | |_| |  _/ |_| (_) / _ \| |) |
#  \__\_\_|_\/___|  \___/|_| |____\___/_/ \_\___/ 
#
#########################################################################################

# Function to build QRZ ADIF Compatible string
def build_adif(qso):
    # Use .get() for every key to avoid KeyError and provide default values if any are missing
    callsign = qso.get('Callsign', '')
    date = qso.get('Date', '')
    time = qso.get('Time', '')
    band = qso.get('Band', '')
    mode = qso.get('Mode', '')
    sent = qso.get('Sent', '')
    received = qso.get('Received', '')
    my_callsign = qso.get('My Callsign', '')
    operator = qso.get('My Operator', '')
    locator = qso.get('Locator', '')
    name = qso.get('Name', '')
    comment = qso.get('Comment', '')
    frequency = qso.get('Frequency', '')

    # Construct the ADIF formatted QSO entry string with required fields
    adif = (
        f"<CALL:{len(callsign)}>{callsign}"
        f"<QSO_DATE:8>{date.replace('-', '')}"  # Date formatted as YYYYMMDD
        f"<TIME_ON:6>{time.replace(':', '')}"   # Time formatted as HHMMSS
        f"<BAND:{len(band)}>{band}"
        f"<MODE:{len(mode)}>{mode}"
        f"<RST_SENT:{len(sent)}>{sent}"
        f"<RST_RCVD:{len(received)}>{received}"
        f"<STATION_CALLSIGN:{len(my_callsign)}>{my_callsign}"
        f"<OPERATOR:{len(operator)}>{operator}"
        f"<GRIDSQUARE:{len(locator)}>{locator}"
        f"<NAME:{len(name)}>{name}"
        f"<COMMENT:{len(comment)}>{comment}"
        f"<FREQ:{len(frequency)}>{frequency}"
    )

    # Append the <EOR> tag at the end of the ADIF string to indicate the end of the QSO record
    adif += "<EOR>"

    return adif

## Function to upload QSO to QRZ
def upload_to_qrz(qso, showstatus):
    global QRZ_status_label
    # Prepare POST data
    post_data = {
        "KEY": my_qrzapi_var.get(),
        "ACTION": "INSERT",
        "ADIF": build_adif(qso),
    }

    try:
        response = requests.post("https://logbook.qrz.com/api", data=post_data)
        if response.status_code == 200:
            if "RESULT=OK" in response.text:
                callsign = qso.get('CALL', '') or qso.get('Callsign', '')
                msg = f"✅ QSO {callsign} successfully uploaded to QRZ."

                color = "green"
            elif "RESULT=FAIL" in response.text:
                reason = response.text.split("REASON=")[-1].split("&")[0]
                if "duplicate" in reason.lower():
                    msg = f"⚠️ {reason}"
                    color = "orange"
                elif "wrong station_callsign" in reason.lower():
                    msg = f"❌ Wrong station_callsign!"#: {reason}"
                    color = "red"
                else:
                    msg = f"❌ QRZ upload failed"#: {reason}"
                    color = "red"
            elif "RESULT=AUTH" in response.text:
                msg = "❌ Invalid QRZ API key."
                color = "red"
            else:
                msg = "⚠️ QRZ returned an unknown response."
                color = "orange"
        else:
            msg = f"❌ HTTP error while uploading to QRZ: {response.status_code}"
            color = "red"
    except Exception as e:
        if DEBUG:
            print(f"QRZ upload exception: {e}")  # Technical debug output
        msg = "❌ QRZ upload failed: no internet connection or DNS error."
        color = "red"

    if DEBUG:
        print(msg)

    if not showstatus:
        QRZ_status_label.config(
            text=msg,
            fg=color,
            cursor="hand2" if "successfully uploaded" in msg else "",
            font=('Arial', 8, 'underline') if "successfully uploaded" in msg else ('Arial', 8)
        )
        QRZ_status_label.unbind("<Button-1>")
        if "successfully uploaded" in msg:
            QRZ_status_label.bind("<Button-1>", lambda e, cs=callsign: open_qrz_link(e, cs))


    return response



#########################################################################################
# __      _____    _ _____  __  __  _    ___   ___  ___ ___ _  _  ___ 
# \ \    / / __|_ | |_   _|_\ \/ / | |  / _ \ / __|/ __|_ _| \| |/ __|
#  \ \/\/ /\__ \ || | | ||___>  <  | |_| (_) | (_ | (_ || || .` | (_ |
#   \_/\_/ |___/\__/  |_|   /_/\_\ |____\___/ \___|\___|___|_|\_|\___|
#
#########################################################################################                                                                     

listener_thread = None
listening = False
sock = None

def load_port_from_config(config):
    """Load the port setting from the configuration."""
    return int(config.get('Wsjtx_settings', 'wsjtx_port', fallback="2338"))

def start_listener(config):
    """
    Start WSJT-X ADIF listener.
    """
    global listening, listener_thread, sock
    if listening:
        print("Listener already running.")
        return

    listening = True
    port = load_port_from_config(config)
    listener_thread = threading.Thread(target=wsjtx_adif_listener, args=(config, port))
    listener_thread.daemon = True
    listener_thread.start()
    print(f"Listener started on port {port}.")

def stop_listener():
    """
    Stop WSJT-X ADIF listener.
    """
    global listening, sock
    if not listening:
        print("Listener not running.")
        return

    listening = False
    if sock:
        sock.close()
        sock = None
    print("Listener stopped.")

def restart_listener(config):
    """
    Restart the WSJT-X listener upon a port change.
    """
    print("Restart listener...")
    stop_listener()
    time.sleep(1)  # Small pause to make sure everything closes properly
    start_listener(config)

def wsjtx_adif_listener(config, port):
    """
    Listen to and digest WSJT-X ADIF broadcasts.
    """
    global listening, sock, current_json_file

    host = "127.0.0.1"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host, port))
        print(f"Listen to WSJT-X ADIF broadcasts on {host}:{port}...")

        while listening:
            try:
                data, addr = sock.recvfrom(4096)
                if not data:
                    continue

                # Decode the ADIF message
                try:
                    adif_record = data.decode("utf-8").strip()
                except UnicodeDecodeError:
                    adif_record = data.decode("latin-1").strip()

                if not adif_record:
                    continue

                # Check if it is a valid ADIF message
                if not is_valid_adif(adif_record):
                    print("Invalid ADIF datagram. Message is ignored.")
                    continue

                # Check if a log is open
                if not current_json_file:
                    messagebox.showerror(
                        "Error",
                        "WSJT-X log data received, but no log loaded!\n"
                        "Load a log and try again."
                    )
                    continue

                # Process the QSO data
                process_qso(adif_record)

            except socket.error as e:
                if not listening:
                    break
                print(f"Socket-error: {e}")
    except Exception as e:
        print(f"Error starting the listener: {e}")
    finally:
        if sock:
            sock.close()
        print("Listener terminated.")






# Function that processes an received WSJTX ADIF record
def process_qso(adif_record):
    """
    Process a valid ADIF record and add it to the log.
    """
    global current_json_file

    callsign = (extract_field(adif_record, "call") or "").upper()
    name = (extract_field(adif_record, "name") or "")
    time_field = (
        import_format_time(extract_field(adif_record, "time_off")) or
        import_format_time(extract_field(adif_record, "time_on")) or
        ""
    )

    sig = (extract_field(adif_record, "sig") or "").upper()
    sig_info = extract_field(adif_record, "sig_info") or ""

    qso_entry = {
        "Date": import_format_date(extract_field(adif_record, "qso_date")) or "",
        "Time": time_field,
        "Callsign": callsign,
        "Name": name,
        "My Callsign": (extract_field(adif_record, "station_callsign") or "").upper(),
        "My Operator": (extract_field(adif_record, "operator") or "").upper(),
        "My Locator": (extract_field(adif_record, "my_gridsquare") or "").upper(),
        "My Location": "",
        "My WWFF": "",
        "My POTA": "",
        "My BOTA": "",
        "Country": (extract_field(adif_record, "country") or "").title(),
        "Continent": (extract_field(adif_record, "cont") or "").upper(),
        "Sent": (extract_field(adif_record, "rst_sent") or "").upper(),
        "Received": (extract_field(adif_record, "rst_rcvd") or "").upper(),
        "Mode": (extract_field(adif_record, "mode") or "").upper(),
        "Submode": (extract_field(adif_record, "submode") or "").upper(),
        "Band": (extract_field(adif_record, "band") or "").lower(),
        "Frequency": extract_field(adif_record, "freq") or "",
        "Locator": (extract_field(adif_record, "gridsquare") or "").upper(),
        "Comment": extract_field(adif_record, "comment") or "",
        "WWFF_POTA": sig,
        "WWFF": sig_info if "WWFF" in sig else "",
        "POTA": sig_info if "POTA" in sig else "",
        "BOTA": sig_info if "BOTA" in sig else "",
        "Satellite": extract_field(adif_record, "sat_name") or ""
    }

    # Debug: Show the processed QSO input
    if DEBUG:
        print(f"QSO-input processed {qso_entry}")

    # Update the country field based on the callsign
    check_callsign_prefix(callsign, update_ui=False)  # Disable UI update to prevent excessive updates
    qso_entry["Country"] = country_var  # Set the updated country
    
    # Upload to QRZ after logging the QSO
    if upload_qrz_var.get():
        upload_to_qrz(qso_entry,False)    
    
    # Add the QSO entry to the logbook
    add_qso_to_logbook(qso_entry)


           

# Function to add a Processed WSJTX ADIF record to the current loaded logbook
def add_qso_to_logbook(qso_entry):
    """
    Add a QSO entry directly to the loaded logbook and update the logbook window if open.
    """
    global qso_lines

    try:
        # Voeg toe aan cache
        qso_lines.append(qso_entry)

        # Schrijf cache naar disk
        save_to_json()

        # Update "Worked Before" tree
        update_worked_before_tree()

        # Update de laatste QSO label
        last_qso_label.config(
            text=f"Last QSO with {qso_entry['Callsign']} at {qso_entry['Time']} "
                 f"on {float(qso_entry['Frequency']):.3f}MHz in {qso_entry['Mode']}"
        )

        # Update logbook venster indien open (via main thread)
        for window in root.winfo_children():
            if isinstance(window, tk.Toplevel) and hasattr(window, 'update_logbook'):
                root.after(0, window.update_logbook)

        # Toon succesbericht
        show_auto_close_messagebox(
            "MiniBook",
            f"Succes!\n\nQSO with {qso_entry['Callsign']} at {qso_entry['Time']}\nsuccessfully added!",
            duration=3000
        )

    except Exception as e:
        show_auto_close_messagebox(
            "MiniBook",
            f"Error!\n\nFailed to log QSO: {e}",
            duration=3000
        )




def show_auto_close_messagebox(title, message, duration=2000):
    def _show():
        temp_root = tk.Toplevel(root)
        temp_root.title(title)
        temp_root.geometry("300x150")
        temp_root.resizable(False, False)
        temp_root.attributes("-topmost", True)
        temp_root.overrideredirect(True)

        root.update_idletasks()
        root_x = root.winfo_rootx()
        root_y = root.winfo_rooty()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        x = root_x + (root_width - 300) // 2
        y = root_y + (root_height - 150) // 2
        temp_root.geometry(f"300x150+{x}+{y}")

        border = tk.Frame(temp_root, bg='black', bd=2)
        border.pack(expand=True, fill='both')

        inner = tk.Frame(border, bg='white')
        inner.pack(expand=True, fill='both', padx=1, pady=1)

        label = tk.Label(inner, text=message, wraplength=280, justify="center", bg='white', font=('Arial', 10))
        label.pack(expand=True, pady=20)

        temp_root.after(duration, temp_root.destroy)

    root.after(0, _show)





def is_valid_adif(adif_record):
    """
    Validate if the ADIF record is a valid datagram.
    Checks for the presence of key tags and general structure.
    """
    # Required tags for a minimal valid ADIF record
    required_tags = ["<call:", "<qso_date:", "<band:", "<mode:"]

    # Check for the presence of required tags
    for tag in required_tags:
        if not re.search(re.escape(tag), adif_record, re.IGNORECASE):
            return False

    # Ensure either <time_on> or <time_off> is present
    if not (re.search(r"<time_on:", adif_record, re.IGNORECASE) or re.search(r"<time_off:", adif_record, re.IGNORECASE)):
        return False

    # Check for <EOR> or <eor> to mark the end of the record
    if not re.search(r"<eor>", adif_record, re.IGNORECASE):
        return False

    return True


def extract_adif_field(record, field_name):
    """
    Extract a field's value from the ADIF record in the format <FIELD_NAME:length>value.
    """
    # Search for the field in a case-insensitive manner with an optional length attribute
    pattern = rf"<{field_name}:(\d+)>([^<]*)"
    match = re.search(pattern, record, re.IGNORECASE)
    if match:
        return match.group(2).strip()  # Extract the value and remove any surrounding whitespace
    return ""  # Return an empty string if the field is not found






#########################################################################################
#  ___ ___ ___    ___ ___  _  _ _____ ___  ___  _    
# | _ \_ _/ __|  / __/ _ \| \| |_   _| _ \/ _ \| |   
# |   /| | (_ | | (_| (_) | .` | | | |   / (_) | |__ 
# |_|_\___\___|  \___\___/|_|\_| |_| |_|_\\___/|____|
#
#########################################################################################

# Hamlib

if sys.platform.startswith('win'):
    import winreg

def connect_to_hamlib_threaded():
    """Start hamlib in a separate thread."""
    thread = threading.Thread(target=connect_to_hamlib, daemon=True)
    thread.start()

# Function to connect to hamlib external server
def connect_to_hamlib():
    global hamlib_process, socket_connection, hamlib_PORT, stop_frequency_thread
    
    stop_frequency_thread.clear()

    hamlib_PORT = config.get('hamlib_settings', 'hamlib_port', fallback="4532")

    try:
        # Use External Server
        server_ip = hamlib_ip_var.get()
        server_port = int(hamlib_PORT)
        print(f"Connect to external hamlib-server at {server_ip}:{server_port}...")

        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_connection.connect((server_ip, server_port))
        gui_state_control(11)  # Connected status

        # Start thread to update frequency and mode
        threading.Thread(target=update_frequency_and_mode_thread, daemon=True).start()


    except Exception as e:
        messagebox.showerror("Error", f"Failed to connect to hamlib: {e}")
        disconnect_from_hamlib()




# Function to establish socket connection after hamlib is started
def establish_socket_connection():
    global socket_connection
    try:
        server_ip = hamlib_ip_var.get()
        server_port = int(hamlib_PORT)
        print(f"Connect to external hamlib-server at {server_ip}:{server_port}...")
        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_connection.connect((server_ip, server_port))

        gui_state_control(11)  # Connected status
        threading.Thread(target=update_frequency_and_mode_thread, daemon=True).start()

    except socket.error as e:
        messagebox.showerror("Error", f"Can not connect!: {e}")
        disconnect_from_hamlib()





# Function to disconnect from hamlib
def disconnect_from_hamlib():
    global hamlib_process, socket_connection
    freqmode_tracking_var.set(False)  # Uncheck the "Frequency / Mode" checkbox
    gui_state_control(12)  # Update to "Disconnected" status

    # Signal the frequency update thread to stop
    stop_frequency_thread.set()

    # Wait for a moment to ensure the thread finishes cleanly
    time.sleep(0.2)  # Allow the thread time to exit (adjust as necessary)

    # Safely close the socket connection
    if socket_connection:
        try:
            socket_connection.close()
        except socket.error as e:
            print(f"Error closing socket: {e}")  # Log the error, if any
        finally:
            socket_connection = None

    # Safely terminate hamlib process
    if hamlib_process:
        try:
            hamlib_process.terminate()
        except Exception as e:
            print(f"Error terminating hamlib process: {e}")  # Log the error
        finally:
            hamlib_process = None





# Function to handle RPRT x error codes
def handle_rprtx_error(error_code):
    print(f"[Hamlib] RPRT {error_code}:")

    if error_code in [-7, -9]:
        print(f"[Hamlib] Critical RPRT {error_code}, please restart HamlibServer.")
        messagebox.showerror("Hamlib Server Error", "Please restart HamlibServer")
        disconnect_from_hamlib()
        return

    error_messages = {
        -5: "I/O error (communication failure).",
        -8: "Communication timed out with the radio.",
        -10: "Radio not present or unable to communicate.",
        -11: "Command rejected by the radio.",
    }

    error_message = error_messages.get(error_code, f"Unknown hamlib error (RPRT {error_code}).")
    messagebox.showerror("hamlib Error", error_message)








def update_frequency_and_mode_thread():
    global frequency_var, frequency_mhz, last_passband
    last_mode = None

    while not stop_frequency_thread.is_set():
        if socket_connection is None:
            print("[Hamlib] No socket connection; stopping thread.")
            break

        try:
            socket_connection.sendall(b"f\n")
            freq_resp = socket_connection.recv(64).decode().strip()

            if "RPRT -7" in freq_resp:
                handle_rprtx_error(-7)
                break
            if "RPRT -9" in freq_resp:
                handle_rprtx_error(-9)
                break
            if freq_resp.isdigit():
                frequency_hz = int(freq_resp)
                frequency_mhz = frequency_hz / 1_000_000
                frequency_var.set(f"{frequency_mhz:.4f}")
            else:
                print(f"[Hamlib] Invalid frequency response: {freq_resp}")

            time.sleep(0.1)

            socket_connection.sendall(b"m\n")
            response = socket_connection.recv(256).decode().strip()

            if "RPRT -7" in response:
                handle_rprtx_error(-7)
                break
            if "RPRT -9" in response:
                handle_rprtx_error(-9)
                break

            lines = response.splitlines()
            if len(lines) >= 2:
                mode = lines[0].strip()
                passband_str = lines[1].strip()

                if mode and mode != last_mode:
                    mode_var.set(mode)
                    last_mode = mode
                    on_mode_change()

                try:
                    pb = int(passband_str)
                    if pb > 0 and pb != last_passband:
                        last_passband = pb
                        print(f"[Hamlib] Passband updated to: {last_passband}")
                except ValueError:
                    print(f"[Hamlib] Invalid passband: {passband_str}")
            else:
                print(f"[Hamlib] Incomplete mode/passband response: {lines}")

        except (socket.error, ValueError) as e:
            print(f"[Hamlib] Communication error: {e}")
            disconnect_from_hamlib()
            break

        time.sleep(0.5)






# Manual Frequency or Mode input handler
def handle_callsign_or_frequency_entry(event=None):
    value = callsign_var.get().strip().upper()

    valid_modes = {
        'USB', 'LSB', 'CW', 'CWR', 'RTTY', 'RTTYR', 'AM', 'FM', 'WFM', 'AMS',
        'PKTLSB', 'PKTUSB', 'PKTFM', 'ECSSUSB', 'ECSSLSB', 'FA',
        'SAM', 'SAL', 'SAH', 'DSB'
    }

    def refocus():
        callsign_var.set("")
        callsign_entry.focus_set()

    def handle_rprt_error_with_popup(code):
        print(f"[Hamlib] Error code: {code}. Please restart HamlibServer.")
        messagebox.showerror("Hamlib Server Error", "Please restart HamlibServer")

    def check_response(response):
        if "RPRT -7" in response:
            handle_rprt_error_with_popup(-7)
            return False
        if "RPRT -9" in response:
            handle_rprt_error_with_popup(-9)
            return False
        return True

    # --- + / - KHz steps ---
    if re.fullmatch(r'[+-]\d{1,5}', value):
        try:
            step_khz = int(value)
            if frequency_mhz is None:
                print("[Hamlib] No current frequency to adjust from.")
                return refocus()

            new_freq_mhz = frequency_mhz + (step_khz / 1000.0)
            new_freq_hz = int(new_freq_mhz * 1_000_000)

            if not (1_000_000 <= new_freq_hz <= 500_000_000):
                print(f"[Hamlib] Target frequency {new_freq_hz} Hz out of range.")
                return refocus()

            if socket_connection is None:
                return refocus()

            socket_connection.sendall(f"F {new_freq_hz}\n".encode())
            response = ""
            timeout = time.time() + 1.0
            while True:
                chunk = socket_connection.recv(1024).decode()
                response += chunk
                if "RPRT 0" in response or "RPRT -7" in response or "RPRT -9" in response or time.time() > timeout:
                    break

            if not check_response(response):
                return refocus()

            if "RPRT 0" in response:
                print(f"[Hamlib] Frequency adjusted by {step_khz} kHz to {new_freq_hz} Hz")
            else:
                print(f"[Hamlib] Frequency adjustment failed: {response}")
                handle_rprtx_error(-1)

        except Exception as e:
            print(f"[Hamlib] Error adjusting frequency: {e}")

        return refocus()

    # --- Mode input ---
    if value in valid_modes:
        if socket_connection is None:
            print("[Hamlib] No socket connection; mode command skipped.")
            return refocus()

        try:
            socket_connection.sendall(b"+m\n")
            mode_response = ""
            timeout = time.time() + 1.0
            while True:
                chunk = socket_connection.recv(1024).decode()
                mode_response += chunk
                if "RPRT 0" in mode_response or "RPRT -7" in mode_response or "RPRT -9" in mode_response or time.time() > timeout:
                    break

            if not check_response(mode_response):
                return refocus()

            current_mode = None
            current_passband = -1

            for line in mode_response.strip().splitlines():
                if line.startswith("Mode:"):
                    current_mode = line.split(":", 1)[1].strip()
                elif line.startswith("Passband:"):
                    try:
                        current_passband = int(line.split(":", 1)[1].strip())
                    except ValueError:
                        print(f"[Hamlib] Invalid passband format in: '{line}'")

            if current_mode != value:
                command = f"+M {value} {current_passband}\n"
                socket_connection.sendall(command.encode())

                response = ""
                timeout = time.time() + 1.0
                while True:
                    chunk = socket_connection.recv(1024).decode()
                    response += chunk
                    if "RPRT 0" in response or "RPRT -7" in response or "RPRT -9" in response or time.time() > timeout:
                        break

                if not check_response(response):
                    return refocus()

                if "RPRT 0" in response:
                    print(f"[Hamlib] Mode successfully set to {value} with passband {current_passband}")
                else:
                    print(f"[Hamlib] Mode set failed, response: {response}")
                    handle_rprtx_error(-1)
            else:
                print(f"[Hamlib] Mode {value} already active; no command sent.")

        except socket.error as e:
            print(f"[Hamlib] Socket error during mode set: {e}")
            handle_rprtx_error(-5)

        return refocus()

    # --- Frequency input ---
    if re.fullmatch(r'\d{4,7}', value):
        try:
            frequency_khz = int(value)

            if not (1000 <= frequency_khz <= 500000):
                print(f"[Input] Rejected: {frequency_khz} kHz is out of valid range.")
                return refocus()

            if socket_connection is None:
                print("[Hamlib] No socket connection; frequency command skipped.")
                return refocus()

            frequency_hz = frequency_khz * 1000
            socket_connection.sendall(f"F {frequency_hz}\n".encode())
            response = ""
            timeout = time.time() + 1.0
            while True:
                chunk = socket_connection.recv(1024).decode()
                response += chunk
                if "RPRT 0" in response or "RPRT -7" in response or "RPRT -9" in response or time.time() > timeout:
                    break

            if not check_response(response):
                return refocus()

            if "RPRT 0" in response:
                print(f"[Hamlib] Frequency successfully set to {frequency_hz} Hz")
            else:
                print(f"[Hamlib] Frequency set failed: {response}")
                handle_rprtx_error(-1)

        except socket.error as e:
            print(f"[Hamlib] Socket error: {e}")
            handle_rprtx_error(-5)

        except ValueError:
            print("[Input] Invalid numeric frequency format.")

        return refocus()

    # --- Invalid input ---
    print(f"[Input] Ignored: '{value}' is not a valid kHz frequency or supported mode.")
    return refocus()





#########################################################################################
#  __  __ ___ _  _ _   _ _ ___ 
# |  \/  | __| \| | | | ( ) __|
# | |\/| | _|| .` | |_| |/\__ \
# |_|  |_|___|_|\_|\___/  |___/
#
#########################################################################################                              

def open_station_setup():
    global Station_Setup_Window

    if Station_Setup_Window is not None and Station_Setup_Window.winfo_exists():
        Station_Setup_Window.lift()
        return

    Station_Setup_Window = tk.Toplevel(root)
    Station_Setup_Window.title("Station Setup")
    Station_Setup_Window.resizable(False, False)

    if platform.system() == "Darwin":
        Station_Setup_Window.geometry("500x460")
    else:
        Station_Setup_Window.geometry("500x460")


    # Force window to stay on top and modal
    Station_Setup_Window.transient(root)
    Station_Setup_Window.grab_set()
    Station_Setup_Window.focus_set()
    Station_Setup_Window.lift()

    # Center the window
    Station_Setup_Window.update_idletasks()
    w = Station_Setup_Window.winfo_width()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()
    x = root_x + (root_w // 2) - (w // 2)
    y = root_y
    Station_Setup_Window.geometry(f"+{x}+{y}")

    local_callsign = tk.StringVar(value=my_callsign_var.get())
    local_operator = tk.StringVar(value=my_operator_var.get())
    local_locator = tk.StringVar(value=my_locator_var.get())
    local_location = tk.StringVar(value=my_location_var.get())
    local_pota = tk.StringVar(value=my_pota_var.get())
    local_pota_name = tk.StringVar()
    local_bota = tk.StringVar(value=my_bota_var.get())
    local_bota_name = tk.StringVar()
    local_bota_lat = tk.StringVar()
    local_bota_long = tk.StringVar()
    local_wwff = tk.StringVar(value=my_wwff_var.get())
    local_wwff_name = tk.StringVar()
    local_wwff_lat = tk.StringVar()
    local_wwff_long = tk.StringVar()    
    local_qrzapi = tk.StringVar(value=my_qrzapi_var.get())
    local_upload_qrz = tk.BooleanVar(value=upload_qrz_var.get())

    local_callsign.trace("w", lambda *args: local_callsign.set(local_callsign.get().upper()))
    local_operator.trace("w", lambda *args: local_operator.set(local_operator.get().upper()))
    local_locator.trace("w", lambda *args: local_locator.set(local_locator.get().upper()))
    local_wwff.trace("w", lambda *args: local_wwff.set(local_wwff.get().upper()))
    local_pota.trace("w", lambda *args: local_pota.set(local_pota.get().upper()))
    local_bota.trace("w", lambda *args: local_bota.set(local_bota.get().upper()))
    
    Station_Setup_Window.grid_columnconfigure(0, weight=1)

    # ---------------- LabelFrame 1: Station info ----------------
    lf1 = tk.LabelFrame(Station_Setup_Window, text="Station Setup", font=('Arial', 10, 'bold'))
    lf1.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
    lf1.grid_columnconfigure(1, weight=1)

    tk.Label(lf1, text="Callsign:", font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=1, sticky='w')
    tk.Entry(lf1, textvariable=local_callsign, font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=10, pady=5, sticky='ew')

    tk.Label(lf1, text="Operator:", font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=1, sticky='w')
    tk.Entry(lf1, textvariable=local_operator, font=('Arial', 10, 'bold')).grid(row=1, column=1, padx=10, pady=5, sticky='ew')

    tk.Label(lf1, text="Locator:", font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=1, sticky='w')
    tk.Entry(lf1, textvariable=local_locator, font=('Arial', 10, 'bold')).grid(row=2, column=1, padx=10, pady=5, sticky='ew')


    def open_qralocator():
        url = "https://www.egloff.eu/qralocator/"
        webbrowser.open(url)

    btn = tk.Button(lf1, text="Find Your QRA Locator", command=open_qralocator)
    btn.grid(row=2, column=2, padx=10, pady=5)    

    tk.Label(lf1, text="Location:", font=('Arial', 10)).grid(row=3, column=0, padx=10, pady=1, sticky='w')
    tk.Entry(lf1, textvariable=local_location, font=('Arial', 10, 'bold')).grid(row=3, column=1, padx=10, pady=5, sticky='ew')

    notebook = ttk.Notebook(Station_Setup_Window)
    notebook.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    Station_Setup_Window.grid_rowconfigure(1, weight=0)
    Station_Setup_Window.grid_columnconfigure(0, weight=1)

    # ---------- POTA tab ----------
    pota_frame = tk.Frame(notebook, background='#f0f0f0')
    notebook.add(pota_frame, text="POTA")

    pota_frame.grid_columnconfigure(1, weight=1)

    tk.Label(pota_frame, text="Reference No.:", font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=1, sticky='w')
    pota_entry = tk.Entry(pota_frame, textvariable=local_pota, font=('Arial', 10, 'bold'))
    pota_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
    pota_entry.bind("<FocusOut>", lambda e: auto_fill_pota_prefix(local_pota, local_pota_name, local_callsign))

    tk.Label(pota_frame, text="Park name:", font=('Arial', 10)).grid(row=1, column=0, columnspan=2, padx=10, pady=1, sticky='w')
    tk.Label(pota_frame, textvariable=local_pota_name, font=('Arial', 10, 'bold'), wraplength=360, justify="left").grid(row=1, column=1, columnspan=2, padx=10, pady=1, sticky='w')


    # ---------- WWFF tab ----------
    wwff_frame = tk.Frame(notebook, background='#f0f0f0')
    notebook.add(wwff_frame, text="WWFF")

    wwff_frame.grid_columnconfigure(1, weight=1)

    tk.Label(wwff_frame, text="Reference No.:", font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=1, sticky='w')
    wwff_entry = tk.Entry(wwff_frame, textvariable=local_wwff, font=('Arial', 10, 'bold'))
    wwff_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
    wwff_entry.bind("<FocusOut>", lambda e: auto_fill_wwff_prefix(local_wwff, local_wwff_name, local_wwff_lat, local_wwff_long, local_callsign))

    tk.Label(wwff_frame, text="Park name:", font=('Arial', 10)).grid(row=1, column=0, columnspan=2, padx=10, pady=1, sticky='w')
    tk.Label(wwff_frame, textvariable=local_wwff_name, font=('Arial', 10, 'bold'), wraplength=360, justify="left").grid(row=1, column=1, columnspan=2, padx=10, pady=1, sticky='w')


    # ---------- BOTA tab ----------
    bota_frame = tk.Frame(notebook, background='#f0f0f0')
    notebook.add(bota_frame, text="BOTA")

    bota_frame.grid_columnconfigure(1, weight=1)

    tk.Label(bota_frame, text="Reference No.:", font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=1, sticky='w')
    bota_entry = tk.Entry(bota_frame, textvariable=local_bota, font=('Arial', 10, 'bold'))
    bota_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
    bota_entry.bind("<FocusOut>", lambda e: auto_fill_bota_prefix(local_bota, local_bota_name, local_bota_lat, local_bota_long, local_callsign))

    tk.Label(bota_frame, text="Bunker name:", font=('Arial', 10)).grid(row=1, column=0, columnspan=2, padx=10, pady=1, sticky='w')
    tk.Label(bota_frame, textvariable=local_bota_name, font=('Arial', 10, 'bold'), wraplength=360, justify="left").grid(row=1, column=1, columnspan=2, padx=10, pady=1, sticky='w')


    # Auto fill calls
    auto_fill_pota_prefix(local_pota, local_pota_name, local_callsign)
    auto_fill_wwff_prefix(local_wwff, local_wwff_name, local_wwff_lat, local_wwff_long, local_callsign)
    auto_fill_bota_prefix(local_bota, local_bota_name, local_bota_lat, local_bota_long, local_callsign)

    for frame in (pota_frame, wwff_frame, bota_frame):
        frame.grid_columnconfigure(0, minsize=100)
        frame.grid_columnconfigure(1, weight=1)


    # ---------------- LabelFrame 5: QRZ Upload ----------------
    lf5 = tk.LabelFrame(Station_Setup_Window, text="QRZ Upload", font=('Arial', 10, 'bold'))
    lf5.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
    lf5.grid_columnconfigure(1, weight=1)

    tk.Checkbutton(lf5, text="Upload to QRZ", variable=local_upload_qrz).grid(row=0, column=0, columnspan=2, sticky="w", padx=10)

    tk.Label(lf5, text="QRZ API Key:", font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=1, sticky='w')
    qrzapi_entry = tk.Entry(lf5, textvariable=local_qrzapi, font=('Arial', 10, 'bold'), show="*")
    qrzapi_entry.grid(row=1, column=1, padx=(10, 100), pady=5, sticky='ew')

    def toggle_qrz_visibility():
        if qrzapi_entry.cget('show') == '*':
            qrzapi_entry.config(show='')
            toggle_button.config(text='Hide')
        else:
            qrzapi_entry.config(show='*')
            toggle_button.config(text='Show')

    toggle_button = tk.Button(lf5, text='Show', command=toggle_qrz_visibility, width=10)
    toggle_button.place(in_=qrzapi_entry, relx=1.0, x=5, y=-5, anchor='nw')

    tk.Label(lf5, text="API key needs to match Callsign!\nkey must be in format:\nXXXX-XXXX-XXXX-XXXX", 
             font=('Arial', 8, "bold")).grid(row=2, column=0, columnspan=2, padx=10, pady=1, sticky='ew')


    def close_window():
        global Station_Setup_Window
        Station_Setup_Window.destroy()
        Station_Setup_Window = None

    def save_setup():
        if not is_valid_locator(local_locator.get().strip()):
            messagebox.showerror("Invalid Locator", "The Maidenhead locator must be at least 4 characters and valid.\nExample: FN31 or FN31TK")
            return
        # Set global values from local vars
        my_callsign_var.set(local_callsign.get())
        my_operator_var.set(local_operator.get())
        my_locator_var.set(local_locator.get())
        my_location_var.set(local_location.get())
        my_pota_var.set(local_pota.get())
        my_wwff_var.set(local_wwff.get())
        my_bota_var.set(local_bota.get())
        my_qrzapi_var.set(local_qrzapi.get())
        upload_qrz_var.set(local_upload_qrz.get())

        save_station_setup()
        close_window()

    def cancel_setup():
        close_window()


    tk.Button(Station_Setup_Window, text="Save & Exit", command=save_setup, width=10, height=2).grid(row=5, column=0, padx=20, pady=10, sticky="w")
    tk.Button(Station_Setup_Window, text="Cancel", command=cancel_setup, width=10, height=2).grid(row=5, column=0, padx=20, pady=10, sticky="e")

    Station_Setup_Window.protocol("WM_DELETE_WINDOW", close_window)



def open_preferences():
    global Preference_Window, utc_offset_var, hamlib_ip_var, hamlib_port_var

    if Preference_Window is not None and Preference_Window.winfo_exists():
        Preference_Window.lift()
        return

    Preference_Window = tk.Toplevel(root)
    Preference_Window.title("Preferences")
    Preference_Window.resizable(False, False)

    if platform.system() == "Darwin":
        Preference_Window.geometry("350x490")
    else:
        Preference_Window.geometry("350x490")

    Preference_Window.transient(root)
    Preference_Window.grab_set()
    Preference_Window.focus_set()
    Preference_Window.lift()

    Preference_Window.update_idletasks()
    w = Preference_Window.winfo_width()

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()

    x = root_x + (root_w // 2) - (w // 2)
    y = root_y
    Preference_Window.geometry(f"+{x}+{y}")

    hamlib_port_var = tk.StringVar(value=config.get('hamlib_settings', 'hamlib_port', fallback="4532"))
    hamlib_ip_var = tk.StringVar(value=config.get('hamlib_settings', 'hamlib_ip', fallback="127.0.0.1"))
    wsjtx_port = config.get('Wsjtx_settings', 'wsjtx_port', fallback="2333")

    # === LabelFrame 1: Reload last logbook on startup ===
    lf_reload = tk.LabelFrame(Preference_Window, text="Reload last logbook on startup", font=('Arial', 10, 'bold'))
    lf_reload.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    reload_last_logbook_var = tk.BooleanVar(value=config.getboolean('General', 'reload_last_logbook', fallback=False))
    tk.Label(lf_reload, text="Enable Reload:").grid(row=0, column=0, sticky="w", pady=2)
    tk.Checkbutton(lf_reload, variable=reload_last_logbook_var).grid(row=0, column=1, sticky="w", pady=2)

    # === LabelFrame 2: UTC Time offset ===
    lf_utc = tk.LabelFrame(Preference_Window, text="UTC Time offset", font=('Arial', 10, 'bold'))
    lf_utc.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    tk.Label(lf_utc, text="Offset (Hours):").grid(row=0, column=0, sticky="w", pady=2)
    utc_offset_var = tk.StringVar(value=config.get('Global_settings', 'utc_offset', fallback='0'))
    utc_offset_menu = ttk.Combobox(lf_utc, textvariable=utc_offset_var, values=[str(i) for i in range(-12, 13)], width=5)
    utc_offset_menu.grid(row=0, column=1, sticky="w", pady=2)
    utc_offset_var.trace_add('write', lambda *args: update_datetime())

    # === LabelFrame 3: Hamlib Setup ===
    lf_hamlib = tk.LabelFrame(Preference_Window, text="Hamlib Setup", font=('Arial', 10, 'bold'))
    lf_hamlib.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    tk.Label(lf_hamlib, text="Port:").grid(row=0, column=0, sticky="w", pady=2)
    hamlib_port_var = tk.StringVar(value=config.get('hamlib_settings', 'hamlib_port', fallback="4532"))
    server_port_frame = tk.Frame(lf_hamlib)
    for value in ["4532", "4536", "4538", "4540"]:
        tk.Radiobutton(server_port_frame, text=value, variable=hamlib_port_var, value=value).pack(side=tk.LEFT)
    server_port_frame.grid(row=0, column=1, sticky="w", pady=2)

    tk.Label(lf_hamlib, text="IP-address:").grid(row=1, column=0, sticky="w", pady=2)
    ip_entry = tk.Entry(lf_hamlib, textvariable=hamlib_ip_var)
    ip_entry.grid(row=1, column=1, sticky="w", pady=2)
    ip_entry.configure(state="normal")

    # === LabelFrame 4: QSO Reception using UDP (WSJT-X) ===
    lf_wsjtx = tk.LabelFrame(Preference_Window, text="QSO Reception using UDP (WSJT-X)", font=('Arial', 10, 'bold'))
    lf_wsjtx.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    wsjtx_port_var = tk.StringVar(value=wsjtx_port)
    tk.Label(lf_wsjtx, text="Port:").grid(row=0, column=0, sticky="e", pady=2)
    wsjtx_port_entry = tk.Entry(lf_wsjtx, textvariable=wsjtx_port_var, width=10)
    wsjtx_port_entry.grid(row=0, column=1, sticky="w", pady=2)

    # === LabelFrame 5: QRZ Lookup Settings ===
    lf_qrz = tk.LabelFrame(Preference_Window, text="QRZ Lookup Settings", font=('Arial', 10, 'bold'))
    lf_qrz.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    use_qrz_lookup_var = tk.BooleanVar(value=config.getboolean("QRZ", "use_qrz_lookup", fallback=False))
    tk.Label(lf_qrz, text="Use QRZ Lookup:").grid(row=0, column=0, sticky="w", pady=2)
    tk.Checkbutton(lf_qrz, variable=use_qrz_lookup_var).grid(row=0, column=1, sticky="w", pady=2)

    tk.Label(lf_qrz, text="Username:").grid(row=1, column=0, sticky="e", pady=2)
    tk.Label(lf_qrz, text="Password:").grid(row=2, column=0, sticky="e", pady=2)

    qrz_username_var = tk.StringVar(value=config.get("QRZ", "username", fallback=""))
    qrz_password_var = tk.StringVar(value=config.get("QRZ", "password", fallback=""))

    qrz_username_entry = tk.Entry(lf_qrz, textvariable=qrz_username_var)
    qrz_password_entry = tk.Entry(lf_qrz, textvariable=qrz_password_var, show="*")

    qrz_username_entry.grid(row=1, column=1, sticky="w", pady=2)
    qrz_password_entry.grid(row=2, column=1, sticky="w", pady=2, padx=(0, 100))

    def toggle_password_visibility():
        if qrz_password_entry.cget('show') == '*':
            qrz_password_entry.config(show='')
            toggle_pw_button.config(text='Hide')
        else:
            qrz_password_entry.config(show='*')
            toggle_pw_button.config(text='Show')

    toggle_pw_button = tk.Button(lf_qrz, text='Show', command=toggle_password_visibility, width=10)
    toggle_pw_button.place(in_=qrz_password_entry, relx=1.0, x=5, y=-5, anchor='nw')

    def toggle_qrz_entries(*args):
        state = 'normal' if use_qrz_lookup_var.get() else 'disabled'
        qrz_username_entry.config(state=state)
        qrz_password_entry.config(state=state)

    use_qrz_lookup_var.trace_add("write", toggle_qrz_entries)
    toggle_qrz_entries()

    # === LabelFrame 6: Backup Folder ===
    lf_backup = tk.LabelFrame(Preference_Window, text="Backup Folder", font=('Arial', 10, 'bold'))
    lf_backup.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    backup_folder_var = tk.StringVar(value=config.get("General", "backup_folder", fallback=""))
    backup_entry = tk.Entry(lf_backup, textvariable=backup_folder_var, width=40)
    backup_entry.grid(row=0, column=1, sticky="w", pady=2)

    def choose_backup_folder():
        folder = filedialog.askdirectory(title="Select Backup Folder")
        if folder:
            backup_folder_var.set(folder)

    tk.Button(lf_backup, text="Browse", command=choose_backup_folder).grid(row=0, column=0, sticky="e", pady=2, padx=(0,5))

    def is_valid_ip(ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def is_valid_port(port):
        try:
            port = int(port)
            return 0 <= port <= 65535
        except (ValueError, TypeError):
            return False

    def value_check():
        if not is_valid_port(wsjtx_port_var.get()):
            messagebox.showerror("Error", f"{wsjtx_port_var.get()} is an invalid port.")
            return
        if not is_valid_ip(hamlib_ip_var.get()):
            messagebox.showerror("Error", f"{hamlib_ip_var.get()} is an invalid IP address.")
            return
        save_preferences()

    def close_window():
        global Preference_Window
        Preference_Window.destroy()
        Preference_Window = None

    def save_preferences():
        if 'reload_last_logbook' in config['General']:
            if current_json_file:
                config['General']['reload_last_logbook'] = str(reload_last_logbook_var.get())
            else:
                config['General']['reload_last_logbook'] = "False"
        config['Global_settings']['utc_offset'] = utc_offset_var.get()
        config['hamlib_settings']['hamlib_port'] = hamlib_port_var.get()
        config['hamlib_settings']['hamlib_ip'] = hamlib_ip_var.get()
        config["Wsjtx_settings"]['wsjtx_port'] = str(wsjtx_port_var.get())

        if 'QRZ' not in config:
            config.add_section('QRZ')
        if qrz_username_var.get().strip():
            config['QRZ']['username'] = qrz_username_var.get().strip()
        if qrz_password_var.get().strip():
            config['QRZ']['password'] = qrz_password_var.get().strip()
        config['QRZ']['use_qrz_lookup'] = str(use_qrz_lookup_var.get())

        if backup_folder_var.get().strip():
            config['General']['backup_folder'] = backup_folder_var.get().strip()

        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

        update_datetime()
        disconnect_from_hamlib()
        restart_listener(config)
        close_window()

    def cancel_preferences():
        close_window()

    tk.Button(Preference_Window, text="Save & Exit", command=value_check, width=10, height=2).grid(row=70, column=0, columnspan=2, padx=20, pady=10, sticky="w")
    tk.Button(Preference_Window, text="Cancel", command=cancel_preferences, width=10, height=2).grid(row=70, column=0, columnspan=2, padx=20, pady=10, sticky="e")

    Preference_Window.protocol("WM_DELETE_WINDOW", close_window)



#########################################################################################
#   ___ ___  _  _ ___ ___ ___   _    ___   _   ___    __       ___   ___   _____ 
#  / __/ _ \| \| | __|_ _/ __| | |  / _ \ /_\ |   \  / _|___  / __| /_\ \ / / __|
# | (_| (_) | .` | _| | | (_ | | |_| (_) / _ \| |) | > _|_ _| \__ \/ _ \ V /| _| 
#  \___\___/|_|\_|_| |___\___| |____\___/_/ \_\___/  \_____|  |___/_/ \_\_/ |___|
#
#########################################################################################


# Function for loading parameters from config.ini, creates default parameters or file of not exists
def load_config():
    """
    Load parameters from config.ini and ensure every section and key is explicitly checked.
    If the configuration file does not exist, create it with default values.
    """
    file_path = CONFIG_FILE

    # Check if the file exists; if not, create it with default sections and keys
    if not os.path.exists(file_path):
        print("Configuration file not found. Creating a new one with default values.")
        config['Global_settings'] = {}
        config['General'] = {}
        config['hamlib_settings'] = {}
        config['Wsjtx_settings'] = {}

    # Read the existing file or newly created sections
    config.read(file_path)

    # Ensure all sections and their keys exist
    # Global_settings
    if 'Global_settings' not in config:
        config.add_section('Global_settings')
    if 'utc_offset' not in config['Global_settings']:
        config['Global_settings']['utc_offset'] = '0'

    # General
    if 'General' not in config:
        config.add_section('General')
    if 'reload_last_logbook' not in config['General']:
        config['General']['reload_last_logbook'] = 'False'
    if 'last_loaded_logbook' not in config['General']:
        config['General']['last_loaded_logbook'] = ''

    # hamlib_settings
    if 'hamlib_settings' not in config:
        config.add_section('hamlib_settings')
    if 'hamlib_port' not in config['hamlib_settings']:
        config['hamlib_settings']['hamlib_port'] = '4532'
    if 'hamlib_ip' not in config['hamlib_settings']:
        config['hamlib_settings']['hamlib_ip'] = '127.0.0.1'


    # Wsjtx_settings
    if 'Wsjtx_settings' not in config:
        config.add_section('Wsjtx_settings')
    if 'wsjtx_port' not in config['Wsjtx_settings']:
        config['Wsjtx_settings']['wsjtx_port'] = '2333'
        
    if 'QRZ' not in config:
        config.add_section('QRZ')
    if 'username' not in config['QRZ']:
        config['QRZ']['username'] = ''
    if 'password' not in config['QRZ']:
        config['QRZ']['password'] = ''
    if 'use_qrz_lookup' not in config['QRZ']:
        config['QRZ']['use_qrz_lookup'] = 'False'

        
        
    # Save the updated config if any changes were made
    with open(file_path, 'w') as configfile:
        config.write(configfile)





def load_station_setup():
    # Load station details from JSON logbook if the file is loaded
    if current_json_file and os.path.exists(current_json_file):
        try:
            with open(current_json_file, 'r', encoding='utf-8') as file:
                logbook_data = json.load(file)
                #Check for Valid fields in "STATION", otherwise set defaults
                station_info = logbook_data.get("Station", {})
                my_operator_var.set(station_info.get("Operator", "N0CALL"))
                my_callsign_var.set(station_info.get("Callsign", "N0CALL"))
                my_locator_var.set(station_info.get("Locator", "JO22LO"))
                my_location_var.set(station_info.get("Location", ""))
                my_wwff_var.set(station_info.get("WWFF", ""))
                my_pota_var.set(station_info.get("POTA", ""))
                my_bota_var.set(station_info.get("BOTA", ""))
                my_qrzapi_var.set(station_info.get("QRZAPI", ""))
                upload_qrz_var.set(bool(station_info.get("QRZUpload", False)))

                my_callsign_entry.config(textvariable=my_callsign_var)
                my_operator_entry.config(textvariable=my_operator_var)
                my_locator_entry.config(textvariable=my_locator_var)
                my_location_entry.config(textvariable=my_location_var)
                my_wwff_entry.config(textvariable=my_wwff_var)
                my_pota_entry.config(textvariable=my_pota_var)
                my_bota_entry.config(textvariable=my_bota_var)

        except (json.JSONDecodeError, KeyError) as e:
            messagebox.showerror("Error", f"Failed to load station details from logbook: {e}")




def save_station_setup():
    # Save station_callsign and station_locator to JSON logbook
    if current_json_file:
        try:
            with open(current_json_file, 'r+', encoding='utf-8') as file:
                try:
                    json_data = json.load(file)
                except json.JSONDecodeError:
                    json_data = {}  # Initialize as empty if file is empty

                # Update or add the Station section
                json_data["Station"] = {
                    "Callsign": my_callsign_var.get().upper(),
                    "Operator": my_operator_var.get().upper(),
                    "Locator": my_locator_var.get().upper(),
                    "Location" : my_location_var.get(),
                    "WWFF": my_wwff_var.get(),
                    "POTA": my_pota_var.get(),
                    "BOTA": my_bota_var.get(),
                    "QRZAPI": my_qrzapi_var.get(),
                    "QRZUpload": upload_qrz_var.get()
                }

                # Write back to the JSON file
                file.seek(0)
                json.dump(json_data, file, ensure_ascii=False, indent=4)
                file.truncate()  # Ensures no leftover data in the file
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save station details to logbook: {e}")

















#########################################################################################
#   ___  ___  ____  _    ___   ___  _  ___   _ ___ 
#  / _ \| _ \|_  / | |  / _ \ / _ \| |/ / | | | _ \
# | (_) |   / / /  | |_| (_) | (_) | ' <| |_| |  _/
#  \__\_\_|_\/___| |____\___/ \___/|_|\_\\___/|_|  
##
#########################################################################################

def extract_core(callsign):
    callsign = callsign.strip().upper()
    parts = callsign.split('/')
    if len(parts) == 3:
        return parts[1]  # prefix/MainCallsign/suffix
    elif len(parts) == 2:
        # suffix = only letters (like /P of /M or /POTA)
        if re.fullmatch(r'[A-Z]+', parts[1]):
            return parts[0]
        else:
            return parts[1]
    return callsign


def get_session_key(username, password):
    encoded_username = urllib.parse.quote(username)
    encoded_password = urllib.parse.quote(password)
    url = f"https://xmldata.qrz.com/xml/current/?username={encoded_username}&password={encoded_password}"

    try:
        response = requests.get(url, timeout=5)
        root_xml = ET.fromstring(response.content)
        ns = {"qrz": "http://xmldata.qrz.com"}

        key = root_xml.findtext(".//qrz:Key", namespaces=ns)
        error = root_xml.findtext(".//qrz:Error", namespaces=ns)
        return key, error

    except requests.exceptions.RequestException as e:
        print("QRZ login failed:", e)
        return None, "❌ Connection QRZ XML Failed"


def open_qrz_link(event, callsign):
    url = f"https://www.qrz.com/db/{callsign}"
    webbrowser.open_new_tab(url)


def query_callsign(session_key, callsign):
    import re
    ns = {"qrz": "http://xmldata.qrz.com"}

    def do_query(cs):
        print(f"[DEBUG] Querying QRZ for callsign: {cs}")
        url = f"https://xmldata.qrz.com/xml/current/?s={session_key}&callsign={cs}"
        try:
            response = requests.get(url, timeout=5)
            root = ET.fromstring(response.content)
            return root.find(".//qrz:Callsign", ns)
        except Exception as e:
            print(f"Error fetching QRZ XML for {cs}:", e)
            return None

    # Stap 1: probeer originele callsign
    callsign_element = do_query(callsign)

    fallback_name = ""

    if callsign_element is None:
        base = extract_core(callsign)
        if base != callsign:
            fallback_element = do_query(base)
            if fallback_element is not None:
                # Gebruik alleen de naam uit fallback-element
                full_name = f"{fallback_element.findtext('qrz:fname', '', ns)} {fallback_element.findtext('qrz:name', '', ns)}".strip()
                QRZ_status_label.config(
                    text=f"ℹ️ Fallback QRZ lookup: name from {base}",
                    fg="orange",
                    font=('Arial', 8, 'italic')
                )
                QRZ_status_label.unbind("<Button-1>")

                return {
                    "callsign": base,
                    "name": full_name,
                    "address": "",
                    "city": "",
                    "zipcode": "",
                    "province": "",
                    "country": "",
                    "email": "",
                    "grid": "",
                    "cq_zone": "",
                    "itu_zone": "",
                    "qslmgr": "",
                    "lat": "",
                    "lon": "",
                    "mapslink": "",
                }


        # Fallback werkte ook niet
        clear_qrz_fields()
        QRZ_status_label.config(text="⚠️ No Callsign found in QRZ XML.", fg="red")
        return None


    found_call = callsign_element.findtext("qrz:call", default="Unknown", namespaces=ns)

    QRZ_status_label.config(
        text=f"🔍 Found {found_call} in QRZ lookup.",
        fg="blue",
        cursor="hand2",
        font=('Arial', 8, 'underline')
    )
    QRZ_status_label.unbind("<Button-1>")
    QRZ_status_label.bind("<Button-1>", lambda e, cs=found_call: open_qrz_link(e, cs))

    lat = callsign_element.findtext("qrz:lat", default="", namespaces=ns)
    lon = callsign_element.findtext("qrz:lon", default="", namespaces=ns)
    maps_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else ""

    # Als we een fallback naam hebben, gebruik die (alleen voor naamveld)
    full_name = f"{callsign_element.findtext('qrz:fname', '', ns)} {callsign_element.findtext('qrz:name', '', ns)}".strip()
    if not full_name and fallback_name:
        full_name = fallback_name

    return {
        "callsign": found_call,
        "name": full_name,
        "address": callsign_element.findtext("qrz:addr1", "", ns),
        "city": callsign_element.findtext("qrz:addr2", "", ns),
        "zipcode": callsign_element.findtext("qrz:zip", "", ns),
        "province": callsign_element.findtext("qrz:state", "", ns),
        "country": callsign_element.findtext("qrz:country", "", ns),
        "email": callsign_element.findtext("qrz:email", "", ns),
        "grid": callsign_element.findtext("qrz:grid", "", ns),
        "cq_zone": callsign_element.findtext("qrz:cqzone", "", ns),
        "itu_zone": callsign_element.findtext("qrz:ituzone", "", ns),
        "qslmgr": callsign_element.findtext("qrz:qslmgr", "", ns),
        "lat": lat,
        "lon": lon,
        "mapslink": maps_link,
    }

def threaded_on_query():
    threading.Thread(target=on_query_thread, daemon=True).start()

def on_query_thread():
    use_qrz = config.getboolean("QRZ", "use_qrz_lookup", fallback=False)
    if not use_qrz:
        return

    username = config.get("QRZ", "username", fallback="").strip()
    password = config.get("QRZ", "password", fallback="").strip()
    callsign = callsign_var.get().strip()

    if not username or not password:
        root.after(0, lambda: messagebox.showwarning("Missing Credentials", "QRZ username/password not found in config.ini"))
        return

    if not callsign:
        return

    session_key, error = get_session_key(username, password)

    if not session_key:
        if error:
            def show_error():
                QRZ_status_label.config(text=error, fg="red")
                if any(w in error.lower() for w in ["invalid", "incorrect", "not authorized"]):
                    messagebox.showerror("QRZ Login Failed", "Username or password incorrect.")
                elif "connection" in error.lower():
                    messagebox.showerror("Connection Error", "Unable to reach QRZ XML server.")
                else:
                    messagebox.showerror("QRZ Error", error)
            root.after(0, show_error)
        return

    data = query_callsign(session_key, callsign)
    if data is None:
        return  # already handled

    def update_gui():
        locator_var.set(data.get("grid", ""))
        name_var.set(data.get("name", ""))
        city_var.set(data.get("city", ""))
        address_var.set(data.get("address", ""))
        zipcode_var.set(data.get("zipcode", ""))
        qsl_info_var.set(data.get("qslmgr", ""))

    root.after(0, update_gui)

def clear_qrz_fields():
    locator_var.set("")
    name_var.set("")
    city_var.set("")
    address_var.set("")
    zipcode_var.set("")
    qsl_info_var.set("")
    QRZ_status_label.config(text="❌ No data", fg="grey", cursor="")
    QRZ_status_label.unbind("<Button-1>")




# About Window
def show_about():
    global About_Window
    # Check if the window is already open
    if About_Window is not None and About_Window.winfo_exists():
        About_Window.lift()  # Bring the existing window to the front
        return

    About_Window = tk.Toplevel(root)
    About_Window.title("About")
    About_Window.resizable(False, False)
    About_Window.geometry("300x400")

    # Center the About_Window relative to root
    About_Window.update_idletasks()
    w = About_Window.winfo_width()

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()

    x = root_x + (root_w // 2) - (w // 2)
    y = root_y

    About_Window.geometry(f"+{x}+{y}") 

    tk.Label(About_Window, text="MiniBook", font=('Arial', 20, 'bold')).pack(pady=10)
    separator = tk.Frame(About_Window, height=2, bd=0, relief='sunken', bg='gray')
    separator.pack(fill='x', pady=5, padx=10)
    tk.Label(About_Window, text=f"Version {VERSION_NUMBER}\n\nA Python based\nJSON Logbook\n\nDeveloped by:\nBjörn Pasteuning\nPD5DJ\n\nCopyright 2024", font=('Arial', 10)).pack(pady=10)

    url = "https://www.pd5dj.nl"
    link = tk.Label(About_Window, text=url, fg="blue", cursor="hand2", font=('Arial', 10))
    link.pack(pady=10)
    link.bind("<Button-1>", lambda e: webbrowser.open(url))
    
    def close_window():
        global About_Window
        About_Window.destroy()
        About_Window = None

    tk.Button(About_Window, text="Close", command=close_window).pack(pady=10)
    
    # Handle window close event
    About_Window.protocol("WM_DELETE_WINDOW", close_window)    





#########################################################################################
#  ___ _  _ ___ _____ 
# |_ _| \| |_ _|_   _|
#  | || .` || |  | |  
# |___|_|\_|___| |_|  
#                     
#########################################################################################

# Function called beginning at start of program
def init():
    global hamlib_ip_var, hamlib_port_var

    # Checks if cty.day exists
    ctydat_check()
    
    # 
    load_dxcc_to_pota_map()

    # 
    load_pota_references()

    # Checks if wwff_directory.csv exists
    wwffref_check()

    #
    bota_check()

    # Creating & loading of config.ini
    load_config()
    no_file_loaded() # Checks if no logbook is loaded
    update_frequency_from_band() # Update Band to Frequency on Startup
    start_listener(config)
    gui_state_control(12) # Shows disconnected Hamlib status
    update_datetime()
    utc_offset_var.set(config.get('Global_settings', 'utc_offset', fallback='0'))
    hamlib_ip_var  = tk.StringVar(value=config.get('hamlib_settings', 'hamlib_ip', fallback="127.0.0.1"))
    hamlib_port_var     = tk.StringVar(value=config.get('hamlib_settings', 'hamlib_port', fallback=4532))
    callsign_entry.focus_set() # Set focus to the callsign entry field
    load_last_logbook_on_startup()


# Save geometries for root and Logbook_Window
def save_window_geometry(window, name):
    """
    Save a specific window's geometry to the configuration file.
    """
    if window.winfo_exists():
        config = configparser.ConfigParser()
        file_path = CONFIG_FILE
        if os.path.exists(file_path):
            config.read(file_path)
        config[name] = {"geometry": window.geometry()}
        with open(file_path, "w") as configfile:
            config.write(configfile)

# Load geometry for a window
def load_window_geometry(window, name):
    """
    Load geometry for a specific window from the configuration file.
    """
    file_path = CONFIG_FILE
    if os.path.exists(file_path):
        config = configparser.ConfigParser()
        config.read(file_path)
        if name in config and "geometry" in config[name]:
            window.geometry(config[name]["geometry"])
            

def load_window_position(window, name):
    """
    Load the position for a specific window, keeping its size unchanged.
    """
    file_path = CONFIG_FILE
    if os.path.exists(file_path):
        config = configparser.ConfigParser()
        config.read(file_path)
        if name in config and "geometry" in config[name]:
            saved_geometry = config[name]["geometry"]

            # Extract position (x, y) from saved geometry
            try:
                x, y = map(int, saved_geometry.split('+')[1:3])

                # Set only the position, not the size
                window.wm_geometry(f"+{x}+{y}")
            except (ValueError, IndexError):
                print(f"Invalid geometry format in config: {saved_geometry}")


# Exit program
def exit_program():
    response = messagebox.askyesno("Confirmation", "Are you sure you want to quit the program?")
    
    if response:  # If the user clicked "Yes"
        disconnect_from_hamlib()
        # Terminate hamlib if it’s running
        if hamlib_process and hamlib_process.poll() is None:
            
            hamlib_process.terminate()  # Gracefully terminate
            try:
                hamlib_process.wait(timeout=5)  # Wait for the process to terminate
            except subprocess.TimeoutExpired:
                hamlib_process.kill()  # Force kill if it didn’t terminate in time

        save_window_geometry(root, "MainWindow")
        if Logbook_Window is not None and Logbook_Window.winfo_exists():
            save_window_geometry(Logbook_Window, "LogbookWindow")

        root.destroy()
        sys.exit()

    else:  # If the user clicked "No"
        return



#########################################################################################
#  ___  ___ _____ _     ___ ___ ___ ___ ___ ___ _  _  ___ ___ 
# | _ \/ _ \_   _/_\   | _ \ __| __| __| _ \ __| \| |/ __| __|
# |  _/ (_) || |/ _ \  |   / _|| _|| _||   / _|| .` | (__| _| 
# |_|  \___/ |_/_/ \_\ |_|_\___|_| |___|_|_\___|_|\_|\___|___|
#
#########################################################################################

def download_pota_file():
    try:
        response = requests.get(pota_url)
        response.raise_for_status()
        with open(POTA_FILE, "wb") as f:
            f.write(response.content)
        messagebox.showinfo("Download", f"The file {POTA_FILE} has been downloaded successfully.")
    except Exception as e:
        messagebox.showerror("Download Error", f"Failed to download {POTA_FILE}: {e}")

def load_pota_references(pota_file=POTA_FILE):
    global pota_references
    pota_references = {}

    try:
        if not os.path.exists(pota_file):
            messagebox.showinfo("File Not Found", f"The file {pota_file} was not found. It will now be downloaded.")
            download_pota_file()

        with open(pota_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                pota_references[row["reference"]] = row["name"]

    except Exception as e:
        messagebox.showerror("Error", f"Error loading POTA reference list: {e}")

def load_dxcc_to_pota_map(json_file=POTA_MAP_FILE):
    global dxcc_to_pota_map
    try:
        if not os.path.exists(json_file):
            messagebox.showerror("Error", f"Mapping file {json_file} not found!")
            return
        with open(json_file, "r", encoding="utf-8") as f:
            dxcc_to_pota_map = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load mapping file: {e}")

def get_pota_park_name(ref_code):
    return pota_references.get(ref_code, "")


def auto_fill_pota_prefix(entry_var, park_name_var, callsign_var, event=None):
    """
    entry_var: StringVar gekoppeld aan POTA entry
    park_name_var: StringVar gekoppeld aan parknaam label
    callsign_var: StringVar gekoppeld aan callsign entry
    """
    raw_val = entry_var.get().strip()
    call = callsign_var.get().strip().upper()
    pota_digits = re.sub(r"\D", "", raw_val)

    pota_landcode = None  # Altijd initialiseren

    if pota_digits and call:
        land_prefix = None

        for entry in dxcc_data:
            match_found = False
            for p in entry.prefixes[1:]:
                if call.startswith(p.upper()):
                    land_prefix = entry.prefixes[0].upper()
                    match_found = True
                    break
            if not match_found and call.startswith(entry.prefixes[0].upper()):
                land_prefix = entry.prefixes[0].upper()
                match_found = True
            if match_found:
                break

        if not land_prefix:
            match = re.match(r"^([A-Z]+)", call)
            if match:
                land_prefix = match.group(1).upper()

        pota_landcode = dxcc_to_pota_map.get(land_prefix, land_prefix)

    if pota_landcode:
        padded_digits = pota_digits if len(pota_digits) >= 4 else pota_digits.zfill(4)
        ref_code = f"{pota_landcode}-{padded_digits}"
        entry_var.set(ref_code)
        update_pota_park_name(ref_code, park_name_var)
    else:
        # Geen landcode gevonden → alles leegmaken
        entry_var.set("")
        park_name_var.set("")        


def update_pota_park_name(ref_code, park_name_var):
    """Zoekt de POTA-naam en zet deze in het opgegeven StringVar."""
    park_name = pota_references.get(ref_code, "")
    park_name_var.set(park_name)





#########################################################################################
# __      ____      _____ ___   ___ ___ ___ ___ ___ _  _  ___ ___ 
# \ \    / /\ \    / / __| __| | _ \ __| __| _ \ __| \| |/ __| __|
#  \ \/\/ /  \ \/\/ /| _|| _|  |   / _|| _||   / _|| .` | (__| _| 
#   \_/\_/    \_/\_/ |_| |_|   |_|_\___|_| |_|_\___|_|\_|\___|___|
#                                                                 
#########################################################################################

def wwffref_check():
    global wwff_references
    try:
        if not os.path.exists(WWFF_FILE):
            messagebox.showinfo("File Not Found", "The file wwff_directory.csv was not found. It will now be downloaded.")
            download_wwffref_file()

        wwff_references = {}
        with open(WWFF_FILE, encoding="utf-8", newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                # We verwachten minstens 12 kolommen: ref, ..., lat, lon, ...
                if len(row) >= 12:
                    ref = row[0].strip().upper()
                    name = row[2].strip()
                    lat = row[10].strip()
                    lon = row[11].strip()

                    wwff_references[ref] = {
                        "name": name,
                        "lat": lat,
                        "lon": lon
                    }

    except Exception as e:
        messagebox.showerror("Error", f"Error loading WWFF reference list: {e}")



def download_wwffref_file():
    try:
        response = requests.get(wwffref_url)  # wwffref_url moet gedefinieerd zijn als de download-URL
        response.raise_for_status()
        
        with open(WWFF_FILE, "wb") as f:
            f.write(response.content)
        
        messagebox.showinfo("Download", "The file wwff_directory.csv has been downloaded successfully.")
    except Exception as e:
        messagebox.showerror("Download Error", f"Failed to download wwff_directory.csv: {e}")


def auto_fill_wwff_prefix(wwff_var, wwff_park_name_var, wwff_lat_var, wwff_long_var, callsign_var):
    raw_val = wwff_var.get().strip()
    call = callsign_var.get().strip().upper()
    wwff_digits = re.sub(r"\D", "", raw_val)

    land_prefix = None
    if wwff_digits and call:
        for entry in dxcc_data:
            match_found = False
            for p in entry.prefixes[1:]:  # secundaire prefixen
                if call.startswith(p.upper()):
                    land_prefix = entry.prefixes[0].upper()
                    match_found = True
                    break
            if not match_found and call.startswith(entry.prefixes[0].upper()):
                land_prefix = entry.prefixes[0].upper()
                match_found = True
            if match_found:
                break

        if not land_prefix:
            match = re.match(r"^([A-Z]+)", call)
            if match:
                land_prefix = match.group(1).upper()

    if land_prefix:
        ref_code = f"{land_prefix}FF-{wwff_digits.zfill(4)}"
        wwff_var.set(ref_code)

        park_info = wwff_references.get(ref_code)
        if park_info:
            wwff_park_name_var.set(park_info["name"])
            wwff_lat_var.set(park_info["lat"])
            wwff_long_var.set(park_info["lon"])
        else:
            wwff_park_name_var.set("")
            wwff_lat_var.set("")
            wwff_long_var.set("")
    else:
        wwff_var.set("")
        wwff_park_name_var.set("")
        wwff_lat_var.set("")
        wwff_long_var.set("")

#########################################################################################
#  ___  ___ _____ _     ___ ___ ___ ___ ___ ___ _  _  ___ ___ 
# | _ )/ _ \_   _/_\   | _ \ __| __| __| _ \ __| \| |/ __| __|
# | _ \ (_) || |/ _ \  |   / _|| _|| _||   / _|| .` | (__| _| 
# |___/\___/ |_/_/ \_\ |_|_\___|_| |___|_|_\___|_|\_|\___|___|
#
#########################################################################################                                                             

def download_bota_file():
    try:
        response = requests.get(bota_url)
        response.raise_for_status()
        with open(BOTA_FILE, "wb") as f:
            f.write(response.content)
        messagebox.showinfo("Download", f"The file {BOTA_FILE} has been downloaded successfully.")
    except Exception as e:
        messagebox.showerror("Download Error", f"Failed to download {BOTA_FILE}: {e}")

def bota_check():
    """Laad bota_directory.csv in bota_references (ref_code -> (name, lat, lon))."""
    global bota_references
    bota_references.clear()
    try:
        if not os.path.exists(BOTA_FILE):
            messagebox.showinfo("File Not Found", f"The file {BOTA_FILE} was not found. It will now be downloaded.")
            download_bota_file()

        with open(BOTA_FILE, encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # sla header over als aanwezig
            for parts in reader:
                if len(parts) >= 7:
                    ref_code = parts[2].strip().upper()
                    name = parts[3].strip()
                    lat = parts[5].strip()
                    lon = parts[6].strip()
                    bota_references[ref_code] = (name, lat, lon)

    except Exception as e:
        messagebox.showerror("Error", f"Error loading BOTA reference list: {e}")

def auto_fill_bota_prefix(bota_var, bota_name_var, bota_lat_var, bota_long_var, callsign_var):
    raw_val = bota_var.get().strip().upper()
    call = (callsign_var.get() or "").strip().upper()
    bota_digits = re.sub(r"\D", "", raw_val)

    special_prefixes = ["GI", "GW", "GU", "GM", "GJ", "GD"]  # directe landprefix
    land_prefix = None

    # initialiseer outputs
    bota_name_var.set("")
    bota_lat_var.set("")
    bota_long_var.set("")

    if bota_digits and call:
        # Eerst: check speciale lijst
        for sp in special_prefixes:
            if call.startswith(sp):
                land_prefix = sp
                break

        # Anders: gebruik dxcc_data
        if not land_prefix:
            for entry in dxcc_data:
                match_found = False
                for p in entry.prefixes[1:]:
                    if call.startswith(p.upper()):
                        land_prefix = entry.prefixes[0].upper()
                        match_found = True
                        break
                if not match_found and call.startswith(entry.prefixes[0].upper()):
                    land_prefix = entry.prefixes[0].upper()
                    match_found = True
                if match_found:
                    break

        # fallback: gebruik eerste letters/nummers
        if not land_prefix:
            m = re.match(r"^([A-Z0-9]+)", call)
            if m:
                land_prefix = m.group(1).upper()

    # Correctie 9M2 / 9M4 → 9M
    if land_prefix in ("9M2", "9M4"):
        land_prefix = "9M"

    if land_prefix:
        ref_code = f"B/{land_prefix}-{bota_digits.zfill(4)}".upper()
        bota_var.set(ref_code)

        info = bota_references.get(ref_code.upper())
        if info:
            name, lat, lon = info
            bota_name_var.set(name)
            bota_lat_var.set(lat)
            bota_long_var.set(lon)
        else:
            bota_name_var.set("")
            bota_lat_var.set("")
            bota_long_var.set("")







#########################################################################################
#
#  ___ ___ _____ ___ _  _   ___ ___ ___ ___ _____  __   ___ _____ _____ ___   _ _____ 
# | __| __|_   _/ __| || | | _ \ _ \ __| __|_ _\ \/ /  / __|_   _|_   _|   \ /_\_   _|
# | _|| _|  | || (__| __ | |  _/   / _|| _| | | >  <  | (__  | |   | |_| |) / _ \| |  
# |_| |___| |_| \___|_||_| |_| |_|_\___|_| |___/_/\_\  \___| |_|   |_(_)___/_/ \_\_|  
#                                                                                     
#########################################################################################

# Function to check if cty.day file exists in root folder
def ctydat_check():
    global dxcc_data
    try:
        if not os.path.exists(DXCC_FILE):
            messagebox.showinfo("File Not Found", "The file cty.dat was not found. It will now be downloaded.")
            download_ctydat_file()  # Automatically download the file after showing the message
    
    except Exception as e:
        messagebox.showerror("Error", f"Error loading data: {e}")
        return {}
    
    # load and parse cty.dat into dxcc_data with cty_parser.py
    dxcc_data = parse_cty_file(DXCC_FILE)



# Function to download the cty.dat file directly into the root folder
def download_ctydat_file():
    try:
        response = requests.get(ctydat_url)
        response.raise_for_status()  # Check if request was successful
        
        # Save the downloaded file to the root folder
        file_path = DXCC_FILE
        with open(file_path, 'wb') as file:
            file.write(response.content)

        messagebox.showinfo("Download", "The file cty.dat has been downloaded successfully.")
    
    except Exception as e:
        messagebox.showerror("Download Error", f"Failed to download file: {e}")



# Continent mapping
continent_map = {
    "EU": "Europe",
    "OC": "Oceania",
    "AF": "Africa",
    "AN": "Antarctica",
    "AS": "Asia",
    "NA": "North America",
    "SA": "South America"
}

def find_coordinates_by_callsign(callsign):
    callsign = callsign.strip().upper()
    for entry in dxcc_data:
        for raw_prefix in entry.prefixes:
            prefix = re.sub(r'[=;()\[\]*]', '', raw_prefix).strip().upper()
            if callsign.startswith(prefix):
                return entry.latitude, entry.longitude
    return None, None




def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def check_callsign_prefix(callsign, update_ui=True, skip_locator=False):
    global dxcc_data

    callsign = callsign.strip().upper()
    best_match = None
    best_prefix_len = 0

    for entry in dxcc_data:
        for raw_prefix in entry.prefixes:
            prefix = re.sub(r'[=;()\[\]*]', '', raw_prefix).strip().upper()
            if callsign.startswith(prefix) and len(prefix) > best_prefix_len:
                best_match = entry
                best_prefix_len = len(prefix)

    if best_match:
        global country_var, continent_var
        continent = best_match.continent
        continent_name = continent_map.get(continent, "Unknown")
        continent_var = continent
        country_var = best_match.name
        entityCode = prefix
        itu = str(best_match.itu_zone)
        cq = str(best_match.cq_zone)
        lat = best_match.latitude
        lon = best_match.longitude
        heading_var = tk.StringVar()
        distance_var_km = tk.StringVar()
        distance_var_miles = tk.StringVar()

        my_call = my_callsign_var.get().strip().upper()
        my_lat, my_lon = find_coordinates_by_callsign(my_call)

        if my_lat is not None and my_lon is not None:
            sp, lp = calculate_headings(my_lat, my_lon, lat, lon)
            heading_var.set(f"SP: {sp}°  /  LP: {lp}°")

            distance_km = haversine(my_lat, my_lon, lat, lon)
            distance_miles = distance_km * 0.621371

            distance_var_km.set(f"{distance_km:.1f}km")
            distance_var_miles.set(f"{distance_miles:.1f}mi")
        else:
            heading_var.set("SP: --°  /  LP: --°")
            distance_var_km.set("-- km")
            distance_var_miles.set("-- mi")

        if update_ui:
            country_continent_label.config(text=(f"{best_match.name}, ({continent_name})"))
            heading_label.config(text=(heading_var.get()))
            distance_label.config(text=(f"{(distance_var_km.get())} / {(distance_var_miles.get())}"))
            dxcc_cq_itu_label.config(text=(f"CQ: {cq}, ITU: {itu}"))

            # Only calculate from locator if not skipping to avoid recursion
            if not skip_locator and locator_var.get().strip():
                calculate_from_locator()

    else:
        continent_var = ""
        country_var = "[None]"
        entityCode = ""

        if update_ui:
            country_continent_label.config(text="----")
            heading_label.config(text="----")
            distance_label.config(text="----")
            dxcc_cq_itu_label.config(text="----")




def calculate_from_locator():
    """
    Calculates heading and distance based on locator_var and my_locator_var.
    If locator is too short (<4), falls back to prefix-based calculation.
    """
    loc = locator_var.get().strip().upper()
    my_loc = my_locator_var.get().strip().upper()

    # Fallback when locator is too short
    if len(loc) < 4:
        if DEBUG:
            print("[INFO] Locator too short (<4). Falling back to callsign prefix.")
        check_callsign_prefix(callsign_var.get().strip().upper(), skip_locator=True)
        return

    if not is_valid_locator(loc) or not is_valid_locator(my_loc):
        return

    def locator_to_latlon(locator):
        try:
            locator = locator.strip().upper()
            if len(locator) < 4:
                return None, None

            A = ord('A')
            lon = (ord(locator[0]) - A) * 20 - 180
            lat = (ord(locator[1]) - A) * 10 - 90
            lon += int(locator[2]) * 2
            lat += int(locator[3]) * 1
            if len(locator) >= 6:
                lon += (ord(locator[4]) - A) * 5 / 60
                lat += (ord(locator[5]) - A) * 2.5 / 60
            else:
                lon += 1
                lat += 0.5
            return lat, lon
        except Exception:
            return None, None

    lat1, lon1 = locator_to_latlon(my_loc)
    lat2, lon2 = locator_to_latlon(loc)

    if None in (lat1, lon1, lat2, lon2):
        return

    sp, lp = calculate_headings(lat1, lon1, lat2, lon2)
    heading_label.config(text=f"SP: {sp}°  /  LP: {lp}°")

    distance_km = haversine(lat1, lon1, lat2, lon2)
    distance_miles = distance_km * 0.621371
    distance_label.config(text=f"{distance_km:.1f}km / {distance_miles:.1f}mi")






#########################################################################################
# __      _____  ___ _  _____ ___    ___ ___ ___ ___  ___ ___ 
# \ \    / / _ \| _ \ |/ / __|   \  | _ ) __| __/ _ \| _ \ __|
#  \ \/\/ / (_) |   / ' <| _|| |) | | _ \ _|| _| (_) |   / _| 
#   \_/\_/ \___/|_|_\_|\_\___|___/  |___/___|_| \___/|_|_\___|
#                                                             
#########################################################################################

DEBUG_WB4 = False

def normalize_callsign(call):
    return call.upper().split('/')[0]  # Remove any suffix like /P, /M, /QRP, etc.

def update_worked_before_tree(*args):
    global qso_lines

    entered_call = callsign_var.get().strip().upper()
    if not entered_call:
        if DEBUG_WB4:
            print("ℹ️ No callsign entered, clearing tree.")
        workedb4_tree.delete(*workedb4_tree.get_children())
        return

    if DEBUG_WB4:
        print(f"🔍 Searching for callsign starting with: {entered_call}")

    matches = [qso for qso in qso_lines if qso.get("Callsign", "").upper().startswith(entered_call)]
    
    if DEBUG_WB4:
        print(f"📄 Found {len(matches)} match(es) for prefix {entered_call}")

    from datetime import datetime
    def sort_key(qso):
        date = qso.get("Date", "1900-01-01")
        time = qso.get("Time", "00:00:00")
        try:
            return datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.min

    matches.sort(key=sort_key, reverse=True)
    workedb4_tree.delete(*workedb4_tree.get_children())

    # Configure Treeview tags for coloring
    workedb4_tree.tag_configure("oddrow", background="#f0f0f0")
    workedb4_tree.tag_configure("evenrow", background="white")
    workedb4_tree.tag_configure("dupe_date_band_mode_match", foreground="white", background="red", font=("TkDefaultFont", 9, "bold"))  # RED
    workedb4_tree.tag_configure("exact_callsign_today", foreground="black", background="darkorange", font=("TkDefaultFont", 9, "bold"))          # ORANGE
    workedb4_tree.tag_configure("base_callsign_today", foreground="white", background="blue", font=("TkDefaultFont", 9, "bold"))                   # BLUE

    # Current inputs for matching
    today = date_var.get().strip()
    current_band = band_var.get().strip() if 'band_var' in globals() else ""
    current_mode = mode_var.get().strip().upper() if 'mode_var' in globals() else ""

    if DEBUG_WB4:
        print(f"📅 Today: {today}, Band: {current_band}, Mode: {current_mode}")

    row_color = True
    for qso in matches:
        tag = "oddrow" if row_color else "evenrow"
        row_color = not row_color

        qso_call = qso.get("Callsign", "").upper()
        base_qso_call = normalize_callsign(qso_call)
        base_entered_call = normalize_callsign(entered_call)

        date_match = qso.get("Date", "").strip() == today
        band_match = qso.get("Band", "").strip().lower() == current_band.lower()
        mode_match = qso.get("Mode", "").strip().upper() == current_mode

        if DEBUG_WB4:
            print(f"\n🧩 Evaluating QSO: {qso_call} @ {qso.get('Date')} {qso.get('Time')}")
            print(f"  ➤ Base QSO call: {base_qso_call}, Base entered: {base_entered_call}")
            print(f"  ➤ Date match: {date_match}, Band match: {band_match}, Mode match: {mode_match}")

        # Assign color tags:
        # 1) Exact callsign + date + band + mode => RED
        if qso_call == entered_call and date_match and band_match and mode_match:
            tag = "dupe_date_band_mode_match"  # RED
            if DEBUG_WB4:
                print("🔴 Full exact callsign + date + band + mode match (RED)")
        # 2) Exact callsign + date only => ORANGE
        elif qso_call == entered_call and date_match:
            tag = "exact_callsign_today"       # ORANGE
            if DEBUG_WB4:
                print("🟧 Exact callsign + date match (ORANGE)")
        # 3) Base callsign match + date only + different suffix => BLUE
        elif base_qso_call == base_entered_call and qso_call != entered_call and date_match:
            tag = "base_callsign_today"        # BLUE
            if DEBUG_WB4:
                print("🔵 Base callsign match + different suffix + date match (BLUE)")

        workedb4_tree.insert("", "end", values=(
            qso_call,
            qso.get("Date", ""),
            qso.get("Time", ""),
            qso.get("Band", ""),
            qso.get("Mode", ""),
            qso.get("Frequency", ""),
            qso.get("Country", "")
        ), tags=(tag,))



def show_color_legend():
    legend_win = tk.Toplevel(root)
    legend_win.title("Worked Before Color Legend")
    legend_win.resizable(False, False)
    legend_win.configure(padx=10, pady=10)

    width, height = 380, 200

    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_w = root.winfo_width()
    root_h = root.winfo_height()

    x = root_x + (root_w // 2) - (width // 2)
    y = root_y + (root_h // 2) - (height // 2)

    legend_win.geometry(f"{width}x{height}+{x}+{y}")

    legend_items = [
        ("Exact callsign match (including suffix)\nFull match on Date, Band, Mode",
         "red", "black"),
        ("Base callsign match (ignores suffix)\nFull match on Date, Band, Mode",
         "blue", "black"),
        ("Exact callsign match (including suffix)\nMatch on Date only",
         "darkorange", "black"),
        ("Callsign match\nJust worked before",
         "white", "black"),
    ]

    for i, (desc, bg, fg) in enumerate(legend_items):
        color_box = tk.Canvas(legend_win, width=25, height=25, bg=bg, highlightthickness=1, highlightbackground="black")
        color_box.grid(row=i, column=0, padx=(0,10), pady=5)

        label = tk.Label(legend_win, text=desc, justify="left", fg=fg, bg=legend_win.cget("bg"), font=("Arial", 10))
        label.grid(row=i, column=1, sticky="w")

    legend_win.transient(root)
    legend_win.grab_set()
    legend_win.focus_set()




#########################################################################################
#  __  __   _   ___ _  _ 
# |  \/  | /_\ |_ _| \| |
# | |\/| |/ _ \ | || .` |
# |_|  |_/_/ \_\___|_|\_|
#
#########################################################################################                        





# Main window
root = tk.Tk()

style = ttk.Style()
style.theme_use("clam")

if platform.system() == "Darwin": # MacOS
    root.geometry("620x650")
    root.minsize(620, 650)
else: # Linux, Windows
    root.geometry("680x760")
    root.minsize(680, 760)

root.resizable(False, False)

# Global variable for the logbook window
Logbook_Window = None

# Load saved geometry for the main window
load_window_position(root, "MainWindow")


# Configuration & Variables
config = configparser.ConfigParser()
date_var = tk.StringVar()
time_var = tk.StringVar()
callsign_var = tk.StringVar()
callsign_var.trace_add('write', lambda *args: check_callsign_prefix(callsign_var.get(),True)) # Trigger check on input change with the callsign value passed to the function
callsign_var.trace_add("write", update_worked_before_tree)
callsign_var.trace("w", lambda *args: callsign_var.set(callsign_var.get().upper()))
name_var = tk.StringVar()
city_var = tk.StringVar()
zipcode_var = tk.StringVar()
address_var = tk.StringVar()
qsl_info_var = tk.StringVar()
locator_var = tk.StringVar()
locator_var.trace("w", lambda *args: locator_var.set(locator_var.get().upper()))
locator_var.trace_add("write", lambda *args: calculate_from_locator())
my_locator_var = tk.StringVar()
my_location_var = tk.StringVar()
my_callsign_var = tk.StringVar()
my_operator_var = tk.StringVar()
my_pota_var = tk.StringVar()
my_bota_var = tk.StringVar()
pota_park_name_var = tk.StringVar()
my_wwff_var = tk.StringVar()
wwff_park_name_var = tk.StringVar()
my_qrzapi_var = tk.StringVar()

wwff_var = tk.StringVar()
wwff_var.trace("w", lambda *args: wwff_var.set(wwff_var.get().upper()))
wwff_lat_var = tk.StringVar()
wwff_long_var = tk.StringVar()
pota_var = tk.StringVar()
pota_var.trace("w", lambda *args: pota_var.set(pota_var.get().upper()))
bota_var = tk.StringVar()
bota_var.trace("w", lambda *args: bota_var.set(bota_var.get().upper()))
bota_name_var = tk.StringVar()
bota_lat_var = tk.StringVar()
bota_long_var = tk.StringVar()

country_var = tk.StringVar()
continent_var = tk.StringVar()
rst_sent_var = tk.StringVar(value="59")
rst_received_var = tk.StringVar(value="59")
comment_var = tk.StringVar()
frequency_var = tk.StringVar()
band_var = tk.StringVar(value="20m")
band_var.trace_add("write", update_worked_before_tree)
mode_var = tk.StringVar(value="USB")
mode_var.trace_add("write", update_worked_before_tree)
submode_var = tk.StringVar(value="")
satellite_var = tk.StringVar(value="")
utc_offset_var = tk.StringVar(value="0")
radio_status_var = tk.StringVar()
datetime_tracking_enabled = tk.BooleanVar(value=True)
freqmode_tracking_var = tk.BooleanVar(value=False)
qrz_username_var = tk.StringVar()
qrz_password_var = tk.StringVar()
upload_qrz_var = tk.BooleanVar(value=False)


# Preparation of hamlib in Threaded mode
hamlib_process = None
socket_connection = None

stop_frequency_thread = threading.Event()

update_title(root, VERSION_NUMBER, current_json_file, radio_status_var.get())

# Define the update_datetime function
def update_datetime():
    """Update the time variable with the current time."""
    if datetime_tracking_enabled.get():  # Only update if tracking is enabled
        try:
            utc_offset = int(utc_offset_var.get())
        except ValueError:
            utc_offset = 0
            print("Invalid UTC offset, defaulting to 0.")

        now = datetime.now() + timedelta(hours=utc_offset)
        time_var.set(now.strftime("%H:%M:%S"))
        date_var.set(now.strftime("%Y-%m-%d"))
        root.after(1000, update_datetime)  # Schedule next update

# Define toggle function for the checkbox
def toggle_datetime_tracking():
    """Toggle date time updates based on checkbox state."""
    if datetime_tracking_enabled.get():
        update_datetime()  # Start time updates if enabled

# Callback for the Freq/Mode option in the Tracking menu
def toggle_freq_mode():
    if freqmode_tracking_var.get():
        connect_to_hamlib_threaded()
        toggle_freq_mode
    else:
        disconnect_from_hamlib()


# Adding Menu to main window
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)

# Add checkbox to Preferences menu
file_menu.add_command(label="New logbook", command=create_new_json)
file_menu.add_command(label="Load logbook", command=load_json)

file_menu.add_separator()
file_menu.add_command(label="Open Backup Folder", command=open_backup_folder)

file_menu.add_separator()
file_menu.add_command(label="Station setup", command=open_station_setup, state='disabled')
file_menu.add_separator()

file_menu.add_command(label="Preferences", command=open_preferences)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_program)
menu_bar.add_cascade(label="File", menu=file_menu)

# Add "Tracking" menu as a submenu in File menu
tracking_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Tracking", menu=tracking_menu)
# Add "Time" checkbox in Tracking menu
tracking_menu.add_checkbutton(label="Date & Time", variable=datetime_tracking_enabled, command=toggle_datetime_tracking)
tracking_menu.add_checkbutton(label="Radio Frequency & Mode", variable=freqmode_tracking_var, command=toggle_freq_mode)

view_menu = tk.Menu(menu_bar, tearoff=0)
view_menu.add_command(label="Logbook", command=view_logbook)

view_menu.add_command(label="DX Cluster Viewer", command=open_dxspotviewer)

menu_bar.add_cascade(label="Window", menu=view_menu)

# --- Reference Menu ---
reference_menu = tk.Menu(menu_bar, tearoff=0)
reference_menu.add_command(label="DX Summit", command=lambda: webbrowser.open("http://www.dxsummit.fi/#/"))
reference_menu.add_separator()
reference_menu.add_command(label="POTA Activations", command=lambda: webbrowser.open("https://pota.app/#/"))
reference_menu.add_command(label="POTA Map", command=lambda: webbrowser.open("https://pota.app/#/map"))
reference_menu.add_command(label="POTA List", command=lambda: webbrowser.open("https://pota.app/#/parklist"))
reference_menu.add_separator()
reference_menu.add_command(label="WWFF Agenda", command=lambda: webbrowser.open("https://wwff.co/agenda/"))
reference_menu.add_command(label="WWFF Dutch Map", command=lambda: webbrowser.open("https://www.google.com/maps/d/u/0/view?hl=en&mid=1yXBN79NWlsI-wrZaDfyeXA2zg129nEU&ll=52.12186480765635%2C5.251994000000018&z=8"))
reference_menu.add_command(label="WWFF Global Map", command=lambda: webbrowser.open("https://ham-map.com/"))
reference_menu.add_command(label="WWFF Announce activation", command=lambda: webbrowser.open("https://www.cqgma.org/alertwwfflight.php"))
reference_menu.add_separator()
reference_menu.add_command(label="WW BOTA Map", command=lambda: webbrowser.open("https://wwbota.org/map/"))
#reference_menu.add_separator()
#reference_menu.add_command(label="SOTA Watch", command=lambda: webbrowser.open("https://sotawatch.sota.org.uk/"))
menu_bar.add_cascade(label="References", menu=reference_menu)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Worked Before Color Legend", command=show_color_legend)
help_menu.add_separator()
help_menu.add_command(label="Download latest CTY.DAT file", command=download_ctydat_file)
help_menu.add_command(label="Download latest Pota reference file", command=download_pota_file)
help_menu.add_command(label="Download latest WWFF reference file", command=download_wwffref_file)
help_menu.add_command(label="Download latest BOTA reference file", command=download_bota_file)
help_menu.add_command(label="Download Satellites Names", command=download_satellites)
help_menu.add_separator()
help_menu.add_command(label="About", command=show_about)
menu_bar.add_cascade(label="Help", menu=help_menu)

root.config(menu=menu_bar)


# Function to update frequency based on band selection
def update_frequency_from_band(*args):
    selected_band = band_var.get()
    default_frequency = band_to_frequency.get(selected_band, "")
    frequency_var.set(default_frequency)

# Function to check frequency and update the band if needed
def update_band_from_frequency(*args):
    frequency = frequency_var.get()
    
    try:
        frequency = float(frequency)
        for band, (low, high) in band_ranges.items():
            if low <= frequency <= high:
                # Frequency is within the band range, set the band
                band_var.set(band)
                break
        else:
            band_var.set("OOB")
            # If frequency is outside the known bands, don't change the band show Out Of Band
            pass
    except ValueError:
        pass  # Ignore invalid frequency input


# Function to handle backspace and other key events in the entry
def on_focus(event):
    event.widget.selection_clear()  # Clear any text selection
    event.widget.icursor(tk.END)    # Move cursor to the end

def on_keypress(event):
    current_value = frequency_var.get()
    
    if event.keysym in ("BackSpace","Tab","Return"):
        # Allow normal backspace behavior
        return True
    
    # Only allow numbers and one decimal point
    if event.char in "0123456789.":
        # Allow the decimal point if there is no decimal already in the entry
        if event.char == "." and current_value.count('.') >= 1:
            return "break"  # Prevent the second decimal point from being inserted
        return True
    else:
        return "break"  # Block other characters
    
# Entry Background color when focussed
def set_focus_color(event):
    event.widget.configure(background="#FFCCDD")

def reset_focus_color(event):
    event.widget.configure(background="white")


def handle_callsign_from_spot(callsign, freq=None, mode=None):
    callsign_var.set(callsign)
    callsign_entry.focus_set()
    callsign_entry.icursor(tk.END)

    # If frequency tracking is not active then update frequency and mode entries
    if not freqmode_tracking_var.get():
        if freq:
            frequency_var.set(freq)

        if mode and mode in mode_combobox['values']:
            mode_var.set(mode)

    use_qrz = config.getboolean("QRZ", "use_qrz_lookup", fallback=False)
    if use_qrz:
        threaded_on_query()


def on_tab_press(event):
    use_qrz = config.getboolean("QRZ", "use_qrz_lookup", fallback=True)
    if not use_qrz:
        return  # QRZ lookup disabled, do nothing

    threaded_on_query()
    return None





#------------- Field/Label positions Row/Column/Span --------------


My_Info_Frame_row       = 0
QSO_DateTime_Frame_row  = 1
MainEntry_Frame_row     = 2
WWFFPOTA_Frame_row      = 4
QRZ_Info_Frame_row      = 5
DXCC_QRZ_Info_row       = 6
Workedb4_Frame_row      = 7
Button_Frame_row        = 8
Status_Frame_row        = 9



Internal_Y_Padding      = 2
Frame_Y_Padding         = 2
bg_color = root.cget("bg")


root.option_add("*TCombobox*Font", ("Arial", 10))
style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))


# MY INFO FRAME
my_info_frame = tk.LabelFrame(root, bd=2, font=('Arial', 10, 'bold'), relief='groove', text="Station Information", labelanchor="n", pady=Internal_Y_Padding, bg='lightgrey')
my_info_frame.grid(row=My_Info_Frame_row, column=0, columnspan=7, sticky='ew', padx=5, pady=Frame_Y_Padding)

for i in range(6):
    my_info_frame.grid_columnconfigure(i, weight=1)

tk.Label(my_info_frame, text="Callsign:", font=('Arial', 10), bg='lightgrey').grid(row=0, column=0, sticky='e', padx=5)
my_callsign_entry = tk.Entry(my_info_frame, font=('Arial', 10, 'bold'), state='disabled', disabledbackground='white', disabledforeground='black', relief='sunk')
my_callsign_entry.grid(row=0, column=1, sticky='w', padx=5)

tk.Label(my_info_frame, text="Operator:", font=('Arial', 10), bg='lightgrey').grid(row=0, column=2, sticky='e', padx=5)
my_operator_entry = tk.Entry(my_info_frame, font=('Arial', 10, 'bold'), state='disabled', disabledbackground='white', disabledforeground='black', relief='sunk')
my_operator_entry.grid(row=0, column=3, sticky='w', padx=5)

tk.Label(my_info_frame, text="Locator:", font=('Arial', 10), bg='lightgrey').grid(row=0, column=4, sticky='e', padx=5)
my_locator_entry = tk.Entry(my_info_frame, font=('Arial', 10, 'bold'), state='disabled', disabledbackground='white', disabledforeground='black', relief='sunk')
my_locator_entry.grid(row=0, column=5, sticky='w', padx=5)

tk.Label(my_info_frame, text="Location:", font=('Arial', 10), bg='lightgrey').grid(row=1, column=0, sticky='e', padx=5)
my_location_entry = tk.Entry(my_info_frame, font=('Arial', 10, 'bold'), state='disabled', disabledbackground='white', disabledforeground='black', relief='sunk')
my_location_entry.grid(row=1, column=1, sticky='w', padx=5)

tk.Label(my_info_frame, text="WWFF:", font=('Arial', 10), bg='lightgrey').grid(row=1, column=2, sticky='e', padx=5)
my_wwff_entry = tk.Entry(my_info_frame, font=('Arial', 10, 'bold'), state='disabled', disabledbackground='white', disabledforeground='black', relief='sunk')
my_wwff_entry.grid(row=1, column=3, sticky='w', padx=5)

tk.Label(my_info_frame, text="POTA:", font=('Arial', 10), bg='lightgrey').grid(row=1, column=4, sticky='e', padx=5)
my_pota_entry = tk.Entry(my_info_frame, font=('Arial', 10, 'bold'), state='disabled', disabledbackground='white', disabledforeground='black', relief='sunk')
my_pota_entry.grid(row=1, column=5, sticky='w', padx=5)

tk.Label(my_info_frame, text="BOTA:", font=('Arial', 10), bg='lightgrey').grid(row=2, column=0, sticky='e', padx=5)
my_bota_entry = tk.Entry(my_info_frame, font=('Arial', 10, 'bold'), state='disabled', disabledbackground='white', disabledforeground='black', relief='sunk')
my_bota_entry.grid(row=2, column=1, sticky='w', padx=5)






DateTime_frame = tk.LabelFrame(root, bd=2, font=('Arial', 10, 'bold'), relief='groove', text="QSO Date & Time", labelanchor="n", pady=Internal_Y_Padding)
DateTime_frame.grid(row=QSO_DateTime_Frame_row, column=0, columnspan=7, sticky="ew", padx=5, pady=Frame_Y_Padding)


shared_column_widths = [80, 80 , 80, 80, 80, 80, 80]
for i, width in enumerate(shared_column_widths):
    DateTime_frame.grid_columnconfigure(i, weight=0, minsize=width)

# DATE
tk.Label(DateTime_frame, text="Date:", font=('Arial', 10)).grid(row=0, column=1, padx=5, pady=Internal_Y_Padding, sticky='e')
date_entry = DateEntry(DateTime_frame, textvariable=date_var, date_pattern='yyyy-mm-dd', font=('Arial', 10, 'bold'))
date_entry.grid(row=0, column=2, padx=5, pady=Internal_Y_Padding, sticky='w')
date_entry.configure(takefocus=False)

# TIME
tk.Label(DateTime_frame, text="Time:", font=('Arial', 10)).grid(row=0, column=4, padx=5, pady=Internal_Y_Padding, sticky='e')
time_entry = tk.Entry(DateTime_frame, textvariable=time_var, font=('Arial', 10, 'bold'), width=10)
time_entry.grid(row=0, column=5, padx=5, pady=Internal_Y_Padding, sticky='w')
time_entry.configure(takefocus=False)





MainEntry_frame = tk.LabelFrame(root, bd=2, font=('Arial', 10, 'bold'), relief='groove', text="QSO Entry", labelanchor="n", pady=Internal_Y_Padding)
MainEntry_frame.grid(row=MainEntry_Frame_row, column=0, columnspan=6, sticky='ew', padx=5, pady=Frame_Y_Padding)

shared_column_widths = [70, 100, 50, 80, 50, 80]
for i, width in enumerate(shared_column_widths):
    MainEntry_frame.grid_columnconfigure(i, weight=0, minsize=width)

# CALLSIGN
tk.Label(MainEntry_frame, text="Callsign:", font=('Arial', 10)).grid(row=0, column=0, padx=5, sticky='e')
callsign_entry = tk.Entry(MainEntry_frame, textvariable=callsign_var, font=('Arial', 14, 'bold'), width=14)
callsign_entry.grid(row=0, column=1, padx=5, pady=Internal_Y_Padding, sticky='w')
callsign_entry.bind("<Return>", handle_callsign_or_frequency_entry)
callsign_entry.bind("<Tab>", on_tab_press)
callsign_entry.bind("<FocusIn>", set_focus_color)
callsign_entry.bind("<FocusOut>", reset_focus_color)

# SENT
tk.Label(MainEntry_frame, text="Sent:", font=('Arial', 10)).grid(row=0, column=2, padx=5, sticky='e')
rst_sent_combobox = ttk.Combobox(MainEntry_frame, textvariable=rst_sent_var, values=rst_options, font=('Arial', 14, 'bold'), width=8)
rst_sent_combobox.grid(row=0, column=3, padx=5, pady=Internal_Y_Padding, sticky='w')

# RECEIVED
tk.Label(MainEntry_frame, text="Received:", font=('Arial', 10)).grid(row=0, column=4, padx=5, sticky='e')
rst_received_combobox = ttk.Combobox(MainEntry_frame, textvariable=rst_received_var, values=rst_options, font=('Arial', 14, 'bold'), width=8)
rst_received_combobox.grid(row=0, column=5, padx=5, pady=Internal_Y_Padding, sticky='w')

# LOCATOR
tk.Label(MainEntry_frame, text="Locator:", font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=Internal_Y_Padding, sticky='e')
locator_entry = tk.Entry(MainEntry_frame, textvariable=locator_var, font=('Arial', 14, 'bold'), width=12)
locator_entry.grid(row=1, column=1, padx=5, pady=Internal_Y_Padding, sticky='w')
locator_entry.bind("<FocusIn>", set_focus_color)
locator_entry.bind("<FocusOut>", reset_focus_color)

# MODE
tk.Label(MainEntry_frame, text="Mode:", font=('Arial', 10)).grid(row=1, column=2, padx=5, pady=Internal_Y_Padding, sticky='e')
mode_combobox = ttk.Combobox(MainEntry_frame, textvariable=mode_var, values=mode_options, font=('Arial', 14, 'bold'), width=8, state='readonly')
mode_combobox.grid(row=1, column=3, padx=5, pady=Internal_Y_Padding, sticky='w')
mode_combobox.bind("<<ComboboxSelected>>", on_mode_change)

# SUBMODE
tk.Label(MainEntry_frame, text="Submode:", font=('Arial', 10)).grid(row=1, column=4, padx=5, pady=Internal_Y_Padding, sticky='e')
submode_combobox = ttk.Combobox(MainEntry_frame, textvariable=submode_var, values=submode_options, font=('Arial', 14, 'bold'), width=8, state='readonly')
submode_combobox.grid(row=1, column=5, padx=5, pady=Internal_Y_Padding, sticky='w')
submode_combobox.configure(takefocus=False)

# BAND
tk.Label(MainEntry_frame, text="Band:", font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=Internal_Y_Padding, sticky='e')
band_combobox = ttk.Combobox(MainEntry_frame, width=8, textvariable=band_var, values=list(band_to_frequency.keys()), font=('Arial', 14, 'bold'), state='readonly')
band_combobox.grid(row=2, column=1, padx=5, pady=Internal_Y_Padding, sticky='w')
band_combobox.bind("<<ComboboxSelected>>", update_frequency_from_band)

# FREQUENCY
tk.Label(MainEntry_frame, text="Freq (MHz):", font=('Arial', 10)).grid(row=2, column=2, padx=5, pady=Internal_Y_Padding, sticky='e')
freq_entry = tk.Entry(MainEntry_frame, textvariable=frequency_var, font=('Arial', 14, 'bold'), width=10)
freq_entry.grid(row=2, column=3, padx=5, pady=Internal_Y_Padding, sticky='w')
freq_entry.bind("<FocusIn>", on_focus)
freq_entry.bind("<FocusIn>", set_focus_color)
freq_entry.bind("<FocusOut>", reset_focus_color)
freq_entry.bind("<KeyPress>", on_keypress)
frequency_var.trace("w", update_band_from_frequency)

# SATELLITE
tk.Label(MainEntry_frame, text="Satellite:", font=('Arial', 10)).grid(row=2, column=4, padx=5, pady=Internal_Y_Padding, sticky='e')
satellite_list = load_satellite_names()
satellite_list.insert(0, "")
satellite_var = tk.StringVar()
satellite_dropdown = ttk.Combobox(MainEntry_frame, textvariable=satellite_var, values=satellite_list, font=('Arial', 14, 'bold'), width=8, state="readonly")
satellite_dropdown.grid(row=2, column=5, padx=5, pady=Internal_Y_Padding, sticky='ew')

# NAME
tk.Label(MainEntry_frame, text="Name:", font=('Arial', 10)).grid(row=3, column=0, padx=5, pady=Internal_Y_Padding, sticky='e')
name_entry = tk.Entry(MainEntry_frame, textvariable=name_var, font=('Arial', 12, 'bold'))
name_entry.grid(row=3, column=1, padx=5, pady=Internal_Y_Padding, sticky='w')
name_entry.bind("<FocusIn>", set_focus_color)
name_entry.bind("<FocusOut>", reset_focus_color)

# COMMENT
tk.Label(MainEntry_frame, text="Comment:", font=('Arial', 10)).grid(row=3, column=2, padx=5, pady=Internal_Y_Padding, sticky='e')
comment_entry = tk.Entry(MainEntry_frame, textvariable=comment_var, font=('Arial', 12, 'bold'))
comment_entry.grid(row=3, column=3, columnspan=3, padx=5, pady=Internal_Y_Padding, sticky='ew')
comment_entry.bind("<FocusIn>", set_focus_color)
comment_entry.bind("<FocusOut>", reset_focus_color)








notebook = ttk.Notebook(root)
notebook.grid(row=WWFFPOTA_Frame_row, column=0, columnspan=99, sticky='nsew', padx=5, pady=Frame_Y_Padding)

# WWFF tab
wwff_tab = tk.Frame(notebook)
notebook.add(wwff_tab, text="WWFF")

wwff_tab.grid_columnconfigure(0, weight=0, minsize=70)
wwff_tab.grid_columnconfigure(1, weight=1)
wwff_tab.grid_columnconfigure(2, weight=0)

tk.Label(wwff_tab, text="Ref no.:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=Internal_Y_Padding, sticky='e')
wwff_entry = tk.Entry(wwff_tab, textvariable=wwff_var, font=('Arial', 14, 'bold'), width=10)
wwff_entry.grid(row=0, column=1, padx=5, pady=Internal_Y_Padding, sticky='w')
wwff_entry.bind("<FocusIn>", set_focus_color)
wwff_entry.bind(
    "<FocusOut>",
    lambda e: auto_fill_wwff_prefix(wwff_var, wwff_park_name_var, wwff_lat_var, wwff_long_var, callsign_var)
)

wwff_map_button = tk.Button(wwff_tab, text="Show Park on Map", 
                            command=lambda: open_osm_map(    wwff_lat_var, wwff_long_var, my_locator_var, my_callsign_var, wwff_var.get(), wwff_park_name_var.get()))
wwff_map_button.grid(row=0, column=2, padx=5, pady=Internal_Y_Padding, sticky='ew')

tk.Label(wwff_tab, text="Park Name:", font=('Arial', 10)).grid(row=1, column=0, padx=5, sticky='w')
tk.Label(wwff_tab, textvariable=wwff_park_name_var, font=('Arial', 10, 'bold')).grid(row=1, column=1, padx=5, sticky='w')

# POTA tab
pota_tab = tk.Frame(notebook)
notebook.add(pota_tab, text="POTA")

pota_tab.grid_columnconfigure(0, weight=0, minsize=70)
pota_tab.grid_columnconfigure(1, weight=1)

tk.Label(pota_tab, text="Ref no.:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=Internal_Y_Padding, sticky='e')
pota_entry = tk.Entry(pota_tab, textvariable=pota_var, font=('Arial', 14, 'bold'), width=10)
pota_entry.grid(row=0, column=1, padx=5, pady=Internal_Y_Padding, sticky='w')
pota_entry.bind("<FocusIn>", set_focus_color)
pota_entry.bind(
    "<FocusOut>",
    lambda e: auto_fill_pota_prefix(pota_var, pota_park_name_var, callsign_var)
)


tk.Label(pota_tab, text="Park Name:", font=('Arial', 10)).grid(row=1, column=0, padx=5, sticky='w')
tk.Label(pota_tab, textvariable=pota_park_name_var, font=('Arial', 10, 'bold')).grid(row=1, column=1, padx=5, sticky='w')


# BOTA tab
bota_tab = tk.Frame(notebook)
notebook.add(bota_tab, text="BOTA")

bota_tab.grid_columnconfigure(0, weight=0, minsize=70)
bota_tab.grid_columnconfigure(1, weight=1)
bota_tab.grid_columnconfigure(2, weight=0)

tk.Label(bota_tab, text="Ref no.:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=Internal_Y_Padding, sticky='e')
bota_entry = tk.Entry(bota_tab, textvariable=bota_var, font=('Arial', 14, 'bold'), width=10)
bota_entry.grid(row=0, column=1, padx=5, pady=Internal_Y_Padding, sticky='w')
bota_entry.bind("<FocusIn>", set_focus_color)
bota_entry.bind(
    "<FocusOut>",
    lambda e: auto_fill_bota_prefix(bota_var, bota_name_var, bota_lat_var, bota_long_var, callsign_var)
)

bota_map_button = tk.Button(bota_tab, text="Show Bunker on Map", 
                            command=lambda: open_osm_map(bota_lat_var, bota_long_var, my_locator_var, my_callsign_var, bota_var.get(), bota_name_var.get()))
bota_map_button.grid(row=0, column=2, padx=5, pady=Internal_Y_Padding, sticky='ew')

tk.Label(bota_tab, text="Bunker Name:", font=('Arial', 10)).grid(row=1, column=0, padx=5, sticky='w')
tk.Label(bota_tab, textvariable=bota_name_var, font=('Arial', 10, 'bold')).grid(row=1, column=1, padx=5, sticky='w')





notebook = ttk.Notebook(root)
notebook.grid(row=DXCC_QRZ_Info_row, column=0, columnspan=99, sticky='nsew', padx=5, pady=5)

# Tab 1: DXCC Info
dxcc_tab = ttk.Frame(notebook)
dxcc_tab.grid_columnconfigure(0, weight=1)
notebook.add(dxcc_tab, text="DXCC Info")

# Tab 2: Extra QRZ Lookup results
qrz_tab = tk.Frame(notebook, bg=bg_color)
notebook.add(qrz_tab, text="Extra QRZ Lookup results")


# Country/Continent label
country_continent_label = tk.Label(dxcc_tab, text="----", font=('Arial', 14, 'bold'), bg=bg_color)
country_continent_label.grid(row=0, column=0, sticky='ew', pady=(0, 5))

# Subframe-container
subframe_container = tk.Frame(dxcc_tab, bg=bg_color)
subframe_container.grid(row=1, column=0, sticky='ew')
subframe_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")

# Zones Frame
zones_frame = tk.LabelFrame(subframe_container, text="Zones", font=('Arial', 9, 'bold'),
                            labelanchor="n", bg=bg_color, relief='groove', bd=2)
zones_frame.grid(row=0, column=0, padx=5, pady=2, sticky='nsew')
zones_frame.grid_rowconfigure(0, weight=1)
zones_frame.grid_columnconfigure(0, weight=1)

dxcc_cq_itu_label = tk.Label(zones_frame, text="----", font=('Arial', 12, 'bold'), bg=bg_color)
dxcc_cq_itu_label.grid(row=0, column=0, sticky='nsew')

# Distance Frame
distance_frame = tk.LabelFrame(subframe_container, text="Distance", font=('Arial', 9, 'bold'),
                               labelanchor="n", bg=bg_color, relief='groove', bd=2)
distance_frame.grid(row=0, column=1, padx=5, pady=2, sticky='nsew')
distance_frame.grid_rowconfigure(0, weight=1)
distance_frame.grid_columnconfigure(0, weight=1)

distance_label = tk.Label(distance_frame, text="----", font=('Arial', 12, 'bold'), bg=bg_color)
distance_label.grid(row=0, column=0, sticky='nsew')

# Heading Frame
heading_frame = tk.LabelFrame(subframe_container, text="Heading", font=('Arial', 9, 'bold'),
                              labelanchor="n", bg=bg_color, relief='groove', bd=2)
heading_frame.grid(row=0, column=2, padx=5, pady=2, sticky='nsew')
heading_frame.grid_rowconfigure(0, weight=1)
heading_frame.grid_columnconfigure(0, weight=1)

heading_label = tk.Label(heading_frame, text="----", font=('Arial', 16, 'bold'), bg=bg_color)
heading_label.grid(row=0, column=0, sticky='nsew')

tk.Label(qrz_tab, text="Address:", font=('Arial', 10)).grid(row=0, column=0, sticky='e', padx=5, pady=Internal_Y_Padding)
address_entry = tk.Entry(qrz_tab, textvariable=address_var, font=('Arial', 10, 'bold'), width=30)
address_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=Internal_Y_Padding, sticky='w')
address_entry.bind("<FocusIn>", set_focus_color)
address_entry.bind("<FocusOut>", reset_focus_color)
address_entry.configure(takefocus=False)

tk.Label(qrz_tab, text="City:", font=('Arial', 10)).grid(row=1, column=0, sticky='e', padx=5, pady=Internal_Y_Padding)
city_entry = tk.Entry(qrz_tab, textvariable=city_var, font=('Arial', 10, 'bold'), width=30)
city_entry.grid(row=1, column=1, columnspan=2, sticky='w', padx=5, pady=Internal_Y_Padding)
city_entry.bind("<FocusIn>", set_focus_color)
city_entry.bind("<FocusOut>", reset_focus_color)
city_entry.configure(takefocus=False)

tk.Label(qrz_tab, text="Zipcode:", font=('Arial', 10)).grid(row=0, column=3, sticky='e', padx=5, pady=Internal_Y_Padding)
zipcode_entry = tk.Entry(qrz_tab, textvariable=zipcode_var, font=('Arial', 10, 'bold'), width=15)
zipcode_entry.grid(row=0, column=4, sticky='w', padx=5, pady=Internal_Y_Padding)
zipcode_entry.bind("<FocusIn>", set_focus_color)
zipcode_entry.bind("<FocusOut>", reset_focus_color)
zipcode_entry.configure(takefocus=False)

tk.Label(qrz_tab, text="QSL Info:", font=('Arial', 10)).grid(row=1, column=3, sticky='e', padx=5, pady=Internal_Y_Padding)
qsl_info_entry = tk.Entry(qrz_tab, textvariable=qsl_info_var, font=('Arial', 10, 'bold'), width=35)
qsl_info_entry.grid(row=1, column=4, columnspan=1, padx=5, pady=Internal_Y_Padding, sticky='w')
qsl_info_entry.bind("<FocusIn>", set_focus_color)
qsl_info_entry.bind("<FocusOut>", reset_focus_color)
qsl_info_entry.configure(takefocus=False)

qrz_tab.grid_columnconfigure(0, weight=0, minsize=70)
qrz_tab.grid_columnconfigure(1, weight=0, minsize=80)
qrz_tab.grid_columnconfigure(2, weight=0, minsize=10)
qrz_tab.grid_columnconfigure(3, weight=1)
qrz_tab.grid_columnconfigure(4, weight=1)






#----------- WORKED BEFORE FRAME ------------

workedb4_frame = tk.LabelFrame(root, bg=bg_color, bd=2, font=('Arial', 10, 'bold'), relief='groove', text="Worked Before Lookup", labelanchor="n", padx=5, pady=Internal_Y_Padding)
workedb4_frame.grid(row=Workedb4_Frame_row, column=0, columnspan=99, sticky="nsew", pady=Frame_Y_Padding, padx=5)

tree_frame = tk.Frame(workedb4_frame)
tree_frame.pack(fill="both", expand=True, padx=10, pady=0)

# Scrollbars
y_scroll = tk.Scrollbar(tree_frame, orient="vertical")
y_scroll.pack(side="right", fill="y")

# TreeView
cols = ("Callsign", "Date", "Time", "Band", "Mode", "Frequency", "Country")
workedb4_tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=5, yscrollcommand=y_scroll.set)

y_scroll.config(command=workedb4_tree.yview)

for col in cols:
    workedb4_tree.heading(col, text=col)
    workedb4_tree.column(col, anchor="center", width=80)

workedb4_tree.pack(fill="both", expand=True)



Button_frame = tk.Frame(root, bd=2, relief='groove', padx=5, pady=Internal_Y_Padding)
Button_frame.grid(row=Button_Frame_row, column=0, columnspan=7, pady=Frame_Y_Padding, padx=5, sticky='ew')

Button_frame.grid_columnconfigure(0, weight=1)
Button_frame.grid_columnconfigure(1, weight=1)
Button_frame.grid_columnconfigure(2, weight=1)
Button_frame.grid_columnconfigure(3, weight=1)

# Detecteer platform en pas stijl toe
use_ttk = False
if platform.system() == "Darwin":
    use_ttk = True
    style = ttk.Style()
    style.theme_use("clam")

    # Lookup button
    style.configure("Lookup.TButton",
        foreground="black",
        background="#FFFF80",
        font=('Arial', 10, 'bold'),
        anchor="center",
        justify="center",
        padding=(0, 6)
    )
    style.map("Lookup.TButton", background=[("active", "#e0e066")])

    # Log button
    style.configure("Log.TButton",
        foreground="black",
        background="#00FF80",
        font=('Arial', 10, 'bold'),
        anchor="center",
        justify="center",
        padding=(0, 6)
    )
    style.map("Log.TButton", background=[("active", "#00cc66")])

    # Wipe button
    style.configure("Wipe.TButton",
        foreground="black",
        background="#FF8080",
        font=('Arial', 10, 'bold'),
        anchor="center",
        justify="center",
        padding=(0, 6)
    )
    style.map("Wipe.TButton", background=[("active", "#cc6666")])

    # Exit button
    style.configure("Exit.TButton",
        foreground="white",
        background="grey",
        font=('Arial', 10, 'bold'),
        anchor="center",
        justify="center",
        padding=(0, 12)
    )
    style.map("Exit.TButton", background=[("active", "#666666")])


# --- Buttons ---
if use_ttk:
    # ttk variant met vaste afmeting in tekens
    lookup_button = ttk.Button(Button_frame, text="Lookup\nF2", command=threaded_on_query, style="Lookup.TButton", width=10)
    lookup_button.grid(row=0, column=1, padx=10)
    lookup_button.configure(takefocus=False)

    log_button = ttk.Button(Button_frame, text="Log QSO\nF5", command=log_qso, style="Log.TButton", width=10)
    log_button.grid(row=0, column=2, padx=10)
    log_button.configure(takefocus=False)

    wipe_button = ttk.Button(Button_frame, text="Wipe\nF1", command=reset_fields, style="Wipe.TButton", width=10)
    wipe_button.grid(row=0, column=0, padx=10)
    wipe_button.configure(takefocus=False)

    EXIT_button = ttk.Button(Button_frame, text="EXIT", command=exit_program, style="Exit.TButton", width=10)
    EXIT_button.grid(row=0, column=3, padx=10)
    EXIT_button.configure(takefocus=False)

else:
    # Lookup
    lookup_button = tk.Button(Button_frame, text="Lookup\nF2", command=threaded_on_query, bd=3, relief='raised', width=10, height=2, bg='#FFFF80', fg='black', font=('Arial', 10, 'bold'))
    lookup_button.grid(row=0, column=1, padx=10)
    lookup_button.configure(takefocus=False)

    # Log
    log_button = tk.Button(Button_frame, text="Log QSO\nF5", command=log_qso, bd=3, relief='raised', width=10, height=2, bg='#00FF80', fg='black', font=('Arial', 10, 'bold'))
    log_button.grid(row=0, column=2, padx=10)
    log_button.configure(takefocus=False)

    # Wipe
    wipe_button = tk.Button(Button_frame, text="Wipe\nF1", command=reset_fields, bd=3, relief='raised', width=10, height=2, bg='#FF8080', fg='black', font=('Arial', 10, 'bold'))
    wipe_button.grid(row=0, column=0, padx=10)
    wipe_button.configure(takefocus=False)

    # EXIT
    EXIT_button = tk.Button(Button_frame, text="EXIT", command=exit_program, bd=3, relief='raised', width=10, height=2, bg='grey', fg='white', font=('Arial', 10, 'bold'))
    EXIT_button.grid(row=0, column=3, padx=10)
    EXIT_button.configure(takefocus=False)



status_frame = tk.Frame(root, bd=2, relief='groove', padx=5, pady=Internal_Y_Padding)
status_frame.grid(row=Status_Frame_row, column=0, columnspan=7, rowspan=1, sticky="ew", padx=5, pady=Frame_Y_Padding)

status_frame.grid_columnconfigure(0, weight=1)
status_frame.grid_columnconfigure(1, weight=1)

# last_qso_label 
last_qso_label = tk.Label(status_frame, fg="blue", font=('Arial', 8, 'bold'), text="Last QSO info")
last_qso_label.grid(row=0, column=0, sticky='w', padx=5)

# QRZ_status_label 
QRZ_status_label = tk.Label(status_frame, font=('Arial', 8, 'bold'), text="QRZ Status")
QRZ_status_label.grid(row=0, column=1, sticky='e', padx=5)


# Buttons Bindings

# Bind F1 key to reset_fields function
def invoke_reset_fields(event=None):
    reset_fields()
root.bind("<F1>", invoke_reset_fields)

# Bind F2 key to Lookup function
def invoke_lookup_button(event=None):
    lookup_button.invoke()
root.bind("<F2>", invoke_lookup_button)

# Bind F5 key to log_button function
def invoke_log_button(event=None):
    log_button.invoke()
root.bind("<F5>", invoke_log_button)

def on_minibook_exit():
    global dxspotviewer_window
    if dxspotviewer_window and dxspotviewer_window.winfo_exists():
        dxspotviewer_window.destroy()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_minibook_exit)


# Call init function to Preset / Preload  variables / Tasks
init()

# Bind the on_close function to the "X" button
root.protocol("WM_DELETE_WINDOW", exit_program)

# Start main loop
root.mainloop()
