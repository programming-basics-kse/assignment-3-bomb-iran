import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("filename", type=str, help="Source location")
parser.add_argument("-medals", action="store_true", required=True)
parser.add_argument("country", type=str, help="Country name")
parser.add_argument("year", type=int, help="Year of the olympics")
parser.add_argument("-output", help="Filename of output file")
config = vars(parser.parse_args())

data = [line.split('\t') for line in open(config["filename"], "r").read().splitlines()]
data = [{data[0][n]: int(field) if field.isdigit() else field for n, field in enumerate(entry)} for entry in data[1::]]


country = config["country"]
year = config["year"]
entries = [entry for entry in data if country in (entry['Team'], entry['NOC']) and entry['Year'] == year and entry['Medal'] != 'NA']
t = '       Medalists: \n   Name; Sport; Medal\n'
for entry in entries[0:10 if len(entries) >= 10 else len(entries)]:
    t += ' - ' + '; '.join((entry["Name"], entry["Sport"], entry["Medal"])) + '\n'

medals = [entry['Medal'] for entry in entries]
t += "      Total medals: " + f"Gold: {medals.count("Gold")}, Silver: {medals.count("Silver")}, Bronze: {medals.count("Bronze")}"

print(t)