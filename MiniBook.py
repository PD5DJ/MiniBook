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
import serial.tools.list_ports
import socket
import sys
import threading
import time
import ipaddress


VERSION_NUMBER = ("v1.2.9")

# Choose whether to use the local folder (True) or the APPDATA folder (False)
use_local_folder    = False

if use_local_folder:
    data_directory = Path.cwd()
else:
    data_directory = Path(os.getenv('APPDATA')) / "MiniBook"
    # Ensure the directory exists
    data_directory.mkdir(parents=True, exist_ok=True)

# Configuration file path
CONFIG_FILE         = "config.ini"
RIGS_FILE           = "rigs.ini"
DXCC_FILE           = "dxcc.json"
current_json_file   = None  # logbook file

# Global variables
tree                = None  # Logviewer Tree
Logbook_Window      = None  # Logbook window open / closed
Edit_Window         = None  # Edit window open / closed
Preference_Window   = None
Station_Setup_Window= None
About_Window        = None
workedb4_window     = None
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
                "Locator": "AA11BB",  # Placeholder, adjust as needed
                "Location": ""
            },
            "Logbook": []
        }
        with open(current_json_file, 'w') as file:
            json.dump(data, file, indent=4)  # Save initial structure with indentation
        loaded_file_label.config(text=os.path.basename(current_json_file), fg='blue')

        load_station_setup()
        file_menu.entryconfig("Station setup", state="normal")

# Helper function to convert old logbook format (list) to new format (dictionary)
def convert_old_logbook(old_logbook):
    # Create a template for the new format with Station info
    new_format = {
        "Station": {
            "Callsign": "N0CALL",
            "Locator": "AA11BB",  # Placeholder, adjust as needed
            "Location": ""
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
            "My_Locator": "",
            "My_Location": "",
            "Country": entry.get("Country", ""),
            "Continent": entry.get("Continent", ""),
            "Sent": entry.get("Sent", ""),
            "Received": entry.get("Received", ""),
            "Mode": entry.get("Mode", ""),
            "Submode": "",
            "Band": entry.get("Band", ""),
            "Frequency": entry.get("Frequency", ""),
            "Locator": entry.get("Locator", ""),
            "Comment": entry.get("Comment", "")
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
                            loaded_file_label.config(text=os.path.basename(current_json_file), fg='blue')
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
                            loaded_file_label.config(text=os.path.basename(current_json_file), fg='blue')
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
                    file_path = data_directory / CONFIG_FILE
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
                qso.get('My Callsign', ''),
                qso.get('My Locator', ''),
                qso.get('My Location', '')
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
    columns = ('Date', 'Time', 'Callsign', 'Name', 'Country', 'Sent', 'Received', 'Mode', 'Submode','Band', 'Frequency', 'Locator', 'Comment', 'My Callsign', 'My Locator', 'My Location')

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
        'My Callsign': 80,
        'My Locator': 70,
        'My Location': 120,
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
                    qso.get('My Callsign', ''),
                    qso.get('My Locator', ''),
                    qso.get('My Location', '')
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








# Function to edit selected QSO
def edit_qso(event):
    global Edit_Window

    # Check if the edit window is already open
    if Edit_Window is not None and Edit_Window.winfo_exists():
        Edit_Window.lift()  # Bring the existing window to the front
        return

    selected_item = tree.selection()
    if not selected_item:
        return  # No item selected

    # Get the unique identifier from the selected item
    selected_item_values = tree.item(selected_item, 'values')
    unique_identifier = f"{selected_item_values[2]}_{selected_item_values[0]}_{selected_item_values[1]}"  # Example: Callsign_Date_Time

    # Create a new window for editing
    Edit_Window = tk.Toplevel(root)
    Edit_Window.title("Edit QSO Entry")
    Edit_Window.resizable(False, False)

    # Center the edit window relative to Logbook_Window
    Logbook_Window.update_idletasks()  # Ensure dimensions are calculated
    logbook_x = Logbook_Window.winfo_x()
    logbook_y = Logbook_Window.winfo_y()
    logbook_width = Logbook_Window.winfo_width()
    logbook_height = Logbook_Window.winfo_height()
    edit_width = 270  # Estimated width of Edit_Window
    edit_height = 550  # Estimated height of Edit_Window

    edit_x = logbook_x + (logbook_width - edit_width) // 2
    edit_y = logbook_y + (logbook_height - edit_height) // 2
    Edit_Window.geometry(f"{edit_width}x{edit_height}+{edit_x}+{edit_y}")

    # Disable interaction with Logbook_Window until Edit_Window is closed
    Edit_Window.grab_set()

    # Create labels and entries for each QSO attribute
    fields = ['Date', 'Time', 'Callsign', 'Name', 'Country', 'Sent', 'Received', 'Mode', 'Submode', 'Band', 'Frequency', 'Locator', 'Comment', 'My Callsign', 'My Locator', 'My Location']
    entries = {}

    # Find the original QSO entry using the unique identifier
    original_qso = next((qso for qso in qso_lines if f"{qso['Callsign']}_{qso['Date']}_{qso['Time']}" == unique_identifier), None)

    if original_qso is None:
        print("QSO entry not found!")
        return

    for i, field in enumerate(fields):
        tk.Label(Edit_Window, text=field).grid(row=i, column=0, padx=10, pady=5)

        if field == 'Date':
            entry = DateEntry(Edit_Window, date_pattern='yyyy-mm-dd')
            entry.set_date(original_qso['Date'])  # Set the initial date

        elif field == 'Band':
            entry = ttk.Combobox(Edit_Window, values=list(band_to_frequency.keys()), state="readonly")
            entry.set(original_qso.get('Band', ''))

        elif field == 'Mode':
            entry = ttk.Combobox(Edit_Window, values=mode_options, state="readonly")
            entry.set(original_qso.get('Mode', ''))

        elif field == 'Submode':
            entry = ttk.Combobox(Edit_Window, values=submode_options, state="readonly")
            entry.set(original_qso.get('Submode', ''))

        elif field == 'Sent' or field == 'Received':
            entry = ttk.Combobox(Edit_Window, values=rst_options, state="readonly")
            entry.set(original_qso.get(field, ''))

        else:
            entry = tk.Entry(Edit_Window)
            entry.insert(0, original_qso.get(field, ''))

        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[field] = entry  # Store entry reference

    # Function to close the edit window and reset the global variable
    def close_edit_window():
        global Edit_Window
        Edit_Window.grab_release()  # Release the grab when closing        
        Edit_Window.destroy()
        Edit_Window = None

    # Function to save the edited QSO
    def save_changes():
        original_qso['Callsign'] = entries['Callsign'].get().strip().upper()
        original_qso['Locator'] = entries['Locator'].get().strip().upper()
        original_qso['My Locator'] = entries['My Locator'].get().strip().upper()
        original_qso['My Callsign'] = entries['My Callsign'].get().strip().upper()
        original_qso['Mode'] = entries['Mode'].get().strip().upper()
        original_qso['Submode'] = entries['Submode'].get().strip().upper()
        original_qso['Band'] = entries['Band'].get().strip().lower()

        locator1 = original_qso['Locator'].strip()
        locator2 = original_qso['My Locator'].strip()

        # Validate locator field
        if not is_valid_locator(locator1) or not is_valid_locator(locator2):
            messagebox.showerror("Invalid Locator", "The Maidenhead locator must be at least 4 characters and valid.\nExample: FN31 or FN31TK")
            return

        # Update the QSO entry in qso_lines
        for field in fields:
            if field not in ['Callsign', 'Mode', 'Band', 'Submode', 'Locator', 'My Locator', 'My Callsign']:
                original_qso[field] = entries[field].get().strip()

        # Create DateTime object for the updated entry
        date_str = entries['Date'].get().strip()
        time_str = entries['Time'].get().strip()
        if date_str and time_str:
            original_qso['DateTime'] = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')

        # Save changes to the JSON file
        save_to_json()

        # Update the Treeview and close the edit window
        load_json_content()
        close_edit_window()

    # Function to delete the QSO
    def delete_qso():
        if messagebox.askyesno("Delete Confirmation", "Are you sure you want to delete this QSO?"):
            global qso_lines
            qso_lines = [qso for qso in qso_lines if qso != original_qso]

            # Save changes to JSON and reload the Treeview
            save_to_json()
            load_json_content()
            close_edit_window()

    # Close button
    close_button = tk.Button(Edit_Window, text="Close", command=close_edit_window)
    close_button.grid(row=len(fields), column=0, pady=10)

    # Save button
    save_button = tk.Button(Edit_Window, text="Save", command=save_changes)
    save_button.grid(row=len(fields), column=1, pady=10, sticky='e')

    # Delete button
    delete_button = tk.Button(Edit_Window, text="Delete", command=delete_qso)
    delete_button.grid(row=len(fields), column=1, pady=10, sticky='w')

    # Set the Edit_Window to None when it is closed
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

        # Extract QSO fields
        entry = {
            "Date": import_format_date(extract_field(record, "qso_date")) or "",
            "Time": import_format_time(extract_field(record, "time_on")) or "",
            "Callsign": (extract_field(record, "call") or "").upper(),
            "Name": (extract_field(record, "name") or ""),
            "My Callsign": (extract_field(record, "station_callsign") or "").upper(),
            "My Locator": ("").upper(),
            "My Location": ("").upper(),
            "Country": extract_field(record, "country") or "",
            "Continent": (extract_field(record, "cont") or "").upper(),
            "Sent": extract_field(record, "rst_sent") or "",
            "Received": extract_field(record, "rst_rcvd") or "",
            "Mode": extract_field(record, "mode") or "",
            "Submode": extract_field(record, "submode") or "",
            "Band": (extract_field(record, "band") or "").lower(),
            "Frequency": extract_field(record, "freq") or "",
            "Locator": (extract_field(record, "gridsquare") or "").upper(),
            "Comment": extract_field(record, "comment") or ""
        }

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


import os
import shutil
import subprocess

# Function to export JSON log file to ADIF format
def export_to_adif():
    global current_json_file, qso_lines

    if not current_json_file or not qso_lines:
        messagebox.showwarning("Warning", "No logbook file loaded or no QSO entries to export!")
        return

    # Ask the user for the output ADIF file location
    adif_file = filedialog.asksaveasfilename(defaultextension=".adi", filetypes=[("ADIF files", "*.adi")])
    if not adif_file:
        return  # User canceled the save dialog    

    try:
        # Write the ADIF file
        with open(adif_file, 'w') as file:
            for qso in qso_lines:
                # Prepare the ADIF record from the JSON data
                adif_record = []
                callsign = qso.get('Callsign', '')
                name = qso.get('Name', '')
                date = export_format_date(qso.get('Date', ''))
                time = export_format_time(qso.get('Time', ''))
                mode = qso.get('Mode', '')
                submode = qso.get('Submode', '')
                band = qso.get('Band', '')
                frequency = qso.get('Frequency', '')
                sent = qso.get('Sent', '')
                received = qso.get('Received', '')
                comment = qso.get('Comment', '')
                locator = qso.get('Locator', '')

                # Append the formatted fields to the record
                adif_record.append(f"<CALL:{len(callsign)}>{callsign}")
                adif_record.append(f"<NAME:{len(name)}>{name}")
                adif_record.append(f"<QSO_DATE:{len(date)}>{date}")
                adif_record.append(f"<TIME_ON:{len(time)}>{time}")
                adif_record.append(f"<MODE:{len(mode)}>{mode}")
                adif_record.append(f"<SUBMODE:{len(mode)}>{submode}")
                adif_record.append(f"<BAND:{len(band)}>{band}")
                adif_record.append(f"<FREQ:{len(frequency)}>{frequency}")
                adif_record.append(f"<RST_SENT:{len(sent)}>{sent}")
                adif_record.append(f"<RST_RCVD:{len(received)}>{received}")
                adif_record.append(f"<GRIDSQUARE:{len(locator)}>{locator}")
                adif_record.append(f"<COMMENT:{len(comment)}>{comment}")
                
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
    my_locator = my_locator_var.get().upper()
    my_location = my_location_var.get()
    country = country_var
    continent = continent_var
    rst_sent = rst_sent_var.get()
    rst_received = rst_received_var.get()
    band = band_var.get()
    mode = mode_var.get()
    submode = submode_var.get()
    comment = comment_var.get().strip()
    
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
        "My Locator": my_locator,
        "My Location": my_location,
        "Country": country,
        "Continent": continent,
        "Sent": rst_sent,
        "Received": rst_received,
        "Mode": mode,
        "Submode": submode,
        "Band": band,
        "Frequency": frequency,
        "Locator": locator,
        "Comment": comment        
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
    qso_entry = {
        "Date": import_format_date(extract_field(adif_record, "qso_date")) or "",
        "Time": time_field,
        "Callsign": callsign,
        "Name": name,
        "My Callsign": (extract_field(adif_record, "station_callsign") or "").upper(),
        "My Locator": (extract_field(adif_record, "my_gridsquare") or "").upper(),
        "My Location": "",
        "Country": (extract_field(adif_record, "country") or "").title(),
        "Continent": (extract_field(adif_record, "cont") or "").upper(),
        "Sent": (extract_field(adif_record, "rst_sent") or "").upper(),
        "Received": (extract_field(adif_record, "rst_rcvd") or "").upper(),
        "Mode": (extract_field(adif_record, "mode") or "").upper(),
        "Submode": (extract_field(adif_record, "submode") or "").upper(),
        "Band": (extract_field(adif_record, "band") or "").lower(),
        "Frequency": extract_field(adif_record, "freq") or "",
        "Locator": (extract_field(adif_record, "gridsquare") or "").upper(),
        "Comment": extract_field(adif_record, "comment") or ""
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
    """
    Toon een aangepaste messagebox die altijd boven alle vensters verschijnt en sluit na een bepaalde tijd.
    """
    # Maak een nieuw Tk venster
    temp_root = tk.Tk()
    temp_root.title(title)
    temp_root.geometry("300x100")  # Pas de grootte aan naar wens
    temp_root.resizable(False, False)

    # Zorg ervoor dat het venster altijd bovenaan blijft
    temp_root.attributes("-topmost", True)

    # Label voor het bericht
    message_label = tk.Label(temp_root, text=message, wraplength=280, justify="center")
    message_label.pack(expand=True, pady=20)

    # Sluit het venster na de opgegeven duur
    temp_root.after(duration, temp_root.destroy)

    # Start de Tk eventloop
    temp_root.mainloop()




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


# Function to retrieve available serial ports
def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def is_serial_port_available(port_name):
    available_ports = [port.device for port in serial.tools.list_ports.comports()]
    return port_name in available_ports

def connect_to_rigctld_threaded():
    """Start rigctld in a separate thread."""
    thread = threading.Thread(target=connect_to_rigctld, daemon=True)
    thread.start()

# Function to connect to rigctld
def connect_to_rigctld():
    global rigctld_process, socket_connection, serial_port, RIGCTLD_PORT, stop_frequency_thread
    
    stop_frequency_thread.clear()

    RIGCTLD_PORT    = config.get('Rigctld_settings', 'rigctld_port', fallback="4532")
    radio_model     = config.get('Rigctld_settings', 'rigctld_rig_model', fallback="--none--")  # Get Radio model from config.ini   
    radio_id        = rig_model.get(radio_model)                         # Match model iwht the model from rigs.ini and get ID
    serial_port     = config.get('Rigctld_settings', 'rigctld_rig_port', fallback="Select a port")
    baud_rate       = config.get('Rigctld_settings', 'rigctld_rig_baudrate', fallback="9600")
    polling_rate    = config.get('Rigctld_settings', 'rigctld_polling_rate', fallback="1000")
    connect_delay   = config.get('Rigctld_settings', 'rigctld_connect_delay', fallback="5000")
    data_bits       = config.get('Rigctld_settings', 'rigctld_data_bits', fallback=8)
    stop_bits       = config.get('Rigctld_settings', 'rigctld_stop_bits', fallback=1)
    handshake       = config.get('Rigctld_settings', 'rigctld_serial_handshake', fallback="--none--")
    rts_enabled     = config.get('Rigctld_settings', 'rigctld_rts', fallback="OFF")
    dtr_enabled     = config.get('Rigctld_settings', 'rigctld_dtr', fallback="OFF")

    try:
        if use_external_server.get():
            # Use External Server
            server_ip = external_server_ip.get()
            server_port = int(RIGCTLD_PORT)
            print(f"Connect to external rigctld-server at {server_ip}:{server_port}...")

            socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_connection.connect((server_ip, server_port))
            gui_state_control(11)  # Connected status

            # Start thread to update frequency and mode
            threading.Thread(target=update_frequency_and_mode_thread, daemon=True).start()

        else:

            def find_rigctld():
                # Determine the base directory: where the script or executable is located
                if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
                    base_dir = os.path.dirname(sys.executable)
                else:  # Running as a regular script
                    base_dir = os.path.dirname(os.path.abspath(__file__))

                # Construct the path to rigctld.exe in the "hamlib" folder
                rigctld_path = os.path.join(base_dir, "hamlib", "rigctld.exe")

                # Verify that the "hamlib" folder exists
                hamlib_folder_path = os.path.join(base_dir, "hamlib")
                if not os.path.exists(hamlib_folder_path):
                    disconnect_from_rigctld()
                    messagebox.showerror("Error", "The 'hamlib' folder is missing. Please ensure it is present.")
                    return None

                # Verify that the file exists and is executable
                if os.path.exists(rigctld_path) and os.access(rigctld_path, os.X_OK):
                    #print(f"Rigctld found: {rigctld_path}")
                    return rigctld_path
                else:
                    #print(f"ERROR: Rigctld not found or not executable at: {rigctld_path}")
                    return None

            # Use the function to find rigctld path
            rigctld_path = find_rigctld()
            if not rigctld_path:  # If rigctld is not found or folder is missing, exit the function
                return  # Exit early if rigctld_path is None


            if serial_port == "Select a port" or not serial_port:
                messagebox.showerror("Error", "Please select a valid serial port.")
                return

            gui_state_control(10) # Connecting status

            print(f"Rigctld Server Port: {RIGCTLD_PORT}\nRadio Model: {radio_model}\nRadio ID: {radio_id}\nSerial port: {serial_port}\nSpeed: {baud_rate}\nPolling rate: {polling_rate}\nData Bits:{data_bits}\nStop Bits:{stop_bits}\nHandshake: {handshake}\nRTS: {rts_enabled}\nDTR: {dtr_enabled}")

            startupinfo = None
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            rigctld_process = subprocess.Popen(
                
                [
                    rigctld_path, 
                    "-t", f"{RIGCTLD_PORT}",
                    "-m", str(radio_id), 
                    "-r", serial_port, 
                    "-s", baud_rate, 
                    "-C", "timeout=1000", 
                    "-C", "retry=3", 
                    "-C", f"poll_interval={polling_rate}",  # Use f-string for poll_interval
                    "-C", f"data_bits={data_bits},stop_bits={stop_bits},serial_handshake={handshake}", 
                    "-C", f"rts_state={rts_enabled},dtr_state={dtr_enabled}"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            print(f"Connect delay: {connect_delay}mS")
            root.after(connect_delay, establish_socket_connection)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to connect to rigctld: {e}")
        disconnect_from_rigctld()




# Function to establish socket connection after rigctld is started
def establish_socket_connection():
    global socket_connection, use_external_server
    try:
        if use_external_server.get():
            server_ip = external_server_ip.get()
            server_port = int(RIGCTLD_PORT)
            print(f"Connect to external rigctld-server at {server_ip}:{server_port}...")
            socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_connection.connect((server_ip, server_port))
        else:
            print("Connect to local rigctld-server...")
            socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_connection.connect(("localhost", int(RIGCTLD_PORT)))

        gui_state_control(11)  # Connected status
        threading.Thread(target=update_frequency_and_mode_thread, daemon=True).start()

    except socket.error as e:
        messagebox.showerror("Error", f"Can not connect!: {e}")
        disconnect_from_rigctld()





# Function to disconnect from rigctld
def disconnect_from_rigctld():
    global rigctld_process, socket_connection
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

    # Safely terminate rigctld process
    if rigctld_process:
        try:
            rigctld_process.terminate()
        except Exception as e:
            print(f"Error terminating rigctld process: {e}")  # Log the error
        finally:
            rigctld_process = None





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
        disconnect_from_rigctld()
        
    # Get the error message or fallback to a generic message
    error_message = error_messages.get(error_code, f"Unknown rigctld error (RPRT {error_code}).")
    messagebox.showerror("Rigctld Error", error_message)





# Function to update frequency and mode
stop_frequency_thread = threading.Event()  # Event to stop the thread

def update_frequency_and_mode_thread():
    global frequency_var, frequency_mhz, serial_port

    while not stop_frequency_thread.is_set():
        if not use_external_server.get():
            if not is_serial_port_available(serial_port):
                messagebox.showerror("Error", f"Serial port {serial_port} is no longer available.")
                disconnect_from_rigctld()  # Gracefully disconnect
                break

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
            frequency_var.set(f"{frequency_mhz:.4f}")

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
            mode_var.set(filtered_mode)

        except AttributeError:
            print("Socket connection was None during operation.")
            break  # Exit if the socket becomes invalid

        except socket.error as e:
            messagebox.showerror("Error", f"Socket communication error: {e}")
            disconnect_from_rigctld()
            break

        # Wait before the next update (polling interval in seconds)
        #time.sleep(0.1)  # Adjust this delay as needed







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

    # Load saved geometry
    load_window_position(Station_Setup_Window, "StationWindow")

  
    tk.Label(Station_Setup_Window, text="Station Setup", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan="2", padx=10, pady=1)

    my_callsign_var.trace("w", lambda *args: my_callsign_var.set(my_callsign_var.get().upper()))
    # Label & Entry for My Callsign
    tk.Label(Station_Setup_Window, text="My Callsign:", font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=1, sticky='w')
    tk.Entry(Station_Setup_Window, textvariable=my_callsign_var, font=('Arial', 10, 'bold')).grid(row=1, column=1, padx=10, pady=5, sticky='w')

    my_locator_var.trace("w", lambda *args: my_locator_var.set(my_locator_var.get().upper()))
    # Label & Entry for My Locator
    tk.Label(Station_Setup_Window, text="My Locator:", font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=1, sticky='w')
    tk.Entry(Station_Setup_Window, textvariable=my_locator_var, font=('Arial', 10, 'bold')).grid(row=2, column=1, padx=10, pady=5, sticky='w')

    # Label & Entry for My Location
    tk.Label(Station_Setup_Window, text="My Location:", font=('Arial', 10)).grid(row=3, column=0, padx=10, pady=1, sticky='w')
    tk.Entry(Station_Setup_Window, textvariable=my_location_var, font=('Arial', 10, 'bold')).grid(row=3, column=1, padx=10, pady=5, sticky='w')    

    def close_window():
        global Station_Setup_Window
        save_window_geometry(Station_Setup_Window, "StationWindow")
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
        close_window()

    tk.Button(Station_Setup_Window, text="Save & Exit", command=save_setup, width=10, height=2).grid(row=20, column=0, columnspan=2, padx=20, pady=10, sticky="w")
    tk.Button(Station_Setup_Window, text="Cancel", command=cancel_setup, width=10, height=2).grid(row=20, column=0, columnspan=2, padx=20, pady=10, sticky="e")
    
    # Handle window close event
    Station_Setup_Window.protocol("WM_DELETE_WINDOW", close_window)




# Function for Preference menu
def open_preferences():
    global Preference_Window, utc_offset_var, use_external_server, external_server_ip, server_port_var

    # Check if the window is already open
    if Preference_Window is not None and Preference_Window.winfo_exists():
        Preference_Window.lift()  # Bring the existing window to the front
        return

    Preference_Window = tk.Toplevel(root)
    Preference_Window.title("Preferences")
    Preference_Window.resizable(False, False)

    # Load saved geometry
    load_window_position(Preference_Window, "PreferenceWindow")

    # Load saved radio settings
    radio_model         = config.get('Rigctld_settings', 'rigctld_rig_model', fallback="--none--")
    server_port_var     = tk.StringVar(value=config.get('Rigctld_settings', 'rigctld_port', fallback=4532))
    use_external_server = tk.BooleanVar(value=config.getboolean('Rigctld_settings', 'rigctld_ext', fallback=False))
    external_server_ip  = tk.StringVar(value=config.get('Rigctld_settings', 'rigctld_ip', fallback="127.0.0.1"))
    serial_port         = config.get('Rigctld_settings', 'rigctld_rig_port', fallback="Select a port")
    baud_rate           = config.get('Rigctld_settings', 'rigctld_rig_baudrate', fallback=9600)
    polling_rate        = config.get('Rigctld_settings', 'rigctld_polling_rate', fallback=1000)
    connect_delay       = config.get('Rigctld_settings', 'rigctld_connect_delay', fallback=5000)
    data_bits_var       = config.get('Rigctld_settings', 'rigctld_data_bits', fallback=8)
    stop_bits_var       = config.get('Rigctld_settings', 'rigctld_stop_bits', fallback=1)
    handshake_var       = config.get('Rigctld_settings', 'rigctld_serial_handshake', fallback="None")
    rts_state           = config.get('Rigctld_settings', 'rigctld_rts', fallback="OFF")
    dtr_state           = config.get('Rigctld_settings', 'rigctld_dtr', fallback="OFF")
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

    tk.Label(Preference_Window, text="Hamlib Rigctld Setup", font=('Arial', 10, 'bold')).grid(row=6, column=0, columnspan="2", padx=10, pady=1)

    # Rigctld Server port
    tk.Label(Preference_Window, text="Port:").grid(row=7, column=0, padx=10, pady=1, sticky='w')
    server_port_var = tk.StringVar(value=config.get('Rigctld_settings', 'rigctld_port', fallback=4532))
    server_port_frame = tk.Frame(Preference_Window)
    for value in ["4532", "4536", "4538", "4540"]:
        tk.Radiobutton(server_port_frame, text=value, variable=server_port_var, value=value).pack(side=tk.LEFT)
    server_port_frame.grid(row=7, column=1, padx=10, pady=1, sticky='w')
    
    # Function for logging entries, comboboxes, checkboxes and radio buttons
    def toggle_external_server(ip_entry):
        if use_external_server.get():
            ip_entry.configure(state="normal")
            port_combobox.configure(state="disabled")
            baud_combobox.configure(state="disabled")
            radio_combobox.configure(state="disabled")
            polling_combobox.state(["disabled"])
            connect_delay_combobox.state(["disabled"])
            for radiobutton in data_bits_radiobuttons:
                radiobutton.configure(state="disabled")
            for radiobutton in stop_bits_radiobuttons:
                radiobutton.configure(state="disabled")
            for radiobutton in handshake_radiobuttons:
                radiobutton.configure(state="disabled")
            for checkbox in [rts_checkbutton, dtr_checkbutton]:
                checkbox.configure(state="disabled")
        else:
            ip_entry.configure(state="disabled")
            port_combobox.configure(state="normal")
            baud_combobox.configure(state="normal")
            radio_combobox.configure(state="normal")
            polling_combobox.state(["!disabled"])
            connect_delay_combobox.state(["!disabled"])
            for radiobutton in data_bits_radiobuttons:
                radiobutton.configure(state="normal")          
            for radiobutton in stop_bits_radiobuttons:
                radiobutton.configure(state="normal")
            for radiobutton in handshake_radiobuttons:
                radiobutton.configure(state="normal")
            for checkbox in [rts_checkbutton, dtr_checkbutton]:
                checkbox.configure(state="normal")                

   # Remote rigctld server settings
    tk.Label(Preference_Window, text="Use External Server:").grid(row=8, column=0, sticky="w", padx=10, pady=1)
    external_server_checkbox = tk.Checkbutton(Preference_Window, variable=use_external_server, command=lambda: toggle_external_server(ip_entry))
    external_server_checkbox.grid(row=8, column=1, sticky="w", padx=10, pady=1)

    tk.Label(Preference_Window, text="IP-address:").grid(row=9, column=0, sticky="w", padx=10, pady=1)
    ip_entry = tk.Entry(Preference_Window, textvariable=external_server_ip)
    ip_entry.grid(row=9, column=1, padx=10, pady=1, sticky="w")
    ip_entry.configure(state="disabled")

    tk.Label(Preference_Window, text="Radio Setup", font=('Arial', 10, 'bold')).grid(row=10, column=0, columnspan="2", padx=10, pady=1)

    # Radio selection
    tk.Label(Preference_Window, text="Select Radio:").grid(row=11, column=0, padx=10, pady=1, sticky='w')
    selected_radio = tk.StringVar(value=radio_model)
    radio_combobox = ttk.Combobox(Preference_Window, textvariable=selected_radio, values=list(rig_model.keys()), width=30)
    radio_combobox.set(radio_model)  # Set the selected radio
    radio_combobox.grid(row=11, column=1, padx=10, pady=1, sticky='w')


    tk.Label(Preference_Window, text="Serial Setup", font=('Arial', 10, 'bold')).grid(row=20, column=0, columnspan="2", padx=10, pady=1)

    # Serial port selection
    tk.Label(Preference_Window, text="Select Serial Port:").grid(row=21, column=0, padx=10, pady=1, sticky='w')
    port_combobox = ttk.Combobox(Preference_Window, values=get_serial_ports())
    port_combobox.set(serial_port)  # Set the selected port
    port_combobox.grid(row=21, column=1, padx=10, pady=1, sticky='w')

    # Baud rate selection
    tk.Label(Preference_Window, text="Baud Rate:").grid(row=22, column=0, padx=10, pady=1, sticky='w')
    baud_combobox = ttk.Combobox(Preference_Window, values=[4800, 9600, 19200, 38400, 57600, 115200])
    baud_combobox.set(baud_rate)  # Set the selected baud rate
    baud_combobox.grid(row=22, column=1, padx=10, pady=1, sticky='w')


    # Data bits radio buttons
    tk.Label(Preference_Window, text="Data Bits:").grid(row=23, column=0, padx=10, pady=1, sticky='w')
    data_bits_var = tk.StringVar(value=config.get('Rigctld_settings', 'rigctld_data_bits', fallback='8'))
    data_bits_frame = tk.Frame(Preference_Window)

    # Create individual Radiobuttons and pack them
    data_bits_radiobuttons = []  # List to store the Radiobutton widgets
    for value in ["7", "8"]:
        radiobutton = tk.Radiobutton(data_bits_frame, text=value, variable=data_bits_var, value=value)
        radiobutton.pack(side=tk.LEFT)
        data_bits_radiobuttons.append(radiobutton)  # Store each Radiobutton
    data_bits_frame.grid(row=23, column=1, padx=10, pady=1, sticky='w')

    # Stop bits radio buttons
    tk.Label(Preference_Window, text="Stop Bits:").grid(row=24, column=0, padx=10, pady=1, sticky='w')
    stop_bits_var = tk.StringVar(value=config.get('Rigctld_settings', 'rigctld_stop_bits', fallback='1'))
    stop_bits_frame = tk.Frame(Preference_Window)
    
    stop_bits_radiobuttons = []
    for value in ["1", "2"]:
        radiobutton = tk.Radiobutton(stop_bits_frame, text=value, variable=stop_bits_var, value=value)
        radiobutton.pack(side=tk.LEFT)
        stop_bits_radiobuttons.append(radiobutton)
    stop_bits_frame.grid(row=24, column=1, padx=10, pady=1, sticky='w')

    # Serial handshake radio buttons
    tk.Label(Preference_Window, text="Handshake:").grid(row=25, column=0, padx=10, pady=1, sticky='w')
    handshake_var = tk.StringVar(value=config.get('Rigctld_settings', 'rigctld_serial_handshake', fallback='None'))
    handshake_frame = tk.Frame(Preference_Window)
    handshake_radiobuttons = []
    for value in ["None", "RTS/CTS", "XON/XOFF"]:
        radiobutton = tk.Radiobutton(handshake_frame, text=value, variable=handshake_var, value=value)
        radiobutton.pack(side=tk.LEFT)
        handshake_radiobuttons.append(radiobutton)
    handshake_frame.grid(row=25, column=1, padx=10, pady=1, sticky='w')

    # RTS and DTR checkboxes
    tk.Label(Preference_Window, text="Serial Signals:").grid(row=26, column=0, padx=10, pady=1, sticky='w')
    rts_var = tk.StringVar(value=rts_state)
    rts_checkbutton = tk.Checkbutton(Preference_Window, text="RTS Enabled", variable=rts_var, onvalue="ON", offvalue="OFF")
    rts_checkbutton.grid(row=26, column=1, padx=10, sticky='w')

    dtr_var = tk.StringVar(value=dtr_state)
    dtr_checkbutton = tk.Checkbutton(Preference_Window, text="DTR Enabled", variable=dtr_var, onvalue="ON", offvalue="OFF")
    dtr_checkbutton.grid(row=27, column=1, padx=10, sticky='w')


    # Update rate selection
    tk.Label(Preference_Window, text="Update Rate (ms):").grid(row=28, column=0, padx=10, pady=1, sticky='w')
    polling_combobox = ttk.Combobox(Preference_Window, values=[100, 250, 500, 1000, 2000, 5000])
    polling_combobox.set(polling_rate)  # Set the selected polling rate
    polling_combobox.grid(row=28, column=1, padx=10, pady=1, sticky='w')

    # Connect Delay selection
    tk.Label(Preference_Window, text="Connect delay (ms):").grid(row=29, column=0, padx=10, pady=1, sticky='w')
    connect_delay_combobox = ttk.Combobox(Preference_Window, values=[100, 250, 500, 1000, 2000, 5000, 10000])
    connect_delay_combobox.set(connect_delay)  # Set the selected connection delay
    connect_delay_combobox.grid(row=29, column=1, padx=10, pady=1, sticky='w')

    tk.Label(Preference_Window, text="Increase delay with Bluetooth devices", font=('Arial', 8, 'bold')).grid(row=30, column=0, columnspan="2", padx=10, pady=1)

    separator = ttk.Separator(Preference_Window, orient='horizontal').grid(row=31, column=0, columnspan=2, sticky='ew', padx=10, pady=5)

    tk.Label(Preference_Window, text="QSO Reception using UDP (WSJT-X)", font=('Arial', 10, 'bold')).grid(row=40, column=0, columnspan="2", padx=10, pady=1)    

    # WSJT-X PORT
    wsjtx_port_var = tk.StringVar(value=wsjtx_port)
    tk.Label(Preference_Window, text="Port:").grid(row=41, column=0, padx=10, pady=1, sticky='e')
    wsjtx_port_entry = tk.Entry(Preference_Window, textvariable=wsjtx_port_var, width=10)
    wsjtx_port_entry.grid(row=41, column=1, padx=10, pady=1, sticky='w')

    separator = ttk.Separator(Preference_Window, orient='horizontal').grid(row=50, column=0, columnspan=2, sticky='ew', padx=10, pady=5)


    # Function to enable/disable port and baud comboboxes
    def toggle_comboboxes(*args):
        if selected_radio.get() == "--none--":
            port_combobox.state(["disabled"])
            baud_combobox.state(["disabled"])
            polling_combobox.state(["disabled"])
            connect_delay_combobox.state(["disabled"])
        else:
            port_combobox.state(["!disabled"])
            baud_combobox.state(["!disabled"])
            polling_combobox.state(["!disabled"])
            connect_delay_combobox.state(["!disabled"])



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
    
    selected_radio.trace_add('write', toggle_comboboxes) # Attach the toggle function to the radio combobox variable


    toggle_comboboxes()     # Initialize the state of comboboxes
    
    toggle_external_server(ip_entry) # Start init state of fields

    def close_window():
        global Preference_Window
        save_window_geometry(Preference_Window, "PreferenceWindow")
        Preference_Window.destroy()
        Preference_Window = None

    # Save button
    def save_preferences():
        
        radio_model = radio_combobox.get()
        if radio_model == "--none--" and not use_external_server.get():
            tracking_menu.entryconfig("Radio Frequency & Mode", state="disabled")
            gui_state_control(20) # No radio availabe status
        else:
            tracking_menu.entryconfig("Radio Frequency & Mode", state="normal")
            gui_state_control(12) # Disconnect status
        
        radio_id = rig_model.get(radio_model)
        
        # Only save the 'reload_last_logbook' if the key exists in the config
        if 'reload_last_logbook' in config['General']:
            # Save Reload Last Logbook preference only if a logbook is loaded
            if current_json_file:
                config['General']['reload_last_logbook'] = str(reload_last_logbook_var.get())
            else:
                # Ensure the setting is reset if no logbook is loaded
                config['General']['reload_last_logbook'] = "False"
        config['Global_settings']['utc_offset'] = utc_offset_var.get()
        config['Rigctld_settings']['rigctld_port'] = server_port_var.get()
        config['Rigctld_settings']['rigctld_ip'] = external_server_ip.get()
        config['Rigctld_settings']['rigctld_ext'] = str(use_external_server.get())
        config['Rigctld_settings']['rigctld_rig_model'] = radio_model
        config['Rigctld_settings']['rigctld_rig_id'] = str(radio_id)  # Save radio ID
        config['Rigctld_settings']['rigctld_rig_port'] = port_combobox.get()
        config['Rigctld_settings']['rigctld_rig_baudrate'] = baud_combobox.get()
        config['Rigctld_settings']['rigctld_data_bits'] = data_bits_var.get()
        config['Rigctld_settings']['rigctld_stop_bits'] = stop_bits_var.get()
        config['Rigctld_settings']['rigctld_serial_handshake'] = handshake_var.get()
        config['Rigctld_settings']['rigctld_polling_rate'] = polling_combobox.get()
        config['Rigctld_settings']['rigctld_connect_delay'] = connect_delay_combobox.get()
        config["Rigctld_settings"]['rigctld_rts'] = str(rts_var.get())
        config["Rigctld_settings"]['rigctld_dtr'] = str(dtr_var.get())
        config["Wsjtx_settings"]['wsjtx_port'] = str(wsjtx_port_var.get())
        
        file_path = data_directory / CONFIG_FILE
        with open(file_path, 'w') as configfile:
            config.write(configfile)        
        
        #save_config(server_port_var, external_server_ip, use_external_server, radio_combobox, port_combobox, baud_combobox, polling_combobox, connect_delay_combobox, data_bits_var, stop_bits_var, handshake_var, rts_var, dtr_var, wsjtx_port_var)
        update_datetime()
        disconnect_from_rigctld()
        restart_listener(config)
        close_window()

    def cancel_preferences():
        close_window()

    tk.Button(Preference_Window, text="Save & Exit", command=value_check, width=10, height=2).grid(row=51, column=0, columnspan=2, padx=20, pady=10, sticky="w")
    tk.Button(Preference_Window, text="Cancel", command=cancel_preferences, width=10, height=2).grid(row=51, column=0, columnspan=2, padx=20, pady=10, sticky="e")

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
    file_path = data_directory / CONFIG_FILE

    # Check if the file exists; if not, create it with default sections and keys
    if not os.path.exists(file_path):
        print("Configuration file not found. Creating a new one with default values.")
        config['Global_settings'] = {}
        config['General'] = {}
        config['Rigctld_settings'] = {}
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

    # Rigctld_settings
    if 'Rigctld_settings' not in config:
        config.add_section('Rigctld_settings')
    if 'rigctld_port' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_port'] = '4532'
    if 'rigctld_ip' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_ip'] = '127.0.0.1'
    if 'rigctld_ext' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_ext'] = 'False'
    if 'rigctld_rig_model' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_rig_model'] = 'None'
    if 'rigctld_rig_id' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_rig_id'] = '0000'
    if 'rigctld_rig_port' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_rig_port'] = ''
    if 'rigctld_rig_baudrate' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_rig_baudrate'] = '115200'
    if 'rigctld_polling_rate' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_polling_rate'] = '1000'
    if 'rigctld_connect_delay' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_connect_delay'] = '5000'
    if 'rigctld_data_bits' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_data_bits'] = '8'
    if 'rigctld_stop_bits' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_stop_bits'] = '1'
    if 'rigctld_serial_handshake' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_serial_handshake'] = 'None'
    if 'rigctld_rts' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_rts'] = 'OFF'
    if 'rigctld_dtr' not in config['Rigctld_settings']:
        config['Rigctld_settings']['rigctld_dtr'] = 'OFF'

    # Wsjtx_settings
    if 'Wsjtx_settings' not in config:
        config.add_section('Wsjtx_settings')
    if 'wsjtx_port' not in config['Wsjtx_settings']:
        config['Wsjtx_settings']['wsjtx_port'] = '2333'

    # Save the updated config if any changes were made
    with open(file_path, 'w') as configfile:
        config.write(configfile)




def load_station_setup():
    # Load station details from JSON logbook if the file is loaded
    if current_json_file and os.path.exists(current_json_file):
        try:
            with open(current_json_file, 'r', encoding='utf-8') as file:
                logbook_data = json.load(file)
                station_info = logbook_data.get("Station", {})
                my_callsign_var.set(station_info.get("Callsign", "N0CALL"))
                my_locator_var.set(station_info.get("Locator", "JO22LO"))
                my_location_var.set(station_info.get("Location", ""))
                my_callsign_label.config(textvariable=my_callsign_var)
                my_locator_label.config(textvariable=my_locator_var)
                my_location_label.config(textvariable=my_location_var)
        except (json.JSONDecodeError, KeyError) as e:
            messagebox.showerror("Error", f"Failed to load station details from logbook: {e}")




  

# Functie om rigs.ini in te lezen
def load_rigs():
    rigs = {}

    file_path = RIGS_FILE
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    model, model_id = line.split(':')
                    rigs[model.strip()] = int(model_id.strip())
    return rigs


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
                    "Locator": my_locator_var.get().upper(),
                    "Location" : my_location_var.get()
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
                    loaded_file_label.config(text=os.path.basename(current_json_file), fg='blue')
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
#  ___ _   _ _  _  ___ _____ ___ ___  _  _ ___ 
# | __| | | | \| |/ __|_   _|_ _/ _ \| \| / __|
# | _|| |_| | .` | (__  | |  | | (_) | .` \__ \
# |_|  \___/|_|\_|\___| |_| |___\___/|_|\_|___/
#                                              
#########################################################################################

# Function to reset variables and entries when logbook file failed to load.
def no_file_loaded():
    global current_json_file

    current_json_file = None # Reset the current_json_file to None
    loaded_file_label.config(text="Load or create logbook first!", fg='red')
    my_locator_var.set("")
    my_callsign_var.set("")
    my_location_var.set("")
    my_callsign_label.config(textvariable=my_locator_var)
    my_locator_label.config(textvariable=my_callsign_var)
    my_location_label.config(textvariable=my_location_var)
    file_menu.entryconfig("Station setup", state="disabled")


# Functie to restore fields after logging
def reset_fields():
    comment_var.set("")
    last_qso_label.config(text="") 
    callsign_var.set("")
    name_var.set("")
    rst_sent_var.set("59")
    rst_received_var.set("59")
    locator_var.set("")    
    callsign_entry.focus_set() # Set focus to the callsign entry field


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
        #file_path = data_directory / DXCC_FILE
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



# Function to update radio status
# 0 = dummy
# 10 = connecting
# 11 = connected
# 12 = disconnected
# 20 = noradio
def gui_state_control(status):
    global radio_status_var, use_external_server, external_server_ip, server_port_var


    if status == 10:
        radio_status_var.set("Connecting...")
        radio_status_label.config(fg="blue")

    elif status == 11:
        radio_model = config['Rigctld_settings']['rigctld_rig_model']

        if use_external_server.get():
            radio_status_var.set(f"Connected to {external_server_ip.get()}:{server_port_var.get()}")
            radio_status_label.config(fg="green")
        else:
            radio_status_var.set(f"Connected to {radio_model}")
            radio_status_label.config(fg="green")

        freq_entry.config(fg="red", state='readonly')
        band_combobox.config(state='disabled')        

    elif status == 12:
        radio_status_var.set("Disconnected")
        radio_status_label.config(fg="red")
        freq_entry.config(fg="black", state='normal')
        band_combobox.config(state='normal')
  
    elif status == 20:
        radio_status_var.set("Not available")
        radio_status_label.config(fg="grey")
  
    else:  # Default to idle or unknown state
        radio_status_var.set("Idle")
        radio_status_label.config(fg="gray")




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

    # Load saved geometry
    load_window_position(About_Window, "AboutWindow")        


    tk.Label(About_Window, text="MiniBook", font=('Arial', 20, 'bold')).pack(pady=10)
    separator = tk.Frame(About_Window, height=2, bd=0, relief='sunken', bg='gray')
    separator.pack(fill='x', pady=5, padx=10)
    tk.Label(About_Window, text=f"Version {VERSION_NUMBER}\n\nA Simple JSON Logbook\n\nDeveloped by:\nBjörn Pasteuning\nPD5DJ\n\nCopyright 2024", font=('Arial', 10)).pack(pady=10)

    url = "https://www.pd5dj.nl"
    link = tk.Label(About_Window, text=url, fg="blue", cursor="hand2", font=('Arial', 10))
    link.pack(pady=10)
    link.bind("<Button-1>", lambda e: webbrowser.open(url))
    
    def close_window():
        global About_Window
        save_window_geometry(About_Window, "AboutWindow")
        About_Window.destroy()
        About_Window = None

    tk.Button(About_Window, text="Close", command=close_window).pack(pady=10)
    
    # Handle window close event
    About_Window.protocol("WM_DELETE_WINDOW", close_window)    





# Function called beginning at start of program
def init():
    global use_external_server, external_server_ip, server_port_var, prefixes

    # Creating & loading of config.ini
    load_config()
    no_file_loaded() # Checks if no logbook is loaded
    prefixes = fetch_prefixes() # Initialize prefixes
    update_frequency_from_band() # Update Band to Frequency on Startup
    display_image(0, dxcc_image_label, FLAG_IMAGE_WIDTH , FLAG_IMAGE_HEIGHT) # Empty image
    start_listener(config)
    update_datetime()
    utc_offset_var.set(config.get('Global_settings', 'utc_offset', fallback='0'))
    external_server_ip  = tk.StringVar(value=config.get('Rigctld_settings', 'rigctld_ip', fallback="127.0.0.1"))
    server_port_var     = tk.StringVar(value=config.get('Rigctld_settings', 'rigctld_port', fallback=4532))
    radio_model = config.get('Rigctld_settings', 'rigctld_rig_model', fallback="--none--")
    use_external_server = tk.BooleanVar(value=config.getboolean('Rigctld_settings', 'rigctld_ext'))
    callsign_entry.focus_set() # Set focus to the callsign entry field

    if radio_model == "--none--" and not use_external_server.get():
        tracking_menu.entryconfig("Radio Frequency & Mode", state="disabled")
        gui_state_control(20) # No radio availabe status
    else:
        tracking_menu.entryconfig("Radio Frequency & Mode", state="normal")
        gui_state_control(12) # Disconnect status

    load_last_logbook_on_startup()


# Save geometries for root and Logbook_Window
def save_window_geometry(window, name):
    """
    Save a specific window's geometry to the configuration file.
    """
    if window.winfo_exists():
        config = configparser.ConfigParser()
        file_path = data_directory / CONFIG_FILE
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
    file_path = data_directory / CONFIG_FILE
    if os.path.exists(file_path):
        config = configparser.ConfigParser()
        config.read(file_path)
        if name in config and "geometry" in config[name]:
            window.geometry(config[name]["geometry"])
            

def load_window_position(window, name):
    """
    Load the position for a specific window, keeping its size unchanged.
    """
    file_path = data_directory / CONFIG_FILE
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
        disconnect_from_rigctld()
        # Terminate rigctld if it’s running
        if rigctld_process and rigctld_process.poll() is None:
            
            rigctld_process.terminate()  # Gracefully terminate
            try:
                rigctld_process.wait(timeout=5)  # Wait for the process to terminate
            except subprocess.TimeoutExpired:
                rigctld_process.kill()  # Force kill if it didn’t terminate in time

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
        #file_path = data_directory / DXCC_FILE
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
            country_label.config(text="Not Found")
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
            print(f"Fout bij herladen logboek: {e}")
            return

    entered_call = callsign_var.get().strip().upper()
    if not entered_call or len(entered_call) < 3:
        workedb4_tree.delete(*workedb4_tree.get_children())
        return

    matches = [qso for qso in qso_lines if qso.get("Callsign", "").upper() == entered_call]

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
            qso.get("Frequency", ""),
            qso.get("Mode", ""),
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
root.title(f"MiniBook - {VERSION_NUMBER}")
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
locator_var = tk.StringVar()
my_locator_var = tk.StringVar()
my_location_var = tk.StringVar()
my_callsign_var = tk.StringVar()
country_var = tk.StringVar()
continent_var = tk.StringVar()
rst_sent_var = tk.StringVar(value="59")
rst_received_var = tk.StringVar(value="59")
comment_var = tk.StringVar()
frequency_var = tk.StringVar()
band_var = tk.StringVar(value="20m")
mode_var = tk.StringVar(value="USB")
submode_var = tk.StringVar(value="")
utc_offset_var = tk.StringVar(value="0")
radio_status_var = tk.StringVar()
datetime_tracking_enabled = tk.BooleanVar(value=True)  # Enabled by default
freqmode_tracking_var = tk.BooleanVar(value=False)

# Preparation of Rigctld in Threaded mode
rig_model = load_rigs()
rigctld_process = None
socket_connection = None


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
        connect_to_rigctld_threaded()
        toggle_freq_mode
    else:
        disconnect_from_rigctld()


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

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Update DXCC lookup file", command=download_json_file)
help_menu.add_separator()
help_menu.add_command(label="About", command=show_about)
menu_bar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menu_bar)

     

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



# Set the width for columns 0 and 1
root.grid_columnconfigure(0, weight=0, minsize=50)
root.grid_columnconfigure(1, weight=0, minsize=50)
root.grid_columnconfigure(2, weight=0, minsize=50)
root.grid_columnconfigure(3, weight=0, minsize=50)
root.grid_columnconfigure(4, weight=0, minsize=50)
root.grid_columnconfigure(5, weight=0, minsize=50)
root.grid_columnconfigure(5, weight=0, minsize=50)


#------------- Field/Label positions Row/Column/Span --------------
Seperator_0_row                 = 1
Seperator_0_col                 = 0
Seperator_0_colspan             = 7

Seperator_1_row                 = 3
Seperator_1_col                 = 0
Seperator_1_colspan             = 7

Seperator_2_row                 = 10
Seperator_2_col                 = 0
Seperator_2_colspan             = 7


radio_status_header_row        = 0
radio_status_header_col        = 3
radio_status_header_colspan    = 1
radio_status_row               = 0
radio_status_col               = 4
radio_status_colspan           = 3

File_header_row                = 0
File_header_col                = 0
File_header_colspan            = 1
File_row                       = 0
File_col                       = 1
File_colspan                   = 2

my_callsign_header_row         = 2
my_callsign_header_col         = 0
my_callsign_header_colspan     = 1
my_callsign_row                = 2
my_callsign_col                = 1
my_callsign_colspan            = 1

my_locator_header_row          = 2
my_locator_header_col          = 2
my_locator_header_colspan      = 1
my_locator_row                 = 2
my_locator_col                 = 3
my_locator_colspan             = 1

my_location_header_row         = 2
my_location_header_col         = 4
my_location_header_colspan     = 1
my_location_row                = 2
my_location_col                = 5
my_location_colspan            = 2

Date_header_row                = 4
Date_header_col                = 2
Date_header_colspan            = 1
Date_row                       = 4
Date_col                       = 3
Date_colspan                   = 1

Time_header_row                = 4
Time_header_col                = 4
Time_header_colspan            = 1
Time_row                       = 4
Time_col                       = 5
Time_colspan                   = 1

Callsign_header_row            = 4
Callsign_header_col            = 0
Callsign_header_colspan        = 1
Callsign_row                   = 4
Callsign_col                   = 1
Callsign_colspan               = 1

Name_header_row                = 5
Name_header_col                = 0
Name_header_colspan            = 1
Name_row                       = 5
Name_col                       = 1
Name_colspan                   = 1

Last_qso_header_row            = 4
Last_qso_header_col            = 4
Last_qso_header_colspan        = 1
Last_qso_row                   = 11
Last_qso_col                   = 0
Last_qso_colspan               = 3

RST_sent_header_row            = 5
RST_sent_header_col            = 2
RST_sent_header_colspan        = 1
RST_sent_row                   = 5
RST_sent_col                   = 3
RST_sent_colspan               = 1

RST_rcvd_header_row            = 5
RST_rcvd_header_col            = 4
RST_rcvd_header_colspan        = 1
RST_rcvd_row                   = 5
RST_rcvd_col                   = 5
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

Submode_header_row             = 7
Submode_header_col             = 2
Submode_header_colspan         = 1
Submode_row                    = 7
Submode_col                    = 3
Submode_colspan                = 1

Band_header_row                = 7
Band_header_col                = 0
Band_header_colspan            = 1
Band_row                       = 7
Band_col                       = 1
Band_colspan                   = 1

Freq_header_row                = 8
Freq_header_col                = 0
Freq_header_colspan            = 1
Freq_row                       = 8
Freq_col                       = 1
Freq_colspan                   = 1

Comment_header_row             = 9
Comment_header_col             = 0
Comment_header_colspan         = 1
Comment_row                    = 9
Comment_col                    = 1
Comment_colspan                = 4

Log_button_row                 = 8
Log_button_col                 = 5
Log_button_colspan             = 1
Log_button_rowspan             = 2

Wipe_button_row                = 6
Wipe_button_col                = 5
Wipe_button_colspan            = 1
Wipe_button_rowspan            = 2


DXCC_Info_row                  = 11
DXCC_Info_col                  = 0
DXCC_Info_colspan              = 7

DXCC_image_row                 = 8
DXCC_image_col                 = 1
DXCC_image_colspan             = 1
DXCC_image_rowspan             = 1

Country_row                    = 8
Country_col                    = 2
Country_colspan                = 3

y_padding                      = 2


   
# RADIO STATUS
tk.Label(root, text="Radio status:", font=('Arial', 10)).grid(row=radio_status_header_row, column=radio_status_header_col, columnspan=radio_status_header_colspan, padx=5, pady=0, sticky='e')
radio_status_label = tk.Label(root, textvariable=radio_status_var, font=('Arial', 10, 'bold'))
radio_status_label.grid(row=radio_status_row, column=radio_status_col, columnspan=radio_status_colspan, padx=5, pady=0, sticky='w')

# ---------------------
separator = ttk.Separator(root, orient='horizontal')
separator.grid(row=Seperator_0_row, column=Seperator_0_col, columnspan=Seperator_0_colspan, sticky='ew', padx=5, pady=0)

# LOGBOOK FILE
tk.Label(root, text="Logbook File:", font=('Arial', 10)).grid(row=File_header_row, column=File_header_col, columnspan=File_header_colspan, padx=5, pady=0, sticky='e')
loaded_file_label = tk.Label(root, font=('Arial', 10, 'bold'))
loaded_file_label.grid(row=File_row, column=File_col, columnspan=File_colspan, padx=5, pady=0, sticky='w')

# MY CALLSIGN
tk.Label(root, text="My Callsign:", font=('Arial', 10)).grid(row=my_callsign_header_row, column=my_callsign_header_col, columnspan=my_callsign_header_colspan, padx=5, pady=0, sticky='e')
my_callsign_label = tk.Label(root, font=('Arial', 10, 'bold'))
my_callsign_label.grid(row=my_callsign_row, column=my_callsign_col, columnspan=my_callsign_colspan, padx=5, pady=0, sticky='w')

# MY LOCATOR
tk.Label(root, text="My Locator:", font=('Arial', 10)).grid(row=my_locator_header_row, column=my_locator_header_col, columnspan=my_locator_header_colspan, padx=5, pady=0, sticky='e')
my_locator_label = tk.Label(root, font=('Arial', 10, 'bold'))
my_locator_label.grid(row=my_locator_row, column=my_locator_col, columnspan=my_locator_colspan, padx=5, pady=0, sticky='w')

# MY LOCATION
tk.Label(root, text="My Location:", font=('Arial', 10)).grid(row=my_location_header_row, column=my_location_header_col, columnspan=my_location_header_colspan, padx=5, pady=0, sticky='e')
my_location_label = tk.Label(root, font=('Arial', 10, 'bold'))
my_location_label.grid(row=my_location_row, column=my_location_col, columnspan=my_location_colspan, padx=5, pady=0, sticky='w')

# ---------------------
separator = ttk.Separator(root, orient='horizontal')
separator.grid(row=Seperator_1_row, column=Seperator_1_col, columnspan=Seperator_1_colspan, sticky='ew', padx=5, pady=y_padding)

# DATE
tk.Label(root, text="QSO Date:", font=('Arial', 10)).grid(row=Date_header_row, column=Date_header_col, columnspan=Date_header_colspan, padx=5, pady=y_padding, sticky='e')
date_entry = DateEntry(root, textvariable=date_var, date_pattern='yyyy-mm-dd', font=('Arial', 10, 'bold'))
date_entry.grid(row=Date_row, column=Date_col, columnspan=Date_colspan, padx=5, pady=y_padding, sticky='w')

# TIME
tk.Label(root, text="QSO Time:", font=('Arial', 10)).grid(row=Time_header_row, column=Time_header_col, columnspan=Time_header_colspan, padx=5, pady=y_padding, sticky='e')
time_entry = tk.Entry(root, textvariable=time_var, font=('Arial', 10, 'bold'), width=10)
time_entry.grid(row=Time_row, column=Time_col, columnspan=Time_colspan, padx=5, pady=y_padding, sticky='w')

# CALLSIGN
tk.Label(root, text="Callsign:", font=('Arial', 10)).grid(row=Callsign_header_row, column=Callsign_header_col, columnspan=Callsign_header_colspan, padx=5, pady=y_padding, sticky='e')
callsign_entry = tk.Entry(root, textvariable=callsign_var, font=('Arial', 10, 'bold'))
callsign_entry.grid(row=Callsign_row, column=Callsign_col, columnspan=Callsign_colspan, padx=5, pady=y_padding, sticky='w')

# NAME
tk.Label(root, text="Name:", font=('Arial', 10)).grid(row=Name_header_row, column=Name_header_col, columnspan=Name_header_colspan, padx=5, pady=y_padding, sticky='e')
name_entry = tk.Entry(root, textvariable=name_var, font=('Arial', 10, 'bold'))
name_entry.grid(row=Name_row, column=Name_col, columnspan=Name_colspan, padx=5, pady=y_padding, sticky='w')

# SENT
tk.Label(root, text="RST Sent:", font=('Arial', 10)).grid(row=RST_sent_header_row, column=RST_sent_header_col, columnspan=RST_sent_header_colspan, padx=5, pady=y_padding, sticky='e')
rst_sent_combobox = ttk.Combobox(root, textvariable=rst_sent_var, values=rst_options, font=('Arial', 10, 'bold'), width=8)
rst_sent_combobox.grid(row=RST_sent_row, column=RST_sent_col, columnspan=RST_sent_colspan, padx=5, pady=y_padding, sticky='w')

# RECEIVED
tk.Label(root, text="RST Received:", font=('Arial', 10)).grid(row=RST_rcvd_header_row, column=RST_rcvd_header_col, columnspan=RST_rcvd_header_colspan,  padx=5, pady=y_padding, sticky='e')
rst_received_combobox = ttk.Combobox(root, textvariable=rst_received_var, values=rst_options, font=('Arial', 10, 'bold'), width=8)
rst_received_combobox.grid(row=RST_rcvd_row, column=RST_rcvd_col, columnspan=RST_rcvd_colspan, padx=5, pady=y_padding, sticky='w')

# LOCATOR
tk.Label(root, text="Locator:", font=('Arial', 10)).grid(row=Locator_header_row, column=Locator_header_col, columnspan=Locator_header_colspan,  padx=5, pady=y_padding, sticky='e')
tk.Entry(root, textvariable=locator_var, font=('Arial', 10, 'bold')).grid(row=Locator_row, column=Locator_col, columnspan=Locator_colspan,  padx=5, pady=y_padding, sticky='w')
locator_var.trace("w", lambda *args: locator_var.set(locator_var.get().upper()))

# MODE
tk.Label(root, text="Mode:", font=('Arial', 10)).grid(row=Mode_header_row, column=Mode_header_col, columnspan=Mode_header_colspan,  padx=5, pady=y_padding, sticky='e')
mode_combobox = ttk.Combobox(root, textvariable=mode_var, values=mode_options, font=('Arial', 10, 'bold'), width=8, state='readonly')
mode_combobox.grid(row=Mode_row, column=Mode_col, columnspan=Mode_colspan, padx=5, pady=y_padding, sticky='w')

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
freq_entry.bind("<KeyPress>", on_keypress)  # Bind keypress to allow numbers and one decimal point
frequency_var.trace("w", update_band_from_frequency) # Bind frequency input to update the band if the frequency is outside the selected band

# COMMENT
tk.Label(root, text="Comment:", font=('Arial', 10)).grid(row=Comment_header_row, column=Comment_header_col, columnspan=Comment_header_colspan, padx=5, pady=y_padding, sticky='e')
tk.Entry(root, textvariable=comment_var, font=('Arial', 10, 'bold')).grid(row=Comment_row, column=Comment_col, columnspan=Comment_colspan, padx=5, pady=y_padding, sticky='ew')

# IMAGE
dxcc_image_label = tk.Label(root,anchor='e')
dxcc_image_label.grid(row=DXCC_image_row, column=DXCC_image_col, columnspan=DXCC_image_colspan, rowspan=DXCC_image_rowspan, sticky='e', padx=5)

# COUNTRY, CONTINENT
country_label = tk.Label(root, font=('Arial', 9, 'bold'),anchor='w')
country_label.grid(row=Country_row, column=Country_col, columnspan=Country_colspan, sticky='w')

# LOG BUTTON
log_button = tk.Button(root, text="Log QSO\nF5", command=log_qso, bd=3, relief='raised',width=10, height=2, bg='green', fg='white', font=('Arial', 10, 'bold'))
log_button.grid(row=Log_button_row, column=Log_button_col, columnspan=Log_button_colspan, rowspan=Log_button_rowspan, padx=15, pady=10, sticky='w')

# WIPE BUTTON
wipe_button = tk.Button(root, text="Wipe\nF1", command=reset_fields, bd=3, relief='raised',width=10, height=2, bg='grey', fg='white', font=('Arial', 10, 'bold'))
wipe_button.grid(row=Wipe_button_row, column=Wipe_button_col, columnspan=Wipe_button_colspan, rowspan=Wipe_button_rowspan, padx=15, pady=10, sticky='w')

# ---------------------
separator = ttk.Separator(root, orient='horizontal')
separator.grid(row=Seperator_2_row, column=Seperator_2_col, columnspan=Seperator_2_colspan, sticky='ew', padx=5)

# LAST QSO
last_qso_label = tk.Label(root, fg="blue", padx=5, pady=y_padding, font=('Arial', 8, 'bold'))
last_qso_label.grid(row=Last_qso_row, column=Last_qso_col, columnspan=Last_qso_colspan,padx=5, sticky='w')


# DXCC INFO
dxcc_cqitu = tk.Label(root, font=('Arial', 8))
dxcc_cqitu.grid(row=DXCC_Info_row, column=DXCC_Info_col, columnspan=DXCC_Info_colspan, padx=5,  sticky='e')





#----------- WORKED BEFORE FRAME ------------
bg_color = root.cget("bg")

workedb4_frame = tk.Frame(workedb4_window, bg=bg_color)
workedb4_frame.grid(row=10, column=0, columnspan=99, sticky="nsew", pady=(10, 0))
root.grid_rowconfigure(10, weight=1)
root.grid_columnconfigure(0, weight=1)


title_label = tk.Label(workedb4_frame, text="Worked before result", font=('Arial', 11, 'bold'), bg=bg_color)
title_label.pack(anchor="center", padx=10, pady=(5, 0))

tree_frame = tk.Frame(workedb4_frame)
tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

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


# Call init function to Preset / Preload  variables / Tasks
init()

# Bind the on_close function to the "X" button
root.protocol("WM_DELETE_WINDOW", exit_program)

# Start main loop
root.mainloop()
