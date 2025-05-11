#**********************************************************************************************************************************
# File          :   BulkEditor
# Project       :   A Simple JSON Based logbook bulk editor for portable use.
# Description   :   Bulk edit of contact information, multiple field editting
# Date          :   18-10-2024
# Authors       :   Bjorn Pasteuning - PD5DJ
# Website       :   https://wwww.pd5dj.nl
#
# Version history
#  13-11-2024   :   1.0.2   - Row colors fixed when Searching/Sorting
#  20-11-2024   :   1.0.3   - Submode added
#  27-11-2024   :   1.0.4   - Name added
#  03-05-2025   :   1.0.5   - Satellite field added.
#                           - Date & Time sorting fixed
#  09-05-2025   :   1.0.6   - Dupe check added
#                           - Search function added
#**********************************************************************************************************************************

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry  # Import DateEntry for the date picker
from datetime import datetime
import json
import re

VERSION_NUMBER = "1.0.6"
data = {"Station": {}, "Logbook": []}
logbook_file_path = None
file_name_var = None





def search_treeview():
    search_term = search_var.get().strip().lower()

    # Clear all items from Treeview
    bulk_tree.delete(*bulk_tree.get_children())

    if not search_term:
        # Geen zoekterm: toon alle QSOs
        filtered_qsos = list(enumerate(data["Logbook"]))
    else:
        filtered_qsos = []
        for idx, qso in enumerate(data["Logbook"]):
            # Controleer of zoekterm in een van de waarden zit (geconverteerd naar string en lowercase)
            if any(search_term in str(value).lower() for value in qso.values()):
                filtered_qsos.append((idx, qso))

    # Voeg de (gefilterde) QSOs toe
    for new_idx, (original_idx, qso) in enumerate(filtered_qsos):
        row_tag = "oddrow" if new_idx % 2 == 0 else "evenrow"
        bulk_tree.insert("", "end", iid=original_idx, values=(
            qso.get('Date', ''),
            qso.get('Time', ''),
            qso.get('Callsign', '').upper(),
            qso.get('Name', ''),
            qso.get('Mode', '').upper(),
            qso.get('Submode', '').upper(),
            qso.get('Band', '').lower(),
            qso.get('Frequency', ''),
            qso.get('Sent', ''),
            qso.get('Received', ''),
            qso.get('Locator', '').upper(),
            qso.get('Comment', ''),
            qso.get('WWFF', ''),
            qso.get('POTA', ''),
            qso.get('Country', ''),
            qso.get('Continent', '').upper(),
            qso.get('My Callsign', '').upper(),
            qso.get('My Operator', '').upper(),
            qso.get('My Locator', '').upper(),
            qso.get('My Location', ''),
            qso.get('My WWFF', ''),
            qso.get('My POTA', ''),
            qso.get('Satellite', '')
        ), tags=(row_tag,))
        

def bulk_edit_window():
    global root, search_var, bulk_tree, file_name_var
    root = tk.Tk()
    root.title(f"MiniBook Logbook Bulk Editor - v{VERSION_NUMBER}")

    # Hoofdcontainer
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)

    file_name_var = tk.StringVar()
    file_name_var.set("No file loaded")

    file_label = tk.Label(frame, textvariable=file_name_var, font=("Arial", 12, "bold italic"))
    file_label.pack(pady=(5, 0))


    # Eerste rij: Open en Save (gecentreerd)
    top_button_frame = tk.Frame(frame)
    top_button_frame.pack(pady=(10, 0))

    file_button = tk.Button(top_button_frame, text="Open Logbook File", command=open_logbook_file)
    file_button.pack(side=tk.LEFT, padx=5)

    save_button = tk.Button(top_button_frame, text="Save Logbook", command=save_logbook)
    save_button.pack(side=tk.LEFT, padx=5)

    # Tweede rij: Find Duplicates (gecentreerd)
    find_frame = tk.Frame(frame)
    find_frame.pack(pady=(5, 0))

    find_dupes_button = tk.Button(find_frame, text="Find Duplicates", command=find_duplicates)
    find_dupes_button.pack(padx=5)

    # Derde rij: Search Entry + knop (gecentreerd)
    search_frame = tk.Frame(frame)
    search_frame.pack(pady=(5, 10))

    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
    search_entry.pack(side=tk.LEFT, padx=5)

    search_button = ttk.Button(search_frame, text="Search", command=search_treeview)
    search_button.pack(side=tk.LEFT, padx=5)

    # TreeView (onderaan, volledig uitgevouwen)
    tree_frame = tk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    global bulk_tree, x_scroll, y_scroll
    x_scroll = tk.Scrollbar(tree_frame, orient="horizontal")
    x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    y_scroll = tk.Scrollbar(tree_frame, orient="vertical")
    y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    bulk_tree = ttk.Treeview(
        tree_frame,
        columns=("Date", "Time", "Callsign", "Name", "Mode", "Submode", "Band", "Frequency",
                 "Sent", "Received", "Locator", "Comment", "WWFF", "POTA", "Country",
                 "Continent", "My Callsign", "My Operator", "My Locator", "My Location", "My WWFF", "My POTA", "Satellite"),
        xscrollcommand=x_scroll.set,
        yscrollcommand=y_scroll.set
    )
    for col_num, col_name in enumerate(bulk_tree["columns"], 1):
        bulk_tree.heading(f"#{col_num}", text=col_name, anchor="center",
                          command=lambda _col=col_name: sort_column(bulk_tree, _col, False))
        bulk_tree.column(f"#{col_num}", anchor="center", stretch=True, width=100)
    bulk_tree["show"] = "headings"
    bulk_tree.tag_configure("oddrow", background="lightblue")
    bulk_tree.tag_configure("evenrow", background="white")
    bulk_tree.pack(fill=tk.BOTH, expand=True)

    x_scroll.config(command=bulk_tree.xview)
    y_scroll.config(command=bulk_tree.yview)

    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Bulk Edit", command=bulk_edit)
    context_menu.add_command(label="Delete Selected QSO(s)", command=delete_selected_qsos)
    bulk_tree.bind("<Button-3>", lambda event: show_context_menu(event, context_menu))

    close_button = tk.Button(frame, text="Close", command=close_program)
    close_button.pack(side=tk.BOTTOM, padx=10, pady=10)




def sort_column(tree, col, reverse):
    """Sort Treeview column on click and reapply row colors."""
    # Extract the data in the specified column
    data_list = [(tree.set(child, col), child) for child in tree.get_children('')]
    
    # Sort the data list based on the column value
    data_list.sort(reverse=reverse)
    
    # Reorder items in the Treeview based on sorted order
    for index, (_, child) in enumerate(data_list):
        tree.move(child, '', index)

    # Reapply alternating row colors
    for index, child in enumerate(tree.get_children('')):
        row_tag = "oddrow" if index % 2 == 0 else "evenrow"
        tree.item(child, tags=(row_tag,))
    
    # Update heading command to toggle between ascending and descending
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))


def find_duplicates():
    seen = {}
    duplicate_index_map = {}

    for idx, qso in enumerate(data["Logbook"]):
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

    dup_window = tk.Toplevel(root)
    dup_window.title("Duplicate QSOs Found")

    tree = ttk.Treeview(dup_window, columns=("Index", "Callsign", "Date", "Time"), show="headings", selectmode="extended")
    tree.heading("Index", text="Index")
    tree.heading("Callsign", text="Callsign")
    tree.heading("Date", text="Date")
    tree.heading("Time", text="Time")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tree_to_log_index = {}
    color_styles = ["lightblue", "white", "lightgreen", "lightyellow", "lightpink", "lavender", "lightgray"]

    # Definieer tags met kleuren
    for i, color in enumerate(color_styles):
        tag_name = f"tag_{i}"
        tree.tag_configure(tag_name, background=color)

    # Voeg rijen toe met per groep een andere kleur
    for group_index, (key, indices) in enumerate(duplicate_index_map.items()):
        tag_name = f"tag_{group_index % len(color_styles)}"
        for idx in indices:
            qso = data["Logbook"][idx]
            iid = f"dup_{idx}"
            tree.insert(
                "", "end", iid=iid,
                values=(idx, qso.get("Callsign"), qso.get("Date"), qso.get("Time")),
                tags=(tag_name,)
            )
            tree_to_log_index[iid] = idx

    def delete_selected_duplicates():
        selected_iids = tree.selection()
        if not selected_iids:
            messagebox.showwarning("No Selection", "Select records to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(selected_iids)} selected duplicates?"):
            return
        indices_to_delete = sorted([tree_to_log_index[iid] for iid in selected_iids], reverse=True)
        for i in indices_to_delete:
            try:
                del data["Logbook"][i]
            except IndexError:
                continue
        update_treeview()
        dup_window.destroy()
        messagebox.showinfo("Done", f"{len(indices_to_delete)} duplicates removed.")

    tk.Button(dup_window, text="Delete Selected", command=delete_selected_duplicates).pack(pady=5)
    tk.Button(dup_window, text="Close", command=dup_window.destroy).pack(pady=5)




def open_logbook_file():
    global logbook_file_path
    current_json_file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.mbk")])
    if current_json_file:
        logbook_file_path = current_json_file
        load_logbook_data(current_json_file)
        update_treeview()

        # Update de venstertitel met bestandsnaam
        filename_only = current_json_file.split("/")[-1]
        root.title(f"MiniBook Logbook Bulk Editor - v{VERSION_NUMBER} - [{filename_only}]")
        file_name_var.set(f"Loaded file: {filename_only}")


def load_logbook_data(current_json_file):
    global data
    try:
        with open(logbook_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        messagebox.showerror("Error", f"Failed to open file: {e}")

def update_treeview():
    for item in bulk_tree.get_children():
        bulk_tree.delete(item)

    for idx, qso in enumerate(data["Logbook"]):
        row_tag = "oddrow" if idx % 2 == 0 else "evenrow"
        bulk_tree.insert("", "end", iid=idx, values=(
            qso.get('Date', ''),
            qso.get('Time', ''),
            qso.get('Callsign', '').upper(),
            qso.get('Name', ''),
            qso.get('Mode', '').upper(),
            qso.get('Submode', '').upper(),
            qso.get('Band', '').lower(),
            qso.get('Frequency', ''),
            qso.get('Sent', ''),
            qso.get('Received', ''),
            qso.get('Locator', '').upper(),
            qso.get('Comment', ''),
            qso.get('WWFF', ''),
            qso.get('POTA', ''),
            qso.get('Country', ''),
            qso.get('Continent', '').upper(),
            qso.get('My Callsign', '').upper(),
            qso.get('My Operator', '').upper(),
            qso.get('My Locator', '').upper(),
            qso.get('My Location', ''),
            qso.get('My WWFF', ''),
            qso.get('My POTA', ''),
            qso.get('Satellite', '')
        ), tags=(row_tag,))

    # Sorteer na het laden op Datum en Tijd (nieuwste eerst)
    sort_by_date_time_desc()


def show_context_menu(event, context_menu):
    selected_items = bulk_tree.selection()
    if selected_items:
        bulk_tree.selection_set(selected_items)
        context_menu.post(event.x_root, event.y_root)


def delete_selected_qsos():
    selected_items = bulk_tree.selection()
    if not selected_items:
        messagebox.showwarning("No Selection", "Please select at least one QSO to delete.")
        return

    if not messagebox.askyesno("Confirm Delete", f"Delete {len(selected_items)} selected QSO(s)? This cannot be undone."):
        return

    # Sort in reverse order to avoid index shifting issues when deleting
    indices_to_delete = sorted([int(item) for item in selected_items], reverse=True)
    
    for idx in indices_to_delete:
        try:
            del data["Logbook"][idx]
        except IndexError:
            continue  # Skip invalid indexes just in case

    update_treeview()
    messagebox.showinfo("Deleted", f"{len(indices_to_delete)} QSO(s) have been deleted.")



def bulk_edit():
    selected_items = bulk_tree.selection()
    if not selected_items:
        messagebox.showwarning("No Selection", "Please select at least one QSO record to edit.")
        return

    bulk_edit_window = tk.Toplevel(root)
    bulk_edit_window.title("Bulk Edit")
    bulk_edit_window.resizable(False, False)

    # Center the edit window relative to logbook_window
    root.update_idletasks()  # Ensure dimensions are calculated
    logbook_x = root.winfo_x()
    logbook_y = root.winfo_y()
    logbook_width = root.winfo_width()
    logbook_height = root.winfo_height()
    edit_width = 350  # Estimated width of edit_window
    edit_height = 100  # Estimated height of edit_window

    edit_x = logbook_x + (logbook_width - edit_width) // 2
    edit_y = logbook_y + (logbook_height - edit_height) // 2
    bulk_edit_window.geometry(f"{edit_width}x{edit_height}+{edit_x}+{edit_y}")    

    # Disable interaction with root window until bulk_edit_window is closed
    bulk_edit_window.grab_set()

    field_options = ["Callsign", "Name", "Date", "Time", "Mode", "Submode", "Band", "Frequency", "Sent", "Received", "Locator",
                     "Comment",  "WWFF", "POTA", "Country", "Continent", "My Callsign", "My Operator", "My Locator", "My Location", "My WWFF", "My POTA", "Satellite"]
    
    band_ranges = ["2200m", "160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "11m", "10m",
                   "6m", "4m", "2m", "1.25m", "70cm", "33cm", "23cm", "13cm"]
    
    # -------- Operating mode options --------
    mode_options        = ["AM", "FM", "USB", "LSB", "SSB", "CW", "CW-R", "DIG", "RTTY", "MFSK", "DYNAMIC", "JT65", "JT8", "FT8", "PSK31", "PSK64", "PSK125", "QPSK31", "PKT","OLIVIA", "SSTV", "VARA","DOMINO"]
    submode_options     = ["","FT4"]
    rst_options = [str(i) for i in range(51, 60)] + ["59+10dB", "59+20dB", "59+30dB", "59+40dB"]

    field_var = tk.StringVar()
    tk.Label(bulk_edit_window, text="Select field to edit:").grid(row=0, column=0, padx=10, pady=5)
    field_dropdown = ttk.Combobox(bulk_edit_window, textvariable=field_var, values=field_options)
    field_dropdown.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(bulk_edit_window, text="New value:").grid(row=1, column=0, padx=10, pady=5)

    # Define a placeholder for the new value widget
    new_value_widget = None

    def update_value_widget(event=None):
        nonlocal new_value_widget

        # Remove the existing widget if any
        if new_value_widget:
            new_value_widget.destroy()

        selected_field = field_var.get()

        # Use specific widgets for specific fields
        if selected_field == "Band":
            new_value_widget = ttk.Combobox(bulk_edit_window, values=band_ranges)
        elif selected_field == "Mode":
            new_value_widget = ttk.Combobox(bulk_edit_window, values=mode_options)
        elif selected_field == "Submode":
            new_value_widget = ttk.Combobox(bulk_edit_window, values=submode_options)            
        elif selected_field in ["Sent", "Received"]:
            new_value_widget = ttk.Combobox(bulk_edit_window, values=rst_options)
        elif selected_field == "Date":
            new_value_widget = DateEntry(bulk_edit_window, date_pattern="yyyy-mm-dd")  # Date picker for Date field
        else:
            new_value_widget = tk.Entry(bulk_edit_window)

        new_value_widget.grid(row=1, column=1, padx=10, pady=5)
        new_value_widget.focus_set()

    # Update the new value widget when the field changes
    field_dropdown.bind("<<ComboboxSelected>>", update_value_widget)

    # Call once to set initial state
    update_value_widget()

    def save_bulk_edit():
        field = field_var.get()
        new_value = new_value_widget.get() if new_value_widget else ""

        for item in selected_items:
            qso_index = int(item)
            qso = data["Logbook"][qso_index]

            # Validate both Locator fields if they are being edited
            if 'Locator' in field or 'My Locator' in field:
                if not is_valid_locator(new_value):
                    messagebox.showerror("Invalid Locator", f"The Maidenhead locator in 'Locator' field must be at least 4 characters and valid.\nExample: FN31 or FN31TK")
                    return

            # Ensure specific fields are stored in uppercase
            if field in ["Callsign", "My Callsign", "Locator", "My Locator", "Band"]:
                qso[field] = new_value.upper()  # Convert to uppercase
            else:
                qso[field] = new_value  # Keep original case for other fields

            # Update the corresponding row in the tree view
            bulk_tree.item(item, values=(
                qso.get('Date', ''),
                qso.get('Time', ''),
                qso.get('Callsign', '').upper(),
                qso.get('Name', ''),
                qso.get('Mode', '').upper(),
                qso.get('Submode', '').upper(),  # Gebruik een lege string als 'Submode' ontbreekt
                qso.get('Band', ''),
                qso.get('Frequency', ''),
                qso.get('Sent', ''),
                qso.get('Received', ''),
                qso.get('Locator', '').upper(),
                qso.get('Comment', ''),
                qso.get('WWFF', ''),
                qso.get('POTA', ''),
                qso.get('Country', ''),
                qso.get('Continent', '').upper(),
                qso.get('My Callsign', '').upper(),
                qso.get('My Operator', '').upper(),
                qso.get('My Locator', '').upper(),
                qso.get('My Location', ''),
                qso.get('My WWFF', ''),
                qso.get('My POTA', ''),
                qso.get('Satellite', '')
            ))

    def close_bulk_edit_window():
        bulk_edit_window.grab_release()  # Release the grab when closing
        bulk_edit_window.destroy()

    tk.Button(bulk_edit_window, text="Update Record(s)", command=save_bulk_edit).grid(row=2, column=0, pady=10)
    tk.Button(bulk_edit_window, text="Close", command=close_bulk_edit_window).grid(row=2, column=1, pady=10)

# Function to check if Locator is valid format
def is_valid_locator(locator):
    """Check if a locator is valid: either empty or at least 4 characters matching the Maidenhead format."""
    if locator == "":
        return True  # Locator can be empty
    elif len(locator) >= 4 and re.match(r'^[A-R]{2}\d{2}([A-X]{2})?$', locator, re.IGNORECASE):
        return True
    return False

def close_program():
    root.quit()

def save_logbook():
    global logbook_file_path
    if messagebox.askyesno("Save QSO Records", "Are you sure you want to save QSO Records? This cannot be undone!"):
        if logbook_file_path:
            with open(logbook_file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
            messagebox.showinfo("Save Logbook", "Logbook has been saved.")
        else:
            messagebox.showwarning("Save Error", "No file loaded to save.")


def sort_by_date_time_desc():
    """Sort QSO records by Date and Time, newest first."""
    def parse_datetime(item_id):
        values = bulk_tree.item(item_id, "values")
        date_str = values[0].strip()
        time_str = values[1].strip()

        try:
            # Fallback op 00:00:00 als tijd ontbreekt
            if not time_str:
                time_str = "00:00:00"

            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.min
        return dt

    items = bulk_tree.get_children()
    sorted_items = sorted(items, key=parse_datetime, reverse=True)  # Nieuwste eerst

    for index, item_id in enumerate(sorted_items):
        bulk_tree.move(item_id, '', index)
        row_tag = "oddrow" if index % 2 == 0 else "evenrow"
        bulk_tree.item(item_id, tags=(row_tag,))



def main():
    bulk_edit_window()
    root.mainloop()

if __name__ == "__main__":
    main()
