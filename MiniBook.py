#**********************************************************************************************************************************
# File          :   MiniBook.py
# Project       :   A Simple JSON Based logbook for portable use.
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
#**********************************************************************************************************************************

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import configparser
import os
from pathlib import Path
import requests
import re
import json
import webbrowser
from tkcalendar import DateEntry
import platform
import subprocess
import socket
import sys
import threading
import time
import ipaddress
import requests
import xml.etree.ElementTree as ET
import urllib.parse
import math


VERSION_NUMBER = ("v1.3.2")

# Configuration file path
DATA_FOLDER         = Path.cwd()
CONFIG_FILE         = "config.ini"
DXCC_FILE           = "dxcc.json"
SAT_FILE            = "satellites.txt"
current_json_file   = None  # logbook file

# --- QRZ Config ---
QRZ_URL = "https://xmldata.qrz.com/xml/current/"
QRZ_SESSION_KEY = None

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

# Flag image sizing
FLAG_IMAGE_WIDTH    = 40
FLAG_IMAGE_HEIGHT   = 40

# -------- Operating mode options --------
mode_options        = ["AM", "FM", "USB", "LSB", "SSB", "CW", "CW-R", "DIG", "RTTY", "MFSK", "DYNAMIC", "JT65", "JT8", "FT8", "PSK31", "PSK64", "PSK125", "QPSK31", "PKT","OLIVIA", "SSTV", "VARA","DOMINO"]
submode_options     = ["","FT4"]

# -------- RST Sent/Received options -------
rst_options         = [str(i) for i in range(51, 60)] + ["59+10dB", "59+20dB", "59+30dB", "59+40dB"]

# -------- DXCC information source --------
#dxcc_url            = "https://raw.githubusercontent.com/k0swe/dxcc-json/refs/heads/main/dxcc.json"
dxcc_url            = "https://raw.githubusercontent.com/pd5dj/dxcc-json/refs/heads/main/dxcc.json"



#########################################################################################
#  ___ _   _ _  _  ___ _____ ___ ___  _  _ ___ 
# | __| | | | \| |/ __|_   _|_ _/ _ \| \| / __|
# | _|| |_| | .` | (__  | |  | | (_) | .` \__ \
# |_|  \___/|_|\_|\___| |_| |___\___/|_|\_|___/
#                                              
#########################################################################################

# Function to update Title
def update_title(root, version, filename=None, status_text=None):
    parts = [f"MiniBook {version}"]
    if filename:
        parts.append(os.path.basename(filename))
    if status_text:
        parts.append(status_text)
    root.title(" | ".join(parts))


# Function to reset variables and entries when logbook file failed to load.
def no_file_loaded():
    global current_json_file

    current_json_file = None # Reset the current_json_file to None
    update_title(root, VERSION_NUMBER, "Load or create logbook first!", radio_status_var.get())
    my_locator_var.set("")
    my_callsign_var.set("")
    my_operator_var.set("")
    my_location_var.set("")
    my_callsign_label.config(textvariable=my_callsign_var)
    my_operator_label.config(textvariable=my_operator_var)
    my_locator_label.config(textvariable=my_locator_var)
    my_location_label.config(textvariable=my_location_var)
    file_menu.entryconfig("Station setup", state="disabled")


# Function to restore fields after logging
def reset_fields():
    comment_var.set("")
    last_qso_label.config(text="")
    callsign_var.set("")
    name_var.set("")
    city_var.set("")
    zipcode_var.set("")
    address_var.set("")
    qsl_info_var.set("")
    heading_var.set("")
    on_mode_change()  # 
    locator_var.set("")    
    callsign_entry.focus_set() # Set focus to the callsign entry field
    heading_entry.config(state='normal')
    heading_entry.delete(0, tk.END)
    heading_entry.config(state='readonly')            


# Function to check if Locator is valid format
def is_valid_locator(locator):
    """Check if a locator is valid: either empty or at least 4 characters matching the Maidenhead format."""
    if locator == "":
        return True  # Locator can be empty
    elif len(locator) >= 4 and re.match(r'^[A-R]{2}\d{2}([A-X]{2})?$', locator, re.IGNORECASE):
        return True
    return False


# Function to display Image in a label
def display_image(number, label, width, height):
    # Construct the image file name
    image_file = f"flags/{number}.png"

    # Try to load and display the image
    try:
        image = Image.open(image_file)
        image_resized = image.resize((width, height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image_resized)

        # Update the label with the image
        label.config(image=photo)
        label.image = photo  # Keep a reference to avoid garbage collection

    except FileNotFoundError:
        # Do nothing if the image is not found
        label.config(image="")  # Clear any existing image



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
        
# Function to fetch prefixes from the JSON file
def fetch_prefixes():
    try:
        file_path = DXCC_FILE

        if not os.path.exists(file_path):
            show_popup_download()
        
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
        
        prefix_map = {}
        
        for entry in data['dxcc']:
            prefixes = entry['prefix'].split(',')
            name = entry['name']
            cq = entry['cq']
            itu = entry['itu']
            continent = entry['continent']
            entityCode = entry['entityCode']
            
            for prefix in prefixes:
                cleaned_prefix = prefix.strip().upper()
                if cleaned_prefix:
                    prefix_map[cleaned_prefix] = {
                        'name': name,
                        'continent': continent,
                        'cq': cq,
                        'itu': itu,
                        'entityCode': entityCode,
                        'prefixRegex': entry['prefixRegex']  # Store the regex for this prefix
                    }
        
        return prefix_map
    
    except Exception as e:
        messagebox.showerror("Error", f"Error loading data: {e}")
        return {}


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
    "160m": "1.850",
    "80m": "3.650",
    "60m": "5.360",
    "40m": "7.000",
    "30m": "10.100",
    "20m": "14.000",
    "17m": "18.100",
    "15m": "21.000",
    "12m": "24.890",
    "11m": "27.000",
    "10m": "28.000",
    "6m": "50.000",
    "4m": "70.000",
    "2m": "144.000",
	"1.25m": "220.000",
    "70cm": "430.000",
	"33cm": "902.000",
    "23cm": "1296.000",
    "13cm": "2300.000"
}




def on_mode_change(event=None):
    selected_mode = mode_var.get().upper()
    if selected_mode in ["CW", "CW-R", "RTTY", "OLIVIA", "PSK31", "PSK64", "PSK125", "MFSK", "DOMINO", "VARA", "SSTV"]:
        rst_sent_var.set("599")
        rst_received_var.set("599")
    else:
        rst_sent_var.set(rst_options[8])
        rst_received_var.set(rst_options[8])



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
    global radio_status_var, external_server_ip, server_port_var


    if status == 10:
        radio_status_var.set("Connecting...")

    elif status == 11:
        radio_status_var.set(f"Connected to {external_server_ip.get()}:{server_port_var.get()}")

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


# Formats WWFF code by inserting a dash after "FF" when typed, but only once and ensures valid entry
def format_wwff_input(event, entry_widget, entry_var):
    value = entry_var.get().upper()

    # Insert dash after 'FF' if not already there
    ff_index = value.find("FF")
    if ff_index != -1:
        dash_index = ff_index + 2
        if len(value) > dash_index and value[dash_index] != "-":
            value = value[:dash_index] + "-" + value[dash_index:]
        elif len(value) == dash_index:
            value += "-"

    # Prevent recursion
    entry_widget.unbind("<KeyRelease>")
    entry_var.set(value)
    entry_widget.icursor(tk.END)
    entry_widget.bind("<KeyRelease>", lambda e: format_wwff_input(e, entry_widget, entry_var))

    # Validation
    if "-" in value:
        prefix, suffix = value.split("-", 1)
        if (
            len(prefix) >= 4 and         # At least 4 characters in prefix
            suffix.isdigit() and         # Suffix must be digits only
            len(suffix) >= 4             # At least 4 digits
        ):
            entry_widget.config(bg="lightgreen")
        else:
            entry_widget.config(bg="#FFCCDD")
    else:
        entry_widget.config(bg="#FFCCDD")

# Makes sure entries are uppercase
def format_pota_input(event, entry_widget, entry_var):
    # Force uppercase and get current value
    raw = entry_var.get().upper()

    # Regex om prefix (letters), digits, en suffix te scheiden
    match = re.match(r'^([A-Z]+)(\d*)(.*)', raw.replace('-', '', 1))  # Remove only first dash
    if not match:
        entry_widget.config(bg='#FFCCDD')
        return

    prefix, digits, suffix = match.groups()

    # Format output
    formatted = prefix
    if digits:
        formatted += '-' + digits
    if suffix:
        formatted += suffix

    # Update entry field
    entry_var.set(formatted)
    entry_widget.icursor(tk.END)

    # Valid if at least 4 digits follow the dash
    if re.fullmatch(r'^[A-Z]+-\d{4,}.*$', formatted):
        entry_widget.config(bg='lightgreen')
    else:
        entry_widget.config(bg='#FFCCDD')






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
                "POTA": ""
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
            "POTA": ""
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
            "Satellite": ""
        }
        new_format["Logbook"].append(new_entry)

    return new_format

# Function to load an existing JSON file
def load_json():
    global current_json_file, Logbook_Window
    
    # Check if a JSON file is already loaded
    if current_json_file:
        # Ask the user for confirmation
        confirm = messagebox.askyesno("Confirm", "A file is already loaded. Do you want to load a new file?")
        if not confirm:
            return  # User chose not to load a new file
        
        # Close the logbook window if it exists
        if Logbook_Window:
            Logbook_Window.destroy()  # Close the logbook window
            Logbook_Window = None  # Reset reference

    # Proceed to load a new file
    current_json_file = filedialog.askopenfilename(filetypes=[("MiniBook files", "*.mbk")])
    if current_json_file:

        # Load the JSON file
        try:
            with open(current_json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Check if the JSON data is in list format (old format)
                if isinstance(data, list):
                    # Ask user if they want to convert the old format
                    convert_confirm = messagebox.askyesno("Convert Old Format", "Old Logbook format detected! Do you want to convert it to the new format?")
                    if convert_confirm:
                        # Convert the data to the new format
                        data = convert_old_logbook(data)
                        
                        # Ask where to save the converted file
                        new_file_path = filedialog.asksaveasfilename(defaultextension=".mbk", filetypes=[("MiniBook files", "*.mbk")])
                        if new_file_path:
                            with open(new_file_path, 'w', encoding='utf-8') as new_file:
                                json.dump(data, new_file, indent=4)
                            messagebox.showinfo("Conversion Successful", "The logbook has been converted and saved to the new format.")
                            current_json_file = new_file_path
                            update_title(root, VERSION_NUMBER, current_json_file, radio_status_var.get())
                            reset_fields()  # Reset fields if needed
                            load_station_setup()
                            file_menu.entryconfig("Station setup", state="normal")
                        else:
                            messagebox.showinfo("Save Cancelled", "File was not saved.")
                            current_json_file = ""
                            no_file_loaded()
                    else:
                        current_json_file = ""
                        no_file_loaded()
                    return

                # Check if the JSON data is in dictionary format and has the correct structure
                elif isinstance(data, dict):
                    # Validate the expected structure
                    if "Station" in data and "Logbook" in data and isinstance(data["Logbook"], list):
                        station_info = data["Station"]
                        if ("Callsign" in station_info and "Locator" in station_info):
                            # Structure is correct; proceed with loading
                            update_title(root, VERSION_NUMBER, current_json_file, radio_status_var.get())
                            reset_fields()  # Reset fields if needed
                            load_station_setup()
                            file_menu.entryconfig("Station setup", state="normal")
                        else:
                            # Incorrect "Station" structure
                            messagebox.showerror("Invalid Format", "The 'Station' section is missing required fields.")
                            current_json_file = ""
                            no_file_loaded()
                    else:
                        # Incorrect dictionary structure
                        messagebox.showerror("Invalid Format", "File is not in the expected format.")
                        current_json_file = ""
                        no_file_loaded()

                if current_json_file:
                    # Save the last loaded file path to config
                    config.set('General', 'last_loaded_logbook', current_json_file)
                    file_path = DATA_FOLDER / CONFIG_FILE
                    with open(file_path, 'w') as configfile:
                        config.write(configfile)
                

        except Exception as e:
            print(f"Error reading MiniBook file: {e}")
            messagebox.showerror("Error", "Could not read the file. Please ensure it is a valid JSON.")
            current_json_file = ""
            no_file_loaded()


def load_json_content():
    global tree, qso_count_label, qso_lines

    # Clear the Treeview
    tree.delete(*tree.get_children())

    if tree is None:
        return    

    # Read the JSON file
    try:
        with open(current_json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            qso_lines = data.get("Logbook", [])
    except Exception as e:
        print(f"Error reading MiniBook file: {e}")
        return

    # Clear any existing entries in the Treeview
    tree.delete(*tree.get_children())

    if not qso_lines:
        # No QSO entries found, update count label and return
        qso_count_label.config(text="Total of 0 QSO's in logbook")
        print("No QSO entries found in the MiniBook file.")
        return

    # Prepare and sort QSO lines by date and time
    try:
        # Combine Date and Time into a single datetime object for sorting
        for qso in qso_lines:
            qso['DateTime'] = datetime.strptime(
                f"{qso['Date']} {qso['Time']}", '%Y-%m-%d %H:%M:%S'
            ) if qso['Time'] else datetime.strptime(qso['Date'], '%Y-%m-%d')

        # Sort QSO lines by the new DateTime key in descending order
        qso_lines.sort(key=lambda x: x['DateTime'], reverse=True)

        # Populate the Treeview with sorted QSO data
        row_color = True
        qso_counter = 0

        for qso in qso_lines:
            qso_counter += 1
            tag = 'oddrow' if row_color else 'evenrow'
            row_color = not row_color

            # Insert sorted data into the Treeview
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
                qso.get('My Callsign', ''),
                qso.get('My Operator', ''),
                qso.get('My Locator', ''),
                qso.get('My Location', ''),
                qso.get('My WWFF', ''),
                qso.get('My POTA', ''),
                qso.get('Satellite', '')
            ), tags=(tag,))

        # Update QSO count label
        qso_count_label.config(text=f"Total of {qso_counter} QSO's in logbook")

        # Define row colors
        tree.tag_configure("oddrow", background="lightblue")
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
    columns = ('Date', 'Time', 'Callsign', 'Name', 'Country', 'Sent', 'Received', 'Mode', 'Submode','Band', 'Frequency', 'Locator', 'Comment', 'WWFF', 'POTA', 'My Callsign', 'My Operator', 'My Locator', 'My Location', 'My WWFF', 'My POTA')

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
        selectmode='extended',  # <-- zorgt voor multi-select
        xscrollcommand=x_scrollbar.set, 
        yscrollcommand=y_scrollbar.set
    )
    tree.pack(fill='both', expand=True)


    # Right-click context menu for editing QSO
    def show_context_menu(event):
        item = tree.identify_row(event.y)
        if item:
            # Voeg toe aan selectie als nog niet geselecteerd
            if item not in tree.selection():
                tree.selection_add(item)

            selected_items = tree.selection()

            # Alleen "Edit QSO" tonen als precies 1 regel geselecteerd is
            if len(selected_items) == 1:
                context_menu.entryconfig("Edit QSO", state="normal")
            else:
                context_menu.entryconfig("Edit QSO", state="disabled")

            context_menu.post(event.x_root, event.y_root)



    def edit_qso_from_menu():
        # Open the QSO edit window (you can call your edit QSO function here)
        edit_qso(edit_qso)  # Call the edit function with the selected QSO

    # Function to delete QSO from the menu
    def delete_qso_from_menu():
        global qso_lines

        selected_items = tree.selection()
        if selected_items:
            confirm = messagebox.askyesno("Delete QSO(s)", f"Are you sure you want to delete {len(selected_items)} selected QSO(s)?")
            if confirm:
                # Verwijder uit qso_lines op basis van Date, Time en Callsign
                identifiers_to_delete = []
                for item in selected_items:
                    values = tree.item(item)['values']
                    identifiers_to_delete.append((values[0], values[1], values[2]))  # Date, Time, Callsign

                qso_lines = [
                    qso for qso in qso_lines
                    if (qso.get("Date"), qso.get("Time"), qso.get("Callsign")) not in identifiers_to_delete
                ]

                # Verwijder uit TreeView
                for item in selected_items:
                    tree.delete(item)

                save_to_json()
                load_json_content()  # Refresh the tree
                update_worked_before_tree()


    # Create a context menu
    context_menu = tk.Menu(Logbook_Window, tearoff=0)
    context_menu.add_command(label="Edit QSO", command=edit_qso_from_menu)
    context_menu.add_command(label="Delete QSO('s)", command=delete_qso_from_menu)

    # Bind the right-click event to show the context menu
    tree.bind("<Button-3>", show_context_menu)
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
        'My Callsign': 80,
        'My Operator': 80,
        'My Locator': 70,
        'My Location': 120,
        'My WWFF': 50,
        'My POTA': 50,
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
        tree.tag_configure('oddrow', background='lightblue')
        tree.tag_configure('evenrow', background='white')

    # Initial load of the JSON content
    load_json_content()  

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
                    qso.get('My Callsign', ''),
                    qso.get('My Operator', ''),
                    qso.get('My Locator', ''),
                    qso.get('My Location', ''),
                    qso.get('My WWFF', ''),
                    qso.get('My POTA', ''),
                    qso.get('Satellite', '')
                ), tags=('oddrow' if row_color else 'evenrow',))
                row_color = not row_color

            qso_count_label.config(text=f"Total QSO's: {len(matching_entries)}")  # Update the count label

    Logbook_Window.protocol("WM_DELETE_WINDOW", lambda: close_logbook())

    # Search button
    search_button = tk.Button(search_frame, text="Search", command=search_log)
    search_button.pack(pady=5, side='left')

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

    Logbook_Window.update_idletasks()
    logbook_x = Logbook_Window.winfo_x()
    logbook_y = Logbook_Window.winfo_y()
    logbook_width = Logbook_Window.winfo_width()
    logbook_height = Logbook_Window.winfo_height()
    edit_width = 550
    edit_height = 420
    edit_x = logbook_x + (logbook_width - edit_width) // 2
    edit_y = logbook_y + (logbook_height - edit_height) // 2
    Edit_Window.geometry(f"{edit_width}x{edit_height}+{edit_x}+{edit_y}")
    Edit_Window.grab_set()

    fields = ['Date', 'Time', 'Callsign', 'Name', 'Country', 'Sent', 'Received', 'Mode', 'Submode', 'Band', 'Frequency', 'Locator', 'Comment', 'WWFF', 'POTA', 'My Callsign', 'My Operator', 'My Locator', 'My Location', 'My WWFF', 'My POTA', 'Satellite']
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
            entry = ttk.Combobox(form_frame, values=list(band_to_frequency.keys()), state="readonly")
            entry.set(original_qso.get('Band', ''))

        elif field == 'Mode':
            entry = ttk.Combobox(form_frame, values=mode_options, state="readonly")
            entry.set(original_qso.get('Mode', ''))

        elif field == 'Submode':
            entry = ttk.Combobox(form_frame, values=submode_options, state="readonly")
            entry.set(original_qso.get('Submode', ''))

        elif field in ['Sent', 'Received']:
            entry = ttk.Combobox(form_frame, values=rst_options)
            entry.set(original_qso.get(field, ''))

        else:
            if field in ['WWFF', 'My WWFF']:
                var = tk.StringVar()
                var.set(original_qso.get(field, ''))
                entry = tk.Entry(form_frame, textvariable=var)
                entry.bind("<KeyRelease>", lambda e, w=entry, v=var: format_wwff_input(e, w, v))
            elif field in ['POTA', 'My POTA']:
                var = tk.StringVar()
                var.set(original_qso.get(field, ''))
                entry = tk.Entry(form_frame, textvariable=var)
                entry.bind("<KeyRelease>", lambda e, w=entry, v=var: format_pota_input(e, w, v))
            else:
                entry = tk.Entry(form_frame)
                entry.insert(0, original_qso.get(field, ''))

        entry.grid(row=row, column=col * 2 + 1, padx=5, pady=5, sticky='w')
        entries[field] = entry

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

        locator1 = original_qso['Locator'].strip()
        locator2 = original_qso['My Locator'].strip()

        if not is_valid_locator(locator1) or not is_valid_locator(locator2):
            messagebox.showerror("Invalid Locator", "The Maidenhead locator must be at least 4 characters and valid.\nExample: FN31 or FN31TK")
            return

        date_str = entries['Date'].get().strip()
        time_str = entries['Time'].get().strip()

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Date Format", "Date must be in the format: YYYY-MM-DD")
            return

        try:
            datetime.strptime(time_str, '%H:%M:%S')
        except ValueError:
            messagebox.showerror("Invalid Time Format", "Time must be in the format: HH:MM:SS")
            return

        for field in fields:
            if field not in ['Callsign', 'Mode', 'Band', 'Submode', 'Locator', 'My Locator', 'My Callsign']:
                original_qso[field] = entries[field].get().strip()

        original_qso['DateTime'] = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')

        save_to_json()
        load_json_content()
        close_edit_window()

    def delete_qso():
        if messagebox.askyesno("Delete Confirmation", "Are you sure you want to delete this QSO?"):
            global qso_lines
            qso_lines = [qso for qso in qso_lines if qso != original_qso]
            save_to_json()
            load_json_content()
            close_edit_window()

    button_frame = tk.Frame(Edit_Window)
    button_frame.pack(pady=10)

    save_button = tk.Button(button_frame, text="Save", command=save_changes, width=10)
    save_button.pack(side='left', padx=10)

    delete_button = tk.Button(button_frame, text="Delete", command=delete_qso, width=10)
    delete_button.pack(side='left', padx=10)

    close_button = tk.Button(button_frame, text="Close", command=close_edit_window, width=10)
    close_button.pack(side='left', padx=10)

    Edit_Window.protocol("WM_DELETE_WINDOW", close_edit_window)



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

    # Select ADIF file
    adif_file = filedialog.askopenfilename(title="Select ADIF File", filetypes=[("ADIF files", "*.adi"), ("All files", "*.*")])
    if not adif_file:
        return  # Exit if no file is selected

    # Load the currently loaded JSON logbook data
    try:
        with open(current_json_file, "r", encoding="utf-8") as json_file:
            logbook_data = json.load(json_file)
    except FileNotFoundError:
        messagebox.showerror("Error", "Logbook file not found.")
        return
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Logbook file is not valid JSON.")
        return

    # Attempt to read ADIF file with UTF-8 encoding
    try:
        with open(adif_file, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        # Fallback to Latin-1 encoding if UTF-8 fails
        try:
            with open(adif_file, "r", encoding="latin-1") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ADIF file: {e}")
            return

    # Split the content by "<EOR>" to separate each QSO record
    qso_records = content.split("<EOR>")

    # Gather all new entries and duplicates
    new_entries = []
    duplicates = []
    total_qso_count = len(qso_records)
    for record in qso_records:
        # Skip empty records
        if not record.strip():
            continue

        sig = extract_field(record, "sig").upper()
        sig_info = extract_field(record, "sig_info")

        # Determine if this is WWFF or POTA
        wwff = sig_info if sig == "WWFF" else ""
        pota = sig_info if sig == "POTA" else ""

        # Extract QSO fields
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
            "Satellite": extract_field(record, "sat_name") or ""
        }

        # Check if "my_sig" field exists and contains "POTA"
        if extract_field(record, "my_sig") == "POTA":
            entry["My POTA"] = extract_field(record, "my_sig_info") or ""

        # Check and update country and continent based on callsign
        callsign = entry["Callsign"]
        check_callsign_prefix(callsign, False)
        if country_var:
            entry["Country"] = country_var
        if continent_var:
            entry["Continent"] = continent_var

        # Only add entry if the callsign is present
        if entry["Callsign"]:
            # Check for duplicates in logbook, ensuring uppercase comparison
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

    # Ask user action for duplicates if any are found
    added_count = len(new_entries)
    if duplicates:
        duplicate_count = len(duplicates)
        action = custom_duplicate_dialog(parent=root, total_count=total_qso_count, duplicate_count=duplicate_count, added_count=added_count)
        
        if action is None:
            return  # Cancel import if dialog is closed without action
        elif action == "Overwrite":
            for duplicate_entry in duplicates:
                for idx, existing_entry in enumerate(logbook_data["Logbook"]):
                    if (existing_entry["Callsign"] == duplicate_entry["Callsign"] and
                        existing_entry["Date"] == duplicate_entry["Date"] and
                        existing_entry["Time"] == duplicate_entry["Time"]):
                        logbook_data["Logbook"][idx] = duplicate_entry
                        break
        elif action == "Ignore":
            # Count how many were ignored
            ignored_count = len(new_entries)
            new_entries = []  # Clear the new entries, as we ignore duplicates
        elif action == "Add":
            new_entries.extend(duplicates)
            added_count = duplicate_count

    # Add all new (non-duplicate) entries
    logbook_data["Logbook"].extend(new_entries)

    # Save the updated JSON logbook
    with open(current_json_file, "w", encoding="utf-8") as json_file:
        json.dump(logbook_data, json_file, indent=4)

    # Update the logbook window if it is open
    for window in root.winfo_children():
        if isinstance(window, tk.Toplevel) and hasattr(window, 'update_logbook'):
            window.update_logbook()

    # After importing ADIF and processing QSOs
    if duplicates:        
        if action:
            messagebox.showinfo("Import ADIF", f"{duplicate_count} duplicate QSO(s) processed. "
                                              f"{added_count} new QSO(s) added to the logbook.")
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
                my_pota = escape_invalid_characters(qso.get('My POTA', ''))
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
                    wwff_pota = "WWFF"
                    adif_record.append(f"<sig:{len(wwff_pota)}>{wwff_pota}")
                    adif_record.append(f"<sig_info:{len(wwff)}>{wwff}")                    
                elif log_type == "POTA" and pota:
                    wwff_pota = "POTA"
                    adif_record.append(f"<sig:{len(wwff_pota)}>{wwff_pota}")
                    adif_record.append(f"<sig_info:{len(pota)}>{pota}")
                    adif_record.append(f"<my_sig:{len(wwff_pota)}>{wwff_pota}")
                    adif_record.append(f"<my_sig_info:{len(my_pota)}>{my_pota}") 

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


    # Get the values from the input fields and combo boxes
    date = date_var.get()
    time = time_var.get()
    callsign = callsign_var.get().strip()
    name = name_var.get().strip()
    if not callsign:
        messagebox.showwarning("Warning", "Log may not be empty!")
        reset_fields()
        return
    my_callsign = my_callsign_var.get().upper()
    my_operator = my_operator_var.get().upper()
    my_locator = my_locator_var.get().upper()
    my_location = my_location_var.get()
    my_wwff = my_wwff_var.get()
    my_pota = my_pota_var.get()
    country = country_var
    continent = continent_var
    rst_sent = rst_sent_var.get()
    rst_received = rst_received_var.get()
    band = band_var.get()
    mode = mode_var.get()
    submode = submode_var.get()
    comment = comment_var.get().strip()
    wwff = wwff_var.get().strip()
    pota = pota_var.get().strip()
    satellite = satellite_var.get().strip()

    # Set WWFF_POTA: prefer WWFF over POTA
    if wwff:
        wwff_pota = "WWFF"
    elif pota:
        wwff_pota = "POTA"
    else:
        wwff_pota = ""

    
    # Frequency input validation
    if not frequency_var.get():
        frequency = ""
    else:
        try:
            frequency = f"{float(frequency_var.get()):.6f}"
        except ValueError:
            messagebox.showerror("Invalid input", "Enter a valid decimal number for the frequency.")
            return
    
    locator = locator_var.get().strip()

    # Validate locator field
    if not is_valid_locator(locator):
        messagebox.showerror("Invalid Locator", "The Maidenhead locator must be at least 4 characters and valid.\nExample: FN31 or FN31TK")
        return

    # Create a dictionary for the QSO data
    qso_entry = {
        "Date": date,
        "Time": time,
        "Callsign": callsign,
        "Name": name,
        "My Callsign": my_callsign,
        "My Operator": my_operator,
        "My Locator": my_locator,
        "My Location": my_location,
        "My WWFF": my_wwff,
        "My POTA": my_pota,
        "Country": country,
        "Continent": continent,
        "Sent": rst_sent,
        "Received": rst_received,
        "Mode": mode,
        "Submode": submode,
        "Band": band,
        "Frequency": frequency,
        "Locator": locator,
        "Comment": comment,
        "WWFF": wwff,
        "POTA": pota,
        "Satellite": satellite
    }

    # Add entry to JSON-file
    try:
        with open(current_json_file, 'r+', encoding='utf-8') as file:
            # Load existing data or create default structure
            try:
                json_data = json.load(file)
            except json.JSONDecodeError:
                json_data = {"Station": {}, "Logbook": []}

            # Ensure "Station" and "Logbook" keys exist in the JSON structure
            json_data.setdefault("Station", {})
            json_data.setdefault("Logbook", [])

            # Add new QSO entry to "Logbook"
            json_data["Logbook"].append(qso_entry)

            # Write the updated data back to the file
            file.seek(0)
            json.dump(json_data, file, ensure_ascii=False, indent=4)
            file.truncate()  # Ensure no old data remains in the file
            
            # Reset input fields and update last QSO label
            reset_fields()
            last_qso_label.config(text=f"Last QSO: {callsign} at {time_var.get()}")    

            # Update the logbook window if it is open
            for window in root.winfo_children():
                if isinstance(window, tk.Toplevel) and hasattr(window, 'update_logbook'):
                    window.update_logbook()  

    except Exception as e:
        messagebox.showerror("Error", f"Failed to log QSO entry: {e}")




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
        "Satellite": extract_field(adif_record, "sat_name") or ""
    }


    # Debug: Show the processed QSO input
#    print(f"QSO-input processed {qso_entry}")

    # Update the country field based on the callsign
    check_callsign_prefix(callsign, update_ui=False)  # Disable UI update to prevent excessive updates
    qso_entry["Country"] = country_var  # Set the updated country

    # Add the QSO entry to the logbook
    add_qso_to_logbook(qso_entry)
           

def add_qso_to_logbook(qso_entry):
    """
    Add a QSO entry directly to the loaded logbook and update the logbook window if open.
    """
    global current_json_file

    try:
        with open(current_json_file, "r+", encoding="utf-8") as file:
            # Load existing logbook data
            try:
                json_data = json.load(file)
            except json.JSONDecodeError:
                json_data = {"Station": {}, "Logbook": []}

            # Ensure the "Logbook" key exists
            json_data.setdefault("Logbook", [])

            # Add the new QSO entry
            json_data["Logbook"].append(qso_entry)

            # Save the updated logbook
            file.seek(0)
            json.dump(json_data, file, ensure_ascii=False, indent=4)
            file.truncate()

            # Update the last QSO label
            last_qso_label.config(text=f"Last QSO: {qso_entry['Callsign']} at {qso_entry['Time']}")

            # Update the logbook window in the main thread
            for window in root.winfo_children():
                if isinstance(window, tk.Toplevel) and hasattr(window, 'update_logbook'):
                    root.after(0, window.update_logbook)  # Schedule the update on the main thread

            # Toon een succesmelding
            show_auto_close_messagebox("MiniBook", f"Succes!\n\nQSO with {qso_entry['Callsign']} at {qso_entry['Time']} successfully added!", duration=3000)

    except Exception as e:
        show_auto_close_messagebox("MiniBook", f"Error!\n\nFailed to log QSO: {e}", duration=3000)

def show_auto_close_messagebox(title, message, duration=2000):
    def _show():
        temp_root = tk.Toplevel(root)
        temp_root.title(title)
        temp_root.geometry("300x150")
        temp_root.resizable(False, False)
        temp_root.attributes("-topmost", True)
        temp_root.overrideredirect(True)

        # Bereken middenpositie
        root.update_idletasks()
        root_x = root.winfo_rootx()
        root_y = root.winfo_rooty()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        x = root_x + (root_width - 300) // 2
        y = root_y + (root_height - 150) // 2
        temp_root.geometry(f"300x150+{x}+{y}")

        # Border-frame
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
        server_ip = external_server_ip.get()
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
        server_ip = external_server_ip.get()
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
    print(f"Error code: {error_code}")
    error_messages = {
        -5: "I/O error (communication failure).",
        -7: "Lost connection",
        -8: "Communication timed out with the radio.",
        -9: "Invalid command or parameter sent to the radio.",
        -10: "Radio not present or unable to communicate.",
        -11: "Command rejected by the radio.",
    }

    # Optionally terminate the connection on critical errors
    if error_code in [-5, -7, -8, -9, -10, -11]:
        disconnect_from_hamlib()
        
    # Get the error message or fallback to a generic message
    error_message = error_messages.get(error_code, f"Unknown hamlib error (RPRT {error_code}).")
    messagebox.showerror("hamlib Error", error_message)





# Function to update frequency and mode
stop_frequency_thread = threading.Event()  # Event to stop the thread

def update_frequency_and_mode_thread():
    global frequency_var, frequency_mhz, serial_port
    last_mode = None

    while not stop_frequency_thread.is_set():

        # Safely check socket_connection
        if socket_connection is None:
            print("Socket connection is None; exiting thread.")
            break  # Exit the loop if the socket is invalid

        try:
            # Request frequency
            socket_connection.sendall(b"f\n")  # Safely use socket_connection
            frequency_hz = socket_connection.recv(1024).decode().strip()

            # Check for RPRT x error codes in frequency response
            if frequency_hz.startswith("RPRT"):
                handle_rprtx_error(int(frequency_hz.split()[1]))
                break  # Stop further processing if there's an error

            # Convert frequency from Hz to MHz with 3 decimal places
            frequency_mhz = float(frequency_hz) / 1_000_000
            frequency_var.set(f"{frequency_mhz:.3f}")

            # Check socket validity again before sending another request
            if socket_connection is None:
                print("Socket connection became None; exiting thread.")
                break

            # Request mode and filter
            socket_connection.sendall(b"m\n")  # Safely use socket_connection
            mode_response = socket_connection.recv(1024).decode().strip()

            # Check for RPRT x error codes in mode response
            if mode_response.startswith("RPRT"):
                handle_rprtx_error(int(mode_response.split()[1]))
                break  # Stop further processing if there's an error

            # Parse mode and filter
            mode, filter_value = mode_response.split() if ' ' in mode_response else (mode_response, "N/A")
            matching_modes = {
                'USB', 'LSB', 'CW', 'CWR', 'RTTY', 'RTTYR', 'AM', 'FM', 'WFM', 'AMS', 
                'PKTLSB', 'PKTUSB', 'PKTFM', 'ECSSUSB', 'ECSSLSB', 'FA', 'SAM', 'SAL', 'SAH', 'DSB'
            }
            filtered_mode = next((m for m in matching_modes if mode.startswith(m)), "No Match")
            # Check if the mode has changed
            if filtered_mode != last_mode:
                last_mode = filtered_mode       # Update the last_mode
                mode_var.set(filtered_mode)     # Update the variable
                on_mode_change()                # Only call if changed!


        except AttributeError:
            print("Socket connection was None during operation.")
            break  # Exit if the socket becomes invalid

        except socket.error as e:
            messagebox.showerror("Error", f"Socket communication error: {e}")
            disconnect_from_hamlib()
            break

        # Wait before the next update (polling interval in seconds)
        #time.sleep(1.0)  # Adjust this delay as needed







#########################################################################################
#  __  __ ___ _  _ _   _ _ ___ 
# |  \/  | __| \| | | | ( ) __|
# | |\/| | _|| .` | |_| |/\__ \
# |_|  |_|___|_|\_|\___/  |___/
#
#########################################################################################                              

# Function for Station Setup menu
def open_station_setup():
    global Station_Setup_Window
    # Check if the window is already open
    if Station_Setup_Window is not None and Station_Setup_Window.winfo_exists():
        Station_Setup_Window.lift()  # Bring the existing window to the front
        return    

    Station_Setup_Window = tk.Toplevel(root)
    Station_Setup_Window.title("Station Setup")
    Station_Setup_Window.resizable(False, False)

    # Center the Station_Setup_Window relative to root
    Station_Setup_Window.update_idletasks()  # Zorg dat afmetingen bekend zijn
    w = Station_Setup_Window.winfo_width()

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()

    x = root_x + (root_w // 2) - (w // 2)
    y = root_y  # zelfde top als root

    Station_Setup_Window.geometry(f"+{x}+{y}") 

    # Save original values to restore on cancel
    original_callsign   = my_callsign_var.get()
    original_locator    = my_locator_var.get()
    original_location   = my_location_var.get()
    original_operator   = my_operator_var.get()
    original_pota       = my_pota_var.get()
    original_wwff       = my_wwff_var.get()
  
    tk.Label(Station_Setup_Window, text="Station Setup", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan="2", padx=10, pady=1)


    my_callsign_var.trace("w", lambda *args: my_callsign_var.set(my_callsign_var.get().upper()))
    # Label & Entry for My Callsign
    tk.Label(Station_Setup_Window, text="Callsign:", font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=1, sticky='w')
    tk.Entry(Station_Setup_Window, textvariable=my_callsign_var, font=('Arial', 10, 'bold')).grid(row=1, column=1, padx=10, pady=5, sticky='w')

    my_operator_var.trace("w", lambda *args: my_operator_var.set(my_operator_var.get().upper()))
    # Label & Entry for My Operator
    tk.Label(Station_Setup_Window, text="Operator:", font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=1, sticky='w')
    tk.Entry(Station_Setup_Window, textvariable=my_operator_var, font=('Arial', 10, 'bold')).grid(row=2, column=1, padx=10, pady=5, sticky='w')

    my_locator_var.trace("w", lambda *args: my_locator_var.set(my_locator_var.get().upper()))
    # Label & Entry for My Locator
    tk.Label(Station_Setup_Window, text="Locator:", font=('Arial', 10)).grid(row=3, column=0, padx=10, pady=1, sticky='w')
    tk.Entry(Station_Setup_Window, textvariable=my_locator_var, font=('Arial', 10, 'bold')).grid(row=3, column=1, padx=10, pady=5, sticky='w')

    # Label & Entry for My Location
    tk.Label(Station_Setup_Window, text="Location:", font=('Arial', 10)).grid(row=4, column=0, padx=10, pady=1, sticky='w')
    tk.Entry(Station_Setup_Window, textvariable=my_location_var, font=('Arial', 10, 'bold')).grid(row=4, column=1, padx=10, pady=5, sticky='w')    

    # Label & Entry for My POTA
    tk.Label(Station_Setup_Window, text="POTA No.:", font=('Arial', 10)).grid(row=5, column=0, padx=10, pady=1, sticky='w')
    my_pota_entry = tk.Entry(Station_Setup_Window, textvariable=my_pota_var, font=('Arial', 10, 'bold'))
    my_pota_entry.grid(row=5, column=1, padx=10, pady=5, sticky='w')    
    my_pota_entry.bind("<KeyRelease>", lambda event: format_pota_input(event, my_pota_entry, my_pota_var))

    # Label & Entry for My WWFF
    tk.Label(Station_Setup_Window, text="Flora Fauna No.:", font=('Arial', 10)).grid(row=6, column=0, padx=10, pady=1, sticky='w')
    my_wwff_entry = tk.Entry(Station_Setup_Window, textvariable=my_wwff_var, font=('Arial', 10, 'bold'))
    my_wwff_entry.grid(row=6, column=1, padx=10, pady=5, sticky='w')    
    my_wwff_entry.bind("<KeyRelease>", lambda event: format_wwff_input(event, my_wwff_entry, my_wwff_var))


    def close_window():
        global Station_Setup_Window
        Station_Setup_Window.destroy()
        Station_Setup_Window = None

    # Save button
    def save_setup():
        locator = my_locator_var.get().strip()

        # Validate locator field
        if not is_valid_locator(locator):
            messagebox.showerror("Invalid Locator", "The Maidenhead locator must be at least 4 characters and valid.\nExample: FN31 or FN31TK")
            return
        else:
            save_station_setup()
            close_window()

    def cancel_setup():
        my_callsign_var.set(original_callsign)
        my_locator_var.set(original_locator)
        my_location_var.set(original_location)
        my_operator_var.set(original_operator)
        my_pota_var.set(original_pota)        
        my_wwff_var.set(original_wwff)
        close_window()

    tk.Button(Station_Setup_Window, text="Save & Exit", command=save_setup, width=10, height=2).grid(row=20, column=0, columnspan=2, padx=20, pady=10, sticky="w")
    tk.Button(Station_Setup_Window, text="Cancel", command=cancel_setup, width=10, height=2).grid(row=20, column=0, columnspan=2, padx=20, pady=10, sticky="e")
    
    # Handle window close event
    Station_Setup_Window.protocol("WM_DELETE_WINDOW", close_window)




# Function for Preference menu
def open_preferences():
    global Preference_Window, utc_offset_var, external_server_ip, server_port_var

    # Check if the window is already open
    if Preference_Window is not None and Preference_Window.winfo_exists():
        Preference_Window.lift()  # Bring the existing window to the front
        return

    Preference_Window = tk.Toplevel(root)
    Preference_Window.title("Preferences")
    Preference_Window.resizable(False, False)

    # Center the Preference Window relative to root
    Preference_Window.update_idletasks()  # Zorg dat afmetingen bekend zijn
    w = Preference_Window.winfo_width()

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()

    x = root_x + (root_w // 2) - (w // 2)
    y = root_y  # zelfde top als root

    Preference_Window.geometry(f"+{x}+{y}")     

    # Load saved radio settings
    server_port_var     = tk.StringVar(value=config.get('hamlib_settings', 'hamlib_port', fallback=4532))
    external_server_ip  = tk.StringVar(value=config.get('hamlib_settings', 'hamlib_ip', fallback="127.0.0.1"))
    wsjtx_port          = config.get('Wsjtx_settings', 'wsjtx_port', fallback="2333")


    tk.Label(Preference_Window, text="Reload last logbook on startup", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan="2", padx=10, pady=1)

    # Reload Last Logbook Checkbox
    tk.Label(Preference_Window, text="Enable Reload:").grid(row=1, column=0, sticky="w", padx=10, pady=1)
    reload_last_logbook_var = tk.BooleanVar(value=config.getboolean('General', 'reload_last_logbook', fallback=False))
    reload_last_logbook_checkbox = tk.Checkbutton(
        Preference_Window,
        variable=reload_last_logbook_var
    )
    reload_last_logbook_checkbox.grid(row=1, column=1, sticky="w", padx=10, pady=1)

    # Add horizontal line
    separator = ttk.Separator(Preference_Window, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=5)

    tk.Label(Preference_Window, text="UTC Time offset", font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan="2", padx=10, pady=1)

    # Label & Dropdown for UTC offset
    tk.Label(Preference_Window, text="Offset (Hours):").grid(row=4, column=0, padx=10, pady=1, sticky='w')
    utc_offset_var = tk.StringVar(value=config.get('Global_settings', 'utc_offset', fallback='0'))
    utc_offset_menu = ttk.Combobox(Preference_Window, textvariable=utc_offset_var, values=[str(i) for i in range(-12, 13)])
    utc_offset_menu.grid(row=4, column=1, padx=10, pady=1, sticky='w')
    utc_offset_var.trace_add('write', lambda *args: update_datetime())    

    # Add horizontal line
    separator = ttk.Separator(Preference_Window, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky='ew', padx=10, pady=5)

    tk.Label(Preference_Window, text="Hamlib Setup", font=('Arial', 10, 'bold')).grid(row=6, column=0, columnspan="2", padx=10, pady=1)

    # hamlib Server port
    tk.Label(Preference_Window, text="Port:").grid(row=7, column=0, padx=10, pady=1, sticky='w')
    server_port_var = tk.StringVar(value=config.get('hamlib_settings', 'hamlib_port', fallback=4532))
    server_port_frame = tk.Frame(Preference_Window)
    for value in ["4532", "4536", "4538", "4540"]:
        tk.Radiobutton(server_port_frame, text=value, variable=server_port_var, value=value).pack(side=tk.LEFT)
    server_port_frame.grid(row=7, column=1, padx=10, pady=1, sticky='w')
            

   # Remote hamlib server settings
    tk.Label(Preference_Window, text="IP-address:").grid(row=9, column=0, sticky="w", padx=10, pady=1)
    ip_entry = tk.Entry(Preference_Window, textvariable=external_server_ip)
    ip_entry.grid(row=9, column=1, padx=10, pady=1, sticky="w")
    ip_entry.configure(state="normal")

    separator = ttk.Separator(Preference_Window, orient='horizontal').grid(row=31, column=0, columnspan=2, sticky='ew', padx=10, pady=5)

    tk.Label(Preference_Window, text="QSO Reception using UDP (WSJT-X)", font=('Arial', 10, 'bold')).grid(row=40, column=0, columnspan="2", padx=10, pady=1)    

    # WSJT-X PORT
    wsjtx_port_var = tk.StringVar(value=wsjtx_port)
    tk.Label(Preference_Window, text="Port:").grid(row=41, column=0, padx=10, pady=1, sticky='e')
    wsjtx_port_entry = tk.Entry(Preference_Window, textvariable=wsjtx_port_var, width=10)
    wsjtx_port_entry.grid(row=41, column=1, padx=10, pady=1, sticky='w')

    separator = ttk.Separator(Preference_Window, orient='horizontal').grid(row=50, column=0, columnspan=2, sticky='ew', padx=10, pady=5)

    tk.Label(Preference_Window, text="QRZ Lookup Credentials", font=('Arial', 10, 'bold')).grid(row=51, column=0, columnspan="2", padx=10, pady=1)    

    tk.Label(Preference_Window, text="Username:").grid(row=52, column=0, sticky="e", padx=10, pady=1)
    tk.Label(Preference_Window, text="Password:").grid(row=53, column=0, sticky="e", padx=10, pady=1)
    qrz_username_var = tk.StringVar(value=config.get("QRZ", "username", fallback=""))
    qrz_password_var = tk.StringVar(value=config.get("QRZ", "password", fallback=""))

    tk.Entry(Preference_Window, textvariable=qrz_username_var).grid(row=52, column=1, padx=10, pady=1, sticky='w')
    tk.Entry(Preference_Window, textvariable=qrz_password_var, show="*").grid(row=53, column=1, padx=10, pady=1, sticky='w')    

    # Checks if IP address is valid
    def is_valid_ip(ip):
        try:
            # Try creating an IP address object
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            # If a ValueError is raised, the IP is not valid
            return False

    # Checks if Port is valid
    def is_valid_port(port):
        try:
            port = int(port)
            return 0 <= port <= 65535
        except (ValueError, TypeError):
            return False

    # Main validation function
    def value_check():
        # Check if the port is valid
        if is_valid_port(wsjtx_port_var.get()):
            pass  # Valid port, proceed to next check
        else:
            messagebox.showerror("Error", f"{wsjtx_port_var.get()} is an invalid port.")
            return
        
        # Check if the IP is valid
        if is_valid_ip(external_server_ip.get()):
            pass  # Valid IP, proceed to save preferences
        else:
            messagebox.showerror("Error", f"{external_server_ip.get()} is an invalid IP address.")
            return
        
        save_preferences() # If both are valid, save preferences
    
    def close_window():
        global Preference_Window
        Preference_Window.destroy()
        Preference_Window = None

    # Save button
    def save_preferences():
         
        # Only save the 'reload_last_logbook' if the key exists in the config
        if 'reload_last_logbook' in config['General']:
            # Save Reload Last Logbook preference only if a logbook is loaded
            if current_json_file:
                config['General']['reload_last_logbook'] = str(reload_last_logbook_var.get())
            else:
                # Ensure the setting is reset if no logbook is loaded
                config['General']['reload_last_logbook'] = "False"
        config['Global_settings']['utc_offset'] = utc_offset_var.get()
        config['hamlib_settings']['hamlib_port'] = server_port_var.get()
        config['hamlib_settings']['hamlib_ip'] = external_server_ip.get()
        config["Wsjtx_settings"]['wsjtx_port'] = str(wsjtx_port_var.get())

        # Save QRZ credentials in same structure
        if 'QRZ' not in config:
            config.add_section('QRZ')
        if qrz_username_var.get().strip():
            config['QRZ']['username'] = qrz_username_var.get().strip()
        if qrz_password_var.get().strip():
            config['QRZ']['password'] = qrz_password_var.get().strip()

        
        file_path = DATA_FOLDER / CONFIG_FILE
        with open(file_path, 'w') as configfile:
            config.write(configfile)        
        
        update_datetime()
        disconnect_from_hamlib()
        restart_listener(config)
        close_window()

    def cancel_preferences():
        close_window()

    separator = ttk.Separator(Preference_Window, orient='horizontal').grid(row=60, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
    
    tk.Button(Preference_Window, text="Save & Exit", command=value_check, width=10, height=2).grid(row=61, column=0, columnspan=2, padx=20, pady=10, sticky="w")
    tk.Button(Preference_Window, text="Cancel", command=cancel_preferences, width=10, height=2).grid(row=61, column=0, columnspan=2, padx=20, pady=10, sticky="e")

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
    file_path = DATA_FOLDER / CONFIG_FILE

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

                my_operator_label.config(textvariable=my_operator_var)
                my_callsign_label.config(textvariable=my_callsign_var)
                my_locator_label.config(textvariable=my_locator_var)
                my_location_label.config(textvariable=my_location_var)
                my_wwff_label.config(textvariable=my_wwff_var)
                my_pota_label.config(textvariable=my_pota_var)

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
                    "POTA": my_pota_var.get()
                }

                # Write back to the JSON file
                file.seek(0)
                json.dump(json_data, file, ensure_ascii=False, indent=4)
                file.truncate()  # Ensures no leftover data in the file
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save station details to logbook: {e}")






def load_last_logbook_on_startup():
    global current_json_file, Logbook_Window, tree

    # Check if the feature is enabled
    reload_last = config.getboolean('General', 'reload_last_logbook', fallback=False)
    last_logbook = config.get('General', 'last_loaded_logbook', fallback="")

    if reload_last and last_logbook and os.path.exists(last_logbook):
        current_json_file = last_logbook
        try:
            # Ensure log viewer window and tree are initialized
            if not Logbook_Window or not Logbook_Window.winfo_exists():
                view_logbook()  # Initialize the log viewer window and tree

            # Load the logbook content
            with open(current_json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if "Station" in data and "Logbook" in data and isinstance(data["Logbook"], list):
                    update_title(root, VERSION_NUMBER, current_json_file, radio_status_var.get())
                    load_json_content()  # Populate the log viewer with content
                    load_station_setup()
                    file_menu.entryconfig("Station setup", state="normal")                    
                else:
                    messagebox.showerror("Invalid Format", "The last logbook file has an invalid structure.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load the last logbook file: {e}")
    elif reload_last and not os.path.exists(last_logbook):
        messagebox.showwarning("File Not Found", "The last logbook file could not be found.")











#########################################################################################
#   ___  ___  ____  _    ___   ___  _  ___   _ ___ 
#  / _ \| _ \|_  / | |  / _ \ / _ \| |/ / | | | _ \
# | (_) |   / / /  | |_| (_) | (_) | ' <| |_| |  _/
#  \__\_\_|_\/___| |____\___/ \___/|_|\_\\___/|_|  
##
#########################################################################################

def locator_to_latlon(locator):
    if len(locator) < 4:
        raise ValueError("Locator must be at least 4 characters.")
    locator = locator.upper()
    lon = (ord(locator[0]) - ord('A')) * 20 - 180 + (int(locator[2]) * 2) + 1
    lat = (ord(locator[1]) - ord('A')) * 10 - 90 + (int(locator[3]) * 1) + 0.5
    if len(locator) >= 6:
        lon += (ord(locator[4]) - ord('A')) * 5.0 / 60 + 2.5 / 60
        lat += (ord(locator[5]) - ord('A')) * 2.5 / 60 + 1.25 / 60
    return lat, lon

def calculate_azimuth(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.atan2(x, y)
    return (math.degrees(bearing) + 360) % 360

def get_session_key(username, password):
    encoded_username = urllib.parse.quote(username)
    encoded_password = urllib.parse.quote(password)
    url = f"https://xmldata.qrz.com/xml/current/?username={encoded_username}&password={encoded_password}"

    try:
        response = requests.get(url, timeout=5)
        print("Login XML:\n", response.text)
    except requests.exceptions.RequestException:
        print("⚠️ No internet connection")
        return None, None

    root = ET.fromstring(response.content)
    ns = {"qrz": "http://xmldata.qrz.com"}

    key = root.findtext(".//qrz:Key", namespaces=ns)
    if not key:
        key_element = root.find(".//{http://xmldata.qrz.com}Key")
        if key_element is not None:
            key = key_element.text

    error = root.findtext(".//qrz:Error", namespaces=ns)
    return key, error

def query_callsign(session_key, callsign):
    def do_query(cs):
        url = f"https://xmldata.qrz.com/xml/current/?s={session_key}&callsign={cs}"
        try:
            response = requests.get(url, timeout=5)
            print(f"Raw XML for {cs}:\n", response.text)
        except requests.exceptions.RequestException:
            return {}
        root = ET.fromstring(response.content)
        ns = {"qrz": "http://xmldata.qrz.com"}
        return root.find(".//qrz:Callsign", ns)

    callsign_element = do_query(callsign)

    # If lookup fails, try without prefix/suffix
    if callsign_element is None and ("/" in callsign):
        parts = callsign.split("/")
        if len(parts) == 2:
            base_callsign = parts[1] if len(parts[1]) >= len(parts[0]) else parts[0]
            print(f"🔁 Falling back to base callsign: {base_callsign}")
            callsign_element = do_query(base_callsign)

    if callsign_element is None:
        print("⚠️ No Callsign element found in XML!")
        return {}

    ns = {"qrz": "http://xmldata.qrz.com"}
    lat = callsign_element.findtext("qrz:lat", default="", namespaces=ns)
    lon = callsign_element.findtext("qrz:lon", default="", namespaces=ns)
    maps_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else ""

    data = {
        "callsign": callsign_element.findtext("qrz:call", default="", namespaces=ns),
        "name": f"{callsign_element.findtext('qrz:fname', default='', namespaces=ns)} {callsign_element.findtext('qrz:name', default='', namespaces=ns)}".strip(),
        "address": callsign_element.findtext("qrz:addr1", default="", namespaces=ns),
        "city": callsign_element.findtext("qrz:addr2", default="", namespaces=ns),
        "zipcode": callsign_element.findtext("qrz:zip", default="", namespaces=ns),
        "province": callsign_element.findtext("qrz:state", default="", namespaces=ns),
        "country": callsign_element.findtext("qrz:country", default="", namespaces=ns),
        "email": callsign_element.findtext("qrz:email", default="", namespaces=ns),
        "grid": callsign_element.findtext("qrz:grid", default="", namespaces=ns),
        "cq_zone": callsign_element.findtext("qrz:cqzone", default="", namespaces=ns),
        "itu_zone": callsign_element.findtext("qrz:ituzone", default="", namespaces=ns),
        "qslmgr": callsign_element.findtext("qrz:qslmgr", default="", namespaces=ns),
        "lat": lat,
        "lon": lon,
        "mapslink": maps_link,
    }
    return data

def on_query():
    username = config.get("QRZ", "username", fallback="").strip()
    password = config.get("QRZ", "password", fallback="").strip()
    callsign = callsign_var.get().strip()

    if not username or not password:
        messagebox.showerror("Missing Credentials", "QRZ username/password not found in config.ini")
        return

    if not callsign:
        return

    session_key, error = get_session_key(username, password)

    if not session_key:
        if error:
            if "Invalid" in error or "incorrect" in error.lower() or "not authorized" in error.lower():
                messagebox.showerror("QRZ Login Failed", "Username or password incorrect.")
            else:
                messagebox.showerror("Connection Error", error)
        return

    data = query_callsign(session_key, callsign)

    locator_var.set(data.get("grid", ""))
    name_var.set(data.get("name", ""))
    city_var.set(data.get("city", ""))
    address_var.set(data.get("address", ""))
    zipcode_var.set(data.get("zipcode", ""))
    qsl_info_var.set(data.get("qslmgr", ""))

    try:
        my_lat, my_lon = locator_to_latlon(my_locator_var.get())
        target_lat, target_lon = None, None

        if data.get("lat") and data.get("lon"):
            target_lat = float(data["lat"])
            target_lon = float(data["lon"])
        elif data.get("grid"):
            target_lat, target_lon = locator_to_latlon(data["grid"])

        if target_lat is not None and target_lon is not None:
            sp = round(calculate_azimuth(my_lat, my_lon, target_lat, target_lon))
            lp = round((sp + 180) % 360)
            heading_var.set(f"SP: {sp}°  /  LP: {lp}°")
        else:
            heading_var.set("")
    except Exception as e:
        print("Azimuth calculation failed:", e)
        heading_var.set("")




















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
    About_Window.update_idletasks()  # Zorg dat afmetingen bekend zijn
    w = About_Window.winfo_width()

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()

    x = root_x + (root_w // 2) - (w // 2)
    y = root_y  # zelfde top als root

    About_Window.geometry(f"+{x}+{y}") 

    tk.Label(About_Window, text="MiniBook", font=('Arial', 20, 'bold')).pack(pady=10)
    separator = tk.Frame(About_Window, height=2, bd=0, relief='sunken', bg='gray')
    separator.pack(fill='x', pady=5, padx=10)
    tk.Label(About_Window, text=f"Version {VERSION_NUMBER}\n\nA Simple Python based\nJSON Logbook\n\nDeveloped by:\nBjörn Pasteuning\nPD5DJ\n\nCopyright 2024", font=('Arial', 10)).pack(pady=10)

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





# Function called beginning at start of program
def init():
    global external_server_ip, server_port_var, prefixes

    # Creating & loading of config.ini
    load_config()
    no_file_loaded() # Checks if no logbook is loaded
    prefixes = fetch_prefixes() # Initialize prefixes
    update_frequency_from_band() # Update Band to Frequency on Startup
    display_image(0, dxcc_image_label, FLAG_IMAGE_WIDTH , FLAG_IMAGE_HEIGHT) # Empty image
    start_listener(config)
    gui_state_control(12) # Shows disconnected Hamlib status
    update_datetime()
    utc_offset_var.set(config.get('Global_settings', 'utc_offset', fallback='0'))
    external_server_ip  = tk.StringVar(value=config.get('hamlib_settings', 'hamlib_ip', fallback="127.0.0.1"))
    server_port_var     = tk.StringVar(value=config.get('hamlib_settings', 'hamlib_port', fallback=4532))
    callsign_entry.focus_set() # Set focus to the callsign entry field
    load_last_logbook_on_startup()


# Save geometries for root and Logbook_Window
def save_window_geometry(window, name):
    """
    Save a specific window's geometry to the configuration file.
    """
    if window.winfo_exists():
        config = configparser.ConfigParser()
        file_path = DATA_FOLDER / CONFIG_FILE
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
    file_path = DATA_FOLDER / CONFIG_FILE
    if os.path.exists(file_path):
        config = configparser.ConfigParser()
        config.read(file_path)
        if name in config and "geometry" in config[name]:
            window.geometry(config[name]["geometry"])
            

def load_window_position(window, name):
    """
    Load the position for a specific window, keeping its size unchanged.
    """
    file_path = DATA_FOLDER / CONFIG_FILE
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
    #response = messagebox.askyesno("Confirmation", "Are you sure you want to quit the program?")
    
    response="yes"
    
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
#  _____  _____ ___      _ ___  ___  _  _   ___   _____      ___  _ _    ___   _   ___  
# |   \ \/ / __/ __|  _ | / __|/ _ \| \| | |   \ / _ \ \    / / \| | |  / _ \ /_\ |   \ 
# | |) >  < (_| (__  | || \__ \ (_) | .` | | |) | (_) \ \/\/ /| .` | |_| (_) / _ \| |) |
# |___/_/\_\___\___|  \__/|___/\___/|_|\_| |___/ \___/ \_/\_/ |_|\_|____\___/_/ \_\___/ 
#
#########################################################################################

# Function to show a popup and automatically download the JSON file
def show_popup_download():
    messagebox.showinfo("File Not Found", "The file dxcc.json was not found. It will now be downloaded.")
    download_json_file()  # Automatically download the file after showing the message                                   


# Function to download the JSON file directly into the root folder
def download_json_file():

    try:
        response = requests.get(dxcc_url)
        response.raise_for_status()  # Check if request was successful
        
        # Save the downloaded file to the root folder
        file_path = DXCC_FILE
        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        messagebox.showinfo("Download", "The file dxcc.json has been downloaded successfully.")
    
    except Exception as e:
        messagebox.showerror("Download Error", f"Failed to download file: {e}")




# Function to check callsign prefix    
def check_callsign_prefix(callsign, update_ui=True):  # Add 'update_ui' parameter
    callsign = callsign.strip().upper()  # Process the passed callsign

    # Rest of the logic remains the same
    matching_info = None
    exact_matches = []

    sorted_prefixes = sorted(prefixes.keys(), key=len, reverse=True)

    for prefix in sorted_prefixes:
        if callsign.startswith(prefix):
            exact_matches.append(prefixes[prefix])

    if exact_matches:
        regex_matches = []
        for entry in exact_matches:
            regex = entry['prefixRegex']
            if re.match(regex, callsign):
                regex_matches.append(entry)

        if regex_matches:
            matching_info = regex_matches[0]

    if not matching_info:
        for prefix in sorted_prefixes:
            regex = prefixes[prefix]['prefixRegex']
            if re.match(regex, callsign):
                matching_info = prefixes[prefix]
                break

    if matching_info:
        global country_var, continent_var
        continent = ','.join(map(str, matching_info['continent']))
        continent_name = continent_map.get(continent, "Unknown")
        continent_var = continent
        country_var = matching_info['name']
        entityCode = matching_info['entityCode']
        itu = ','.join(map(str, matching_info['itu']))
        cq = ','.join(map(str, matching_info['cq']))

        # Update UI labels and image only if update_ui is True
        if update_ui:
            country_label.config(text=f"{matching_info['name']}, {continent_name}")
            dxcc_cqitu.config(text=f"CQ Zone: {cq}, ITU ZONE: {itu}")
            display_image(entityCode, dxcc_image_label, FLAG_IMAGE_WIDTH , FLAG_IMAGE_HEIGHT)
    else:
        # Set default values for 'Not Found' case
        continent_var = ""
        country_var = "[None]"
        entityCode = ""

        # Update UI labels and image only if update_ui is True
        if update_ui:
            #country_label.config(text="Not Found")
            country_label.config(text="")
            dxcc_cqitu.config(text="")
            display_image(0, dxcc_image_label, FLAG_IMAGE_WIDTH , FLAG_IMAGE_HEIGHT)






# Function Worked Before
def update_worked_before_tree(*args):
    global qso_lines

    if current_json_file:
        try:
            with open(current_json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                qso_lines = data.get("Logbook", [])
        except Exception as e:
            print(f"Error reloading logbook: {e}")
            return

    entered_call = callsign_var.get().strip().upper()
    if not entered_call or len(entered_call) < 1:
        workedb4_tree.delete(*workedb4_tree.get_children())
        return

    matches = [qso for qso in qso_lines if qso.get("Callsign", "").upper().startswith(entered_call)]

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

    workedb4_tree.tag_configure("oddrow", background="lightblue")
    workedb4_tree.tag_configure("evenrow", background="white")

    row_color = True
    for qso in matches:
        tag = "oddrow" if row_color else "evenrow"
        row_color = not row_color

        workedb4_tree.insert("", "end", values=(
            qso.get("Callsign", ""),
            qso.get("Date", ""),
            qso.get("Time", ""),
            qso.get("Band", ""),
            qso.get("Mode", ""),
            qso.get("Frequency", ""),
            qso.get("Country", "")
        ), tags=(tag,))









#########################################################################################
#  __  __   _   ___ _  _ 
# |  \/  | /_\ |_ _| \| |
# | |\/| |/ _ \ | || .` |
# |_|  |_/_/ \_\___|_|\_|
#
#########################################################################################                        





# Main window
root = tk.Tk()


#root.title(f"MiniBook - {VERSION_NUMBER}")
root.resizable(False, False)
root.minsize(680, 265)

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
heading_var = tk.StringVar()
locator_var = tk.StringVar()
my_locator_var = tk.StringVar()
my_location_var = tk.StringVar()
my_callsign_var = tk.StringVar()
my_operator_var = tk.StringVar()
my_pota_var = tk.StringVar()
my_wwff_var = tk.StringVar()
wwff_var = tk.StringVar()
pota_var = tk.StringVar()
country_var = tk.StringVar()
continent_var = tk.StringVar()
rst_sent_var = tk.StringVar(value="59")
rst_received_var = tk.StringVar(value="59")
comment_var = tk.StringVar()
frequency_var = tk.StringVar()
band_var = tk.StringVar(value="20m")
mode_var = tk.StringVar(value="USB")
submode_var = tk.StringVar(value="")
satellite_var = tk.StringVar(value="")
utc_offset_var = tk.StringVar(value="0")
radio_status_var = tk.StringVar()
datetime_tracking_enabled = tk.BooleanVar(value=True)  # Enabled by default
freqmode_tracking_var = tk.BooleanVar(value=False)
qrz_username_var = tk.StringVar()
qrz_password_var = tk.StringVar()

# Preparation of hamlib in Threaded mode
hamlib_process = None
socket_connection = None

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

# Callback voor de optie Freq/Mode in menu Tracking
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
menu_bar.add_cascade(label="Window", menu=view_menu)

# --- Reference Menu ---
reference_menu = tk.Menu(menu_bar, tearoff=0)
reference_menu.add_command(label="DX Summit", command=lambda: webbrowser.open("http://www.dxsummit.fi/#/"))
reference_menu.add_separator()
reference_menu.add_command(label="POTA Activations", command=lambda: webbrowser.open("https://pota.app/#/"))
reference_menu.add_command(label="POTA Map", command=lambda: webbrowser.open("https://pota.app/#/map"))
reference_menu.add_separator()
reference_menu.add_command(label="WWFF Agenda", command=lambda: webbrowser.open("https://wwff.co/agenda/"))
reference_menu.add_command(label="WWFF Dutch Map", command=lambda: webbrowser.open("https://www.google.com/maps/d/u/0/view?hl=en&mid=1yXBN79NWlsI-wrZaDfyeXA2zg129nEU&ll=52.12186480765635%2C5.251994000000018&z=8"))
reference_menu.add_command(label="WWFF Global Map", command=lambda: webbrowser.open("https://ham-map.com/"))
reference_menu.add_command(label="WWFF Announce activation", command=lambda: webbrowser.open("https://www.cqgma.org/alertwwfflight.php"))
#reference_menu.add_separator()
#reference_menu.add_command(label="SOTA Watch", command=lambda: webbrowser.open("https://sotawatch.sota.org.uk/"))
menu_bar.add_cascade(label="References", menu=reference_menu)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Update DXCC lookup file", command=download_json_file)
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
    #event.widget.configure(background="#e0f7ff")
    event.widget.configure(background="#FFCCDD")

def reset_focus_color(event):
    event.widget.configure(background="white")





# Set the width for columns 0 and 1
root.grid_columnconfigure(0, weight=0, minsize=50)
root.grid_columnconfigure(1, weight=0, minsize=50)
root.grid_columnconfigure(2, weight=0, minsize=50)
root.grid_columnconfigure(3, weight=0, minsize=50)
root.grid_columnconfigure(4, weight=0, minsize=50)
root.grid_columnconfigure(5, weight=0, minsize=50)
root.grid_columnconfigure(5, weight=0, minsize=50)


#------------- Field/Label positions Row/Column/Span --------------

System_info_frame_row          = 0
System_info_frame_col          = 0
System_info_frame_colspan      = 10

Seperator_0_row                = 1
Seperator_0_col                = 0
Seperator_0_colspan            = 7

#--------------------------------------

My_info_frame_row              = 2
My_info_frame_col              = 0
My_info_frame_colspan          = 10

Seperator_1_row                = 3
Seperator_1_col                = 0
Seperator_1_colspan            = 7

#--------------------------------------


Date_header_row                = 4
Date_header_col                = 0
Date_header_colspan            = 1
Date_row                       = 4
Date_col                       = 1
Date_colspan                   = 1

Time_header_row                = 4
Time_header_col                = 2
Time_header_colspan            = 1
Time_row                       = 4
Time_col                       = 3
Time_colspan                   = 1

Callsign_header_row            = 5
Callsign_header_col            = 0
Callsign_header_colspan        = 1
Callsign_row                   = 5
Callsign_col                   = 1
Callsign_colspan               = 1

RST_sent_header_row            = 5
RST_sent_header_col            = 2
RST_sent_header_colspan        = 1
RST_sent_row                   = 5
RST_sent_col                   = 3
RST_sent_colspan               = 1

RST_rcvd_header_row            = 5
RST_rcvd_header_col            = 3
RST_rcvd_header_colspan        = 1
RST_rcvd_row                   = 5
RST_rcvd_col                   = 4
RST_rcvd_colspan               = 1

Locator_header_row             = 6
Locator_header_col             = 0
Locator_header_colspan         = 1
Locator_row                    = 6
Locator_col                    = 1
Locator_colspan                = 1

Mode_header_row                = 6
Mode_header_col                = 2
Mode_header_colspan            = 1
Mode_row                       = 6
Mode_col                       = 3
Mode_colspan                   = 1

Submode_header_row             = 6
Submode_header_col             = 3
Submode_header_colspan         = 1
Submode_row                    = 6
Submode_col                    = 4
Submode_colspan                = 1

Band_header_row                = 7
Band_header_col                = 0
Band_header_colspan            = 1
Band_row                       = 7
Band_col                       = 1
Band_colspan                   = 1

Freq_header_row                = 7
Freq_header_col                = 2
Freq_header_colspan            = 1
Freq_row                       = 7
Freq_col                       = 3
Freq_colspan                   = 1

Satellite_header_row           = 7
Satellite_header_col           = 3
Satellite_header_colspan       = 1
Satellite_row                  = 7
Satellite_col                  = 4
Satellite_colspan              = 1

Name_header_row                = 8
Name_header_col                = 0
Name_header_colspan            = 1
Name_row                       = 8
Name_col                       = 1
Name_colspan                   = 1

Comment_header_row             = 8
Comment_header_col             = 2
Comment_header_colspan         = 1
Comment_row                    = 8
Comment_col                    = 3
Comment_colspan                = 3

WWFF_header_row                 = 9
WWFF_header_col                 = 0
WWFF_header_colspan             = 1
WWFF_row                        = 9
WWFF_col                        = 1
WWFF_colspan                    = 1

POTA_header_row                 = 9
POTA_header_col                 = 2
POTA_header_colspan             = 1
POTA_row                        = 9
POTA_col                        = 3
POTA_colspan                    = 1

Seperator_5_row                = 10
Seperator_5_col                = 0
Seperator_5_colspan            = 6

QRZ_text_row                   = 11
QRZ_text_col                   = 0
QRZ_text_colspan               = 2

QSL_info_header_row             = 11
QSL_info_header_col             = 2
QSL_info_header_colspan         = 1
QSL_info_row                    = 11
QSL_info_col                    = 3
QSL_info_colspan                = 3

Address_header_row             = 12  
Address_header_col             = 0
Address_header_colspan         = 1
Address_row                    = 12
Address_col                    = 1
Address_colspan                = 3

Heading_header_row             = 12
Heading_header_col             = 4
Heading_header_rowspan         = 2
Heading_entry_row              = 12
Heading_entry_col              = 5
Heading_entry_colspan          = 2
Heading_entry_rowspan          = 2

City_header_row                = 13
City_header_col                = 0
City_header_colspan            = 1
City_row                       = 13
City_col                       = 1
City_colspan                   = 1

Zipcode_header_row             = 13
Zipcode_header_col             = 2
Zipcode_header_colspan         = 1
Zipcode_row                    = 13
Zipcode_col                    = 3
Zipcode_colspan                = 1



Seperator_2_row                = 14
Seperator_2_col                = 0
Seperator_2_colspan            = 7

#--------------------------------------
DXCC_frame_row                 = 15
DXCC_frame_col                 = 0
DXCC_frame_colspan             = 99


Wipe_button_row                = 4
Wipe_button_col                = 6
Wipe_button_colspan            = 1
Wipe_button_rowspan            = 2

Lookup_button_row              = 6
Lookup_button_col              = 6
Lookup_button_colspan          = 1
Lookup_button_rowspan          = 2

Log_button_row                 = 8
Log_button_col                 = 6
Log_button_colspan             = 1
Log_button_rowspan             = 3

Seperator_3_row                = 16
Seperator_3_col                = 0
Seperator_3_colspan            = 7

#--------------------------------------

workedb4_row                   = 18

Last_qso_row                   = 20
Last_qso_col                   = 0
Last_qso_colspan               = 3

DXCC_Info_row                  = 20
DXCC_Info_col                  = 0
DXCC_Info_colspan              = 7


y_padding                      = 2

bg_color = root.cget("bg")

# MY INFO FRAME
my_info_frame = tk.Frame(root, bg="lightgrey")
my_info_frame.grid(row=My_info_frame_row, column=My_info_frame_col, columnspan=My_info_frame_colspan, sticky='we', padx=5, pady=2)

# Configure columns to stretch and control alignment
my_info_frame.columnconfigure(0, weight=1)  # left
my_info_frame.columnconfigure(1, weight=1)  # center
my_info_frame.columnconfigure(2, weight=1)  # right

# (My Callsign)
callsign_frame = tk.Frame(my_info_frame, bg="lightgrey")
callsign_frame.grid(row=0, column=0, padx=5, sticky='w')
tk.Label(callsign_frame, text="Callsign:", font=('Arial', 10), bg="lightgrey").pack(side='left', padx=(0, 3))
my_callsign_label = tk.Label(callsign_frame, font=('Arial', 10, 'bold'), bg="lightgrey")
my_callsign_label.pack(side='left')

# (My Operator)
operator_frame = tk.Frame(my_info_frame, bg="lightgrey")
operator_frame.grid(row=0, column=1, padx=5, sticky='w')
tk.Label(operator_frame, text="Operator:", font=('Arial', 10), bg="lightgrey").pack(side='left', padx=(0, 3))
my_operator_label = tk.Label(operator_frame, font=('Arial', 10, 'bold'), bg="lightgrey")
my_operator_label.pack(side='left')

# (My Locator)
locator_frame = tk.Frame(my_info_frame, bg="lightgrey")
locator_frame.grid(row=0, column=2, padx=5)
tk.Label(locator_frame, text="Locator:", font=('Arial', 10), bg="lightgrey").pack(side='left', padx=(0, 3))
my_locator_label = tk.Label(locator_frame, font=('Arial', 10, 'bold'), bg="lightgrey")
my_locator_label.pack(side='left')

# (My Location)
location_frame = tk.Frame(my_info_frame, bg="lightgrey")
location_frame.grid(row=1, column=0, padx=5, sticky='w')
tk.Label(location_frame, text="Location:", font=('Arial', 10), bg="lightgrey").pack(side='left', padx=(0, 3))
my_location_label = tk.Label(location_frame, font=('Arial', 10, 'bold'), bg="lightgrey")
my_location_label.pack(side='left')

# (My WWFF)
my_wwff_frame = tk.Frame(my_info_frame, bg="lightgrey")
my_wwff_frame.grid(row=1, column=1, padx=5, sticky='w')  # Positioned under My Callsign
tk.Label(my_wwff_frame, text="WWFF:", font=('Arial', 10), bg="lightgrey").pack(side='left', padx=(0, 3))
my_wwff_label = tk.Label(my_wwff_frame, font=('Arial', 10, 'bold'), bg="lightgrey")
my_wwff_label.pack(side='left')

# (My POTA)
my_pota_frame = tk.Frame(my_info_frame, bg="lightgrey")
my_pota_frame.grid(row=1, column=2, padx=5)  # Positioned under My Locator
tk.Label(my_pota_frame, text="POTA:", font=('Arial', 10), bg="lightgrey").pack(side='left', padx=(0, 3))
my_pota_label = tk.Label(my_pota_frame, font=('Arial', 10, 'bold'), bg="lightgrey")
my_pota_label.pack(side='left')
# ---------------------
separator = ttk.Separator(root, orient='horizontal')
separator.grid(row=Seperator_1_row, column=Seperator_1_col, columnspan=Seperator_1_colspan, sticky='ew', padx=5, pady=0)

# DATE
tk.Label(root, text="QSO Date:", font=('Arial', 10)).grid(row=Date_header_row, column=Date_header_col, columnspan=Date_header_colspan, padx=5, pady=y_padding, sticky='e')
date_entry = DateEntry(root, textvariable=date_var, date_pattern='yyyy-mm-dd', font=('Arial', 10, 'bold'))
date_entry.grid(row=Date_row, column=Date_col, columnspan=Date_colspan, padx=5, pady=y_padding, sticky='w')
date_entry.configure(takefocus=False)

# TIME
tk.Label(root, text="QSO Time:", font=('Arial', 10)).grid(row=Time_header_row, column=Time_header_col, columnspan=Time_header_colspan, padx=5, pady=y_padding, sticky='e')
time_entry = tk.Entry(root, textvariable=time_var, font=('Arial', 10, 'bold'), width=10)
time_entry.grid(row=Time_row, column=Time_col, columnspan=Time_colspan, padx=5, pady=y_padding, sticky='w')
time_entry.configure(takefocus=False)

def on_tab_press(event):
    on_query()
    return None

# CALLSIGN
tk.Label(root, text="Callsign:", font=('Arial', 10)).grid(row=Callsign_header_row, column=Callsign_header_col, columnspan=Callsign_header_colspan, padx=5, pady=y_padding, sticky='e')
callsign_entry = tk.Entry(root, textvariable=callsign_var, font=('Arial', 10, 'bold'))
callsign_entry.grid(row=Callsign_row, column=Callsign_col, columnspan=Callsign_colspan, padx=5, pady=y_padding, sticky='w')
callsign_entry.bind("<Tab>", on_tab_press)
callsign_entry.bind("<FocusIn>", set_focus_color)
callsign_entry.bind("<FocusOut>", reset_focus_color)

# SENT
tk.Label(root, text="Sent:", font=('Arial', 10)).grid(row=RST_sent_header_row, column=RST_sent_header_col, columnspan=RST_sent_header_colspan, padx=5, pady=y_padding, sticky='e')
rst_sent_combobox = ttk.Combobox(root, textvariable=rst_sent_var, values=rst_options, font=('Arial', 10, 'bold'), width=8)
rst_sent_combobox.grid(row=RST_sent_row, column=RST_sent_col, columnspan=RST_sent_colspan, padx=5, pady=y_padding, sticky='w')

# RECEIVED
tk.Label(root, text="Received:", font=('Arial', 10)).grid(row=RST_rcvd_header_row, column=RST_rcvd_header_col, columnspan=RST_rcvd_header_colspan,  padx=5, pady=y_padding, sticky='e')
rst_received_combobox = ttk.Combobox(root, textvariable=rst_received_var, values=rst_options, font=('Arial', 10, 'bold'), width=8)
rst_received_combobox.grid(row=RST_rcvd_row, column=RST_rcvd_col, columnspan=RST_rcvd_colspan, padx=5, pady=y_padding, sticky='w')

# LOCATOR
tk.Label(root, text="Locator:", font=('Arial', 10)).grid(row=Locator_header_row, column=Locator_header_col, columnspan=Locator_header_colspan,  padx=5, pady=y_padding, sticky='e')
locator_entry = tk.Entry(root, textvariable=locator_var, font=('Arial', 10, 'bold'))
locator_entry.grid(row=Locator_row, column=Locator_col, columnspan=Locator_colspan, padx=5, pady=y_padding, sticky='w')
locator_entry.bind("<FocusIn>", set_focus_color)
locator_entry.bind("<FocusOut>", reset_focus_color)

# MODE
tk.Label(root, text="Mode:", font=('Arial', 10)).grid(row=Mode_header_row, column=Mode_header_col, columnspan=Mode_header_colspan,  padx=5, pady=y_padding, sticky='e')
mode_combobox = ttk.Combobox(root, textvariable=mode_var, values=mode_options, font=('Arial', 10, 'bold'), width=8, state='readonly')
mode_combobox.grid(row=Mode_row, column=Mode_col, columnspan=Mode_colspan, padx=5, pady=y_padding, sticky='w')
mode_combobox.bind("<<ComboboxSelected>>", on_mode_change)
    
# SUBMODE
tk.Label(root, text="Submode:", font=('Arial', 10)).grid(row=Submode_header_row, column=Submode_header_col, columnspan=Submode_header_colspan,  padx=5, pady=y_padding, sticky='e')
submode_combobox = ttk.Combobox(root, textvariable=submode_var, values=submode_options, font=('Arial', 10, 'bold'), width=8, state='readonly')
submode_combobox.grid(row=Submode_row, column=Submode_col, columnspan=Submode_colspan, padx=5, pady=y_padding, sticky='w')
submode_combobox.configure(takefocus=False)

# BAND
tk.Label(root, text="Band:", font=('Arial', 10)).grid(row=Band_header_row, column=Band_header_col, columnspan=Band_header_colspan, padx=5, pady=y_padding, sticky='e')
band_combobox = ttk.Combobox(root, width=8, textvariable=band_var, values=list(band_to_frequency.keys()), font=('Arial', 10, 'bold'), state='readonly')
band_combobox.grid(row=Band_row, column=Band_col, columnspan=Band_colspan, padx=5, pady=y_padding, sticky='w')
band_combobox.bind("<<ComboboxSelected>>", update_frequency_from_band) # Bind band change to update frequency

# FREQUENCY
tk.Label(root, text="Freq (MHz):", font=('Arial', 10)).grid(row=Freq_header_row, column=Freq_header_col, columnspan=Freq_header_colspan, padx=5, pady=y_padding, sticky='e')
freq_entry = tk.Entry(root, textvariable=frequency_var, font=('Arial', 10, 'bold'), width=10)
freq_entry.grid(row=Freq_row, column=Freq_col, columnspan=Freq_colspan, padx=5, pady=y_padding, sticky='w')
freq_entry.bind("<FocusIn>", on_focus)      # Set cursor ready for direct edit by selecting all text on focus
freq_entry.bind("<FocusIn>", set_focus_color)
freq_entry.bind("<FocusOut>", reset_focus_color)
freq_entry.bind("<KeyPress>", on_keypress)  # Bind keypress to allow numbers and one decimal point
frequency_var.trace("w", update_band_from_frequency) # Bind frequency input to update the band if the frequency is outside the selected band


# SATELLITE pulldown
tk.Label(root, text="Satellite:", font=('Arial', 10)).grid(row=Satellite_header_row, column=Satellite_header_col, columnspan=Satellite_header_colspan, padx=5, pady=y_padding, sticky='e')
satellite_list = load_satellite_names() # Load list of sattelites
satellite_list.insert(0, "")
satellite_var = tk.StringVar()
satellite_dropdown = ttk.Combobox(root, textvariable=satellite_var, values=satellite_list, font=('Arial', 10, 'bold'), width=8, state="readonly")
satellite_dropdown.grid(row=Satellite_row, column=Satellite_col, columnspan=Satellite_colspan, padx=5, pady=y_padding, sticky='ew')


# NAME
tk.Label(root, text="Name:", font=('Arial', 10)).grid(row=Name_header_row, column=Name_header_col, columnspan=Name_header_colspan, padx=5, pady=y_padding, sticky='e')
name_entry = tk.Entry(root, textvariable=name_var, font=('Arial', 10, 'bold'))
name_entry.grid(row=Name_row, column=Name_col, columnspan=Name_colspan, padx=5, pady=y_padding, sticky='w')
name_entry.bind("<FocusIn>", set_focus_color)
name_entry.bind("<FocusOut>", reset_focus_color)

# COMMENT
tk.Label(root, text="Comment:", font=('Arial', 10)).grid(row=Comment_header_row, column=Comment_header_col, columnspan=Comment_header_colspan, padx=5, pady=y_padding, sticky='e')
comment_entry = tk.Entry(root, textvariable=comment_var, font=('Arial', 10, 'bold'))
comment_entry.grid(row=Comment_row, column=Comment_col, columnspan=Comment_colspan, padx=5, pady=y_padding, sticky='ew')
comment_entry.bind("<FocusIn>", set_focus_color)
comment_entry.bind("<FocusOut>", reset_focus_color)

# WWFF
tk.Label(root, text="WWFF:", font=('Arial', 10)).grid(row=WWFF_header_row, column=WWFF_header_col, columnspan=WWFF_header_colspan, padx=5, pady=y_padding, sticky='e')
wwff_entry = tk.Entry(root, textvariable=wwff_var, font=('Arial', 10, 'bold'))
wwff_entry.grid(row=WWFF_row, column=WWFF_col, columnspan=WWFF_colspan, padx=5, pady=y_padding, sticky='ew')
wwff_entry.bind("<KeyRelease>", lambda event: format_wwff_input(event, wwff_entry, wwff_var))
wwff_entry.bind("<FocusIn>", set_focus_color)
wwff_entry.bind("<FocusOut>", reset_focus_color)

# POTA
tk.Label(root, text="POTA:", font=('Arial', 10)).grid(row=POTA_header_row, column=POTA_header_col, columnspan=POTA_header_colspan, padx=5, pady=y_padding, sticky='e')
pota_entry = tk.Entry(root, textvariable=pota_var, font=('Arial', 10, 'bold'))
pota_entry.grid(row=POTA_row, column=POTA_col, columnspan=POTA_colspan, padx=5, pady=y_padding, sticky='ew')
pota_entry.bind("<KeyRelease>", lambda event: format_pota_input(event, pota_entry, pota_var))
pota_entry.bind("<FocusIn>", set_focus_color)
pota_entry.bind("<FocusOut>", reset_focus_color)

# ---------------------
separator = ttk.Separator(root, orient='horizontal')
separator.grid(row=Seperator_5_row, column=Seperator_5_col, columnspan=Seperator_5_colspan, sticky='ew', padx=5, pady=0)


tk.Label(root, text="Extra QRZ Lookup results", bg='lightgrey', font=('Arial', 10, 'bold')).grid(row=QRZ_text_row, column=QRZ_text_col, columnspan=QRZ_text_colspan, padx=5, pady=y_padding, sticky='ew')

# Address
tk.Label(root, text="QSL Info:", font=('Arial', 10)).grid(row=QSL_info_header_row, column=QSL_info_header_col, columnspan=QSL_info_header_colspan, padx=5, pady=y_padding, sticky='e')
qsl_info_entry = tk.Entry(root, textvariable=qsl_info_var, font=('Arial', 10, 'bold'))
qsl_info_entry.grid(row=QSL_info_row, column=QSL_info_col, columnspan=QSL_info_colspan, padx=5, pady=y_padding, sticky='ew')
qsl_info_entry.bind("<FocusIn>", set_focus_color)
qsl_info_entry.bind("<FocusOut>", reset_focus_color)

# Address
tk.Label(root, text="Address:", font=('Arial', 10)).grid(row=Address_header_row, column=Address_header_col, columnspan=Address_header_colspan, padx=5, pady=y_padding, sticky='e')
address_entry = tk.Entry(root, textvariable=address_var, font=('Arial', 10, 'bold'))
address_entry.grid(row=Address_row, column=Address_col, columnspan=Address_colspan, padx=5, pady=y_padding, sticky='ew')
address_entry.bind("<FocusIn>", set_focus_color)
address_entry.bind("<FocusOut>", reset_focus_color)

# City
tk.Label(root, text="City:", font=('Arial', 10)).grid(row=City_header_row, column=City_header_col, columnspan=City_header_colspan, padx=5, pady=y_padding, sticky='e')
city_entry = tk.Entry(root, textvariable=city_var, font=('Arial', 10, 'bold'))
city_entry.grid(row=City_row, column=City_col, columnspan=City_colspan, padx=5, pady=y_padding, sticky='w')
city_entry.bind("<FocusIn>", set_focus_color)
city_entry.bind("<FocusOut>", reset_focus_color)

# Zip Code
tk.Label(root, text="Zipcode:", font=('Arial', 10)).grid(row=Zipcode_header_row, column=Zipcode_header_col, columnspan=Zipcode_header_colspan, padx=5, pady=y_padding, sticky='e')
zipcode_entry = tk.Entry(root, textvariable=zipcode_var, font=('Arial', 10, 'bold'))
zipcode_entry.grid(row=Zipcode_row, column=Zipcode_col, columnspan=Zipcode_colspan, padx=5, pady=y_padding, sticky='w')
zipcode_entry.bind("<FocusIn>", set_focus_color)
zipcode_entry.bind("<FocusOut>", reset_focus_color)

# Heading Info
tk.Label(root, text="Heading:", font=('Arial', 10)).grid(row=Heading_header_row, column=Heading_header_col, columnspan=1, rowspan=Heading_header_rowspan, padx=0, pady=y_padding, sticky='e')
heading_entry = tk.Entry(root, textvariable=heading_var, font=('Arial', 10, 'bold'),state='readonly')
heading_entry.grid(row=Heading_entry_row, column=Heading_entry_col, columnspan=Heading_entry_colspan, rowspan=Heading_entry_rowspan, padx=5, pady=y_padding, sticky='w')
heading_entry.configure(takefocus=False)

# Frame
dxcc_frame = tk.Frame(dxcc_window, bg=bg_color)
dxcc_frame.grid(row=DXCC_frame_row, column=DXCC_frame_col, columnspan=DXCC_frame_colspan, sticky="nsew", pady=(0, 0))

# Configure columns to center contents
dxcc_frame.columnconfigure(0, weight=1)
dxcc_frame.columnconfigure(1, weight=0)
dxcc_frame.columnconfigure(2, weight=0)
dxcc_frame.columnconfigure(3, weight=1)

# Image label (centered via column 1)
dxcc_image_label = tk.Label(dxcc_frame, anchor='center', bg=bg_color)
dxcc_image_label.grid(row=0, column=1, padx=5, pady=0, sticky="")

# Country label (right next to image, centered via column 2)
country_label = tk.Label(dxcc_frame, font=('Arial', 10, 'bold'), anchor='center', bg=bg_color)
country_label.grid(row=0, column=2, padx=5, pady=0, sticky="")


# --- Lookup Button ---
lookup_button = tk.Button(root, text="Lookup\nF2", command=on_query, bd=3, relief='raised',width=10, height=2, bg='yellow', fg='black', font=('Arial', 10, 'bold'))
lookup_button.grid(row=Lookup_button_row, column=Lookup_button_col, columnspan=Lookup_button_colspan, rowspan=Lookup_button_rowspan, padx=15, pady=0, sticky='w')
lookup_button.configure(takefocus=False)

# LOG BUTTON
log_button = tk.Button(root, text="Log QSO\nF5", command=log_qso, bd=3, relief='raised',width=10, height=2, bg='green', fg='white', font=('Arial', 10, 'bold'))
log_button.grid(row=Log_button_row, column=Log_button_col, columnspan=Log_button_colspan, rowspan=Log_button_rowspan, padx=15, pady=0, sticky='w')
log_button.configure(takefocus=False)

# WIPE BUTTON
wipe_button = tk.Button(root, text="Wipe\nF1", command=reset_fields, bd=3, relief='raised',width=10, height=2, bg='red', fg='white', font=('Arial', 10, 'bold'))
wipe_button.grid(row=Wipe_button_row, column=Wipe_button_col, columnspan=Wipe_button_colspan, rowspan=Wipe_button_rowspan, padx=15, pady=0, sticky='w')
wipe_button.configure(takefocus=False)

# ---------------------
separator = ttk.Separator(root, orient='horizontal')
separator.grid(row=Seperator_2_row, column=Seperator_2_col, columnspan=Seperator_2_colspan, sticky='ew', padx=5)

# LAST QSO
last_qso_label = tk.Label(root, fg="blue", padx=5, pady=y_padding, font=('Arial', 8, 'bold'))
last_qso_label.grid(row=Last_qso_row, column=Last_qso_col, columnspan=Last_qso_colspan,padx=5, sticky='w')

# DXCC INFO
dxcc_cqitu = tk.Label(root, font=('Arial', 8))
dxcc_cqitu.grid(row=DXCC_Info_row, column=DXCC_Info_col, columnspan=DXCC_Info_colspan, padx=5,  sticky='e')

# ---------------------
separator = ttk.Separator(root, orient='horizontal')
separator.grid(row=Seperator_3_row, column=Seperator_3_col, columnspan=Seperator_3_colspan, sticky='ew', padx=5)



#----------- WORKED BEFORE FRAME ------------


workedb4_frame = tk.Frame(workedb4_window, bg=bg_color)
workedb4_frame.grid(row=workedb4_row, column=0, columnspan=99, sticky="nsew", pady=(0, 0))
root.grid_rowconfigure(10, weight=1)
root.grid_columnconfigure(0, weight=1)


title_label = tk.Label(workedb4_frame, text="Worked before result", font=('Arial', 11, 'bold'), bg=bg_color)
title_label.pack(anchor="center", padx=10, pady=(0, 0))

tree_frame = tk.Frame(workedb4_frame)
tree_frame.pack(fill="both", expand=True, padx=10, pady=0)

# Scrollbars
y_scroll = tk.Scrollbar(tree_frame, orient="vertical")
y_scroll.pack(side="right", fill="y")

# TreeView
cols = ("Callsign", "Date", "Time", "Band", "Frequency", "Mode", "Country")
workedb4_tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=5, yscrollcommand=y_scroll.set
)

y_scroll.config(command=workedb4_tree.yview)

for col in cols:
    workedb4_tree.heading(col, text=col)
    workedb4_tree.column(col, anchor="center", width=80)

workedb4_tree.pack(fill="both", expand=True)




# Buttons Bindings
# Bind F5 key to log_button function
def invoke_log_button(event=None):
    log_button.invoke()
root.bind("<F5>", invoke_log_button)

# Bind F1 key to reset_fields function
def invoke_reset_fields(event=None):
    reset_fields()
root.bind("<F1>", invoke_reset_fields)

# Bind F2 key to Lookup function
def invoke_lookup_button(event=None):
    lookup_button.invoke()
root.bind("<F2>", invoke_lookup_button)


# Call init function to Preset / Preload  variables / Tasks
init()

# Bind the on_close function to the "X" button
root.protocol("WM_DELETE_WINDOW", exit_program)

# Start main loop
root.mainloop()
