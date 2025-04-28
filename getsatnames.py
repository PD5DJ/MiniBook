import requests

# URLs van de TLE-lijsten
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
            continue  # Onvolledige TLE, overslaan
        name_line = lines[i].strip()
        if "(" in name_line and ")" in name_line:
            name = name_line.split("(")[-1].split(")")[0].strip()
        else:
            name = name_line.strip()
        satellite_names.append(name)

# Sorteer alfabetisch en verwijder dubbele namen
satellite_names = sorted(set(satellite_names))

# Schrijf naar bestand met lege regel bovenaan
with open("satellites.txt", "w") as f:
    #f.write("\n")  # Lege regel bovenaan
    for name in satellite_names:
        f.write(name + "\n")

print("Bestand 'satellites.txt' succesvol aangemaakt.")
