#**********************************************************************************************************************************
# File          :   cty_parser.py
# Project       :   cty.dat parsing tool
# Description   :   Filters out dxcc data from cty.dat file for further use
# Date          :   29-05-2025
# Authors       :   Bjorn Pasteuning - PD5DJ
# Website       :   https://wwww.pd5dj.nl
#
# Version history
#   29-05-2025  :   1.0.0   - Initial basics running
#**********************************************************************************************************************************

class CtyEntry:
    def __init__(self, name, cq_zone, itu_zone, continent, latitude, longitude, prefixes):
        self.name = name
        self.cq_zone = int(cq_zone)
        self.itu_zone = int(itu_zone)
        self.continent = continent
        self.latitude = float(latitude)             # + = North
        self.longitude = -float(longitude)          # + = West
        self.prefixes = prefixes

def parse_cty_file(filepath):
    entries = []
    with open(filepath, encoding='utf-8') as f:
        lines = f.read().splitlines()

    entry_lines = []
    for line in lines:
        if not line.strip():
            continue
        if not line.startswith(' '):
            if entry_lines:
                entries.append(parse_entry(entry_lines))
            entry_lines = [line]
        else:
            entry_lines.append(line)

    if entry_lines:
        entries.append(parse_entry(entry_lines))

    return entries

def parse_entry(lines):
    header = lines[0]
    data = ''.join(lines[1:])
    parts = header.split(':')
    name = parts[0].strip()
    cq_zone = parts[1].strip()
    itu_zone = parts[2].strip()
    continent = parts[3].strip()
    lat = parts[4].strip()
    lon = parts[5].strip()

    raw_prefixes = data.strip().split(',')
    prefixes = [p.strip() for p in raw_prefixes if p.strip()]
    
    return CtyEntry(name, cq_zone, itu_zone, continent, lat, lon, prefixes)
