import tkinter as tk
from tkinter import messagebox
import requests
import xml.etree.ElementTree as ET
import json
import os
import urllib.parse
import webbrowser
import math

CREDENTIAL_FILE = "qrz_credentials.json"

def save_credentials(username, password, locator):
    credentials = {"username": username, "password": password, "locator": locator}
    with open(CREDENTIAL_FILE, "w") as f:
        json.dump(credentials, f)

def load_credentials():
    if os.path.exists(CREDENTIAL_FILE):
        with open(CREDENTIAL_FILE, "r") as f:
            return json.load(f)
    return {"username": "", "password": "", "locator": ""}

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
        return None, "No internet connection"

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
    url = f"https://xmldata.qrz.com/xml/current/?s={session_key}&callsign={callsign}"

    try:
        response = requests.get(url, timeout=5)
        print("Raw XML:\n", response.text)
    except requests.exceptions.RequestException:
        return {}

    root = ET.fromstring(response.content)
    ns = {"qrz": "http://xmldata.qrz.com"}

    callsign_element = root.find(".//qrz:Callsign", ns)
    if callsign_element is None:
        print("⚠️ No Callsign element found in XML!")
        return {}

    lat = callsign_element.findtext("qrz:lat", default="", namespaces=ns)
    lon = callsign_element.findtext("qrz:lon", default="", namespaces=ns)
    maps_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else ""

    data = {
        "callsign": callsign_element.findtext("qrz:call", default="", namespaces=ns),
        "name": f"{callsign_element.findtext('qrz:fname', default='', namespaces=ns)} {callsign_element.findtext('qrz:name', default='', namespaces=ns)}".strip(),
        "address": callsign_element.findtext("qrz:addr1", default="", namespaces=ns),
        "city": callsign_element.findtext("qrz:addr2", default="", namespaces=ns),
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

def open_map_link(event):
    url = result_vars["MapsLink"].get()
    if url:
        webbrowser.open_new_tab(url)

def on_query():
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    locator = entry_locator.get().strip().upper()
    callsign = entry_callsign.get().strip()

    if username == "" and password == "":
        print("No credentials provided. Skipping query.")
        return
    elif username == "" or password == "":
        messagebox.showerror("Missing Credentials", "Please enter both QRZ username and password.")
        return

    if not callsign:
        return

    session_key, error = get_session_key(username, password)

    if not session_key:
        if error:
            if "Invalid" in error or "incorrect" in error.lower() or "not authorized" in error.lower():
                messagebox.showerror("Login Failed", "Username or password incorrect.")
            else:
                messagebox.showerror("Connection Error", error)
        else:
            print("Query skipped without specific error.")
        return

    # Save valid credentials and locator
    save_credentials(username, password, locator)

    data = query_callsign(session_key, callsign)

    for key in result_vars:
        field_key = key.lower().replace(" ", "").replace("_", "")
        result_vars[key].set(data.get(field_key, ""))

    try:
        my_lat, my_lon = locator_to_latlon(locator)
        target_lat, target_lon = None, None

        if data.get("lat") and data.get("lon"):
            target_lat = float(data["lat"])
            target_lon = float(data["lon"])
        elif data.get("grid"):
            target_lat, target_lon = locator_to_latlon(data["grid"])

        if target_lat is not None and target_lon is not None:
            sp = round(calculate_azimuth(my_lat, my_lon, target_lat, target_lon), 1)
            lp = round((sp + 180) % 360, 1)
            sp_lp_label.config(text=f"SP: {sp}°  /  LP: {lp}°")
        else:
            sp_lp_label.config(text="")
    except Exception as e:
        print("Azimuth calculation failed:", e)
        sp_lp_label.config(text="")

# GUI
root = tk.Tk()
root.title("QRZ.com Lookup")

# Credentials
tk.Label(root, text="QRZ Username:").grid(row=0, column=0, sticky="e")
tk.Label(root, text="QRZ Password:").grid(row=1, column=0, sticky="e")
tk.Label(root, text="My Locator:").grid(row=2, column=0, sticky="e")

entry_username = tk.Entry(root, width=30)
entry_password = tk.Entry(root, show="*", width=30)
entry_locator = tk.Entry(root, width=30)

entry_username.grid(row=0, column=1)
entry_password.grid(row=1, column=1)
entry_locator.grid(row=2, column=1)

creds = load_credentials()
entry_username.insert(0, creds["username"])
entry_password.insert(0, creds["password"])
entry_locator.insert(0, creds.get("locator", ""))

# Callsign input
tk.Label(root, text="Enter Callsign:").grid(row=3, column=0, sticky="e")
entry_callsign = tk.Entry(root, width=20)
entry_callsign.grid(row=3, column=1)

# Result fields
fields = [
    "Callsign", "Name", "Address", "City", "Province", "Country", "Email",
    "Grid", "CQ_Zone", "ITU_Zone", "QSLMgr", "Lat", "Lon", "MapsLink"
]
result_vars = {field: tk.StringVar() for field in fields}

for i, field in enumerate(fields, start=4):
    label_text = field.replace("_", " ")
    tk.Label(root, text=label_text + ":").grid(row=i, column=0, sticky="e")

    if field == "MapsLink":
        link = tk.Label(root, textvariable=result_vars[field], fg="blue", cursor="hand2", anchor="w", width=40)
        link.grid(row=i, column=1, sticky="w")
        link.bind("<Button-1>", open_map_link)
    else:
        tk.Entry(root, textvariable=result_vars[field], state="readonly", width=40).grid(row=i, column=1)

# SP/LP Label
sp_lp_label = tk.Label(root, text="", font=("Arial", 10, "bold"))
sp_lp_label.grid(row=len(fields) + 4, column=0, columnspan=2, pady=5)

# Buttons
tk.Button(root, text="Run Query", command=on_query).grid(row=len(fields) + 5, column=0, pady=10)
tk.Button(root, text="Exit", command=root.quit).grid(row=len(fields) + 5, column=1, pady=10)

root.mainloop()
