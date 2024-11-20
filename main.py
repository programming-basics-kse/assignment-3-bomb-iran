import argparse
from audioop import reverse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("filename", type=str, help="Source location")
parser.add_argument("-medals", nargs=2, metavar=('COUNTRY', 'YEAR'), help="List of medals of country in specific olympics")
parser.add_argument('-total', metavar='YEAR', help="Every country performance on specific olympics")
parser.add_argument('-overall', nargs='+', metavar='COUNTRY', help="Best performance year of every country")
parser.add_argument('-interactive', action="store_true", help="Interactive mode")
parser.add_argument("-output", metavar='FILENAME', help="Filename of output file")
config = vars(parser.parse_args())

def read_file():
    with open(config["filename"], "r") as file: data = [line.split('\t') for line in file.read().splitlines()]
    return [{data[0][n]: int(field) if field.isdigit() else field for n, field in enumerate(entry)} for entry in data[1::]]

def format_left(string, length): return string + " "*(length - len(string))
def format_center(string, length): return ' '*((n := length - len(string))//2) + string + ' '*((n+n%2)//2)

def output(title: str, header: str, body: str, separator: str, footer = '') -> None:
    text = f"\n{title}\n{separator}\n{header}\n{separator}\n{body}\n{separator}\n{footer}"
    print(text)
    if config["output"]:
        print(text, file=open(config['output'], 'w'))


def handle_medals_arg(data_: list, country: str, year: int) -> tuple:
    entries = [entry for entry in data_ if country in (entry['Team'].split('-')[0], entry['NOC']) and
               entry['Year'] == year and entry['Medal'] != 'NA']
    if not entries: raise ValueError("No entries found")
    first10 = [(x["Name"], x["Sport"], x["Medal"]) for x in entries[0:10 if len(entries) >= 10 else len(entries)]]
    max_len = [max(len(x[i]) for x in first10) for i in range(3)]
    string_len = sum(max_len) + 15

    title: str = format_center('Medalists:', string_len)
    separator: str = '-' * string_len
    header: str = f" №   | {' | '.join((format_center(x, max_len[i]) for i, x in enumerate(('Name', 'Sport'))))} | Medal  |"
    body: str = '\n'.join(
        f" {n + 1}. {' ' if n < 9 else ''}| " + ' | '.join(format_left(x[i], max_len[i]) for i in range(3)) + ' |'
        for n, x in enumerate(first10))
    total_medals = {
        medal: [entry['Medal'] for entry in entries].count(medal) for medal in ['Gold', 'Silver', 'Bronze']
    }
    medal_label = "Gold: {Gold}, Silver: {Silver}, Bronze: {Bronze}".format(**total_medals)
    footer: str = format_center(f"Total medals: {medal_label}", string_len)
    return title, header, body, separator, footer

def handle_total_arg(data_: list, year: int) -> tuple:
    entries = [entry for entry in data_  if year == entry['Year'] and entry['Medal'] != 'NA']
    if not entries: raise ValueError("No entries found")

    medals_count = {}
    for entry in entries:
        country = entry['Team'].split('-')[0]
        if country not in medals_count: medals_count[country] = {'Gold': 0, 'Silver': 0, 'Bronze': 0}
        medals_count[country][entry['Medal']] += 1

    medals = [(x, str(medals_count[x]['Gold']), str(medals_count[x]['Silver']), str(medals_count[x]['Bronze'])) for x in medals_count.keys()]
    header_list = ('Country', 'Gold', 'Silver', 'Bronze')
    max_len = [max(max(len(x[i]) for x in medals), len(header_list[i])) for i in range(4)]
    string_len = sum(max_len) + 18

    title: str = format_center('Countries:', string_len)
    separator: str = '-' * string_len
    header: str = f" №   | {' | '.join((format_center(x, max_len[i]) for i, x in enumerate(header_list)))} |"
    body: str = '\n'.join(
        f" {n + 1}. {' ' if n < 9 else ''}| " +
    ' | '.join(
            format_left(x[i], max_len[i]) if i == 0 else format_center(x[i], max_len[i])
            for i in range(4)) + ' | '
        for n, x in enumerate(medals))
    return title, header, body, separator

def handle_overall_arg(data_: list, countries_list: list) -> tuple:
    entries = [entry for entry in data_ if (entry['NOC'] in countries_list or entry['Team'].split('-')[0] in countries_list) and entry['Medal'] != 'NA']
    if not entries: raise ValueError("No entries found")
    countries_info = {}
    for entry in entries:
        country_name = entry['NOC']
        year = entry['Year']
        if country_name not in countries_info: countries_info[country_name] = {
            'Name': entry['Team'].replace('/', '-').split('-')[0],
            'Years': {}
        }
        if year not in countries_info[country_name]['Years']: countries_info[country_name]['Years'][year] = 0
        countries_info[country_name]['Years'][year] += 1

    max_medals = [
        (countries_info[name]['Name'], str(year), str(countries_info[name]['Years'][year]))
        for name in countries_info.keys()
        for year in countries_info[name]['Years'].keys()
        if countries_info[name]['Years'][year] == max(countries_info[name]['Years'].values())
    ]
    header_list = ('Country', 'Year', 'Medals')
    max_len = [max(max(len(country[i]) for country in max_medals), len(header_list[i])) for i in range(3)]
    string_len = sum(max_len) + 15

    title: str = format_center('Best Performances:', string_len)
    separator: str = '-' * string_len
    header: str = f" №   | {' | '.join((format_center(x, max_len[i]) for i, x in enumerate(header_list)))} |"
    body: str = '\n'.join(
        f" {n + 1}. {' ' if n < 9 else ''}| " +
        ' | '.join(
            format_left(x[i], max_len[i]) if i == 0 else format_center(x[i], max_len[i])
            for i in range(3)) + ' | '
        for n, x in enumerate(max_medals))
    return title, header, body, separator

def handle_interactive_arg(data_: list):
    try:
        country = input("Country name or NOC(exit() if you want to close the program): ")
        if country == 'exit()': raise KeyboardInterrupt()

        entries = [entry for entry in data_ if country in (entry['Team'].split('-')[0], entry['NOC'])]
        if not entries: raise ValueError("No entries found")
        years = [x['Year'] for x in entries]
        country = entries[0]['Team'].split('-')[0]
        first_year = min(years)
        first_city = next(entry['City'] for entry in entries if entry['Year'] == first_year)

        olympics = {}
        for entry in entries:
            game = entry['Games']
            medal = entry['Medal']
            olympics.setdefault(game, {'Gold': 0, 'Silver': 0, 'Bronze': 0})
            if medal != 'NA':
                olympics[game][medal] += 1

        sum_medals = sorted([(sum(y.values()), x) for x, y in olympics.items()], reverse=True)
        best_performance, worst_performance = sum_medals[0], sum_medals[-1]
        gold_medals, silver_medals, bronze_medals = zip(*[list(y.values()) for x, y in olympics.items()])
        average_medals = {'Gold': round(sum(gold_medals) / len(gold_medals), 2),
                          'Silver': round(sum(silver_medals) / len(silver_medals), 2),
                          'Bronze': round(sum(bronze_medals) / len(bronze_medals), 2)}

        header = f"The first time in the Olympics was in {first_year} in {first_city} city."
        body1 = f'Best performance game was {best_performance[1]} with {best_performance[0]} medals.'
        body2 = f'Worst performance game was {worst_performance[1]} with {worst_performance[0]} medals.'
        footer = "Average medal count: Gold: {Gold}, Silver: {Silver}, Bronze: {Bronze}\n".format(**average_medals)
        string_length = max(len(header), len(body1), len(body2), len(footer))
        title = format_center(country, string_length)
        header = format_left(header, string_length)
        body = format_center(body1, string_length) + '\n' + format_center(body2, string_length)
        footer = format_center(footer, string_length)
        separator = '-' * string_length
        output(title, header, body, separator, footer)
    except KeyboardInterrupt:
        print("\nExiting...")
        exit()
    except ValueError as e:
        print(e)


def main():
    data = read_file()
    if config["medals"]:
        output(*handle_medals_arg(data, config["medals"][0], int(config["medals"][1])))
    elif config["total"]:
        output(*handle_total_arg(data, int(config["total"])))
    elif config["overall"]:
        output(*handle_overall_arg(data, config["overall"]))
    elif config["interactive"]:
        while True:
            handle_interactive_arg(data)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError) as error:
        print(error)