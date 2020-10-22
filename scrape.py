import os
import sys
from http import HTTPStatus
import requests
import datetime
from requests.models import ReadTimeoutError
from requests_html import HTML
import pandas as pd

now  =  datetime.datetime.now()
year = now.year

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def url_to_txt(url, filename="world.html", save=False):
    r = requests.get(url)
    filename = f"world-{year}.html"
    if r.status_code ==  HTTPStatus.OK:
        html_text = r.text
        if save:
            with open(filename, "w") as f:
                f.write(html_text)
        return html_text

    return None

def parse_and_extract(url, name='2020'):
    html_text = url_to_txt(url)
    if html_text == None:
        return False
    r_html = HTML(html=html_text)

    table_class  = ".imdb-scroll-table" # using  "class"
    # table_class = "#table" using "id"
    r_table = r_html.find(table_class)
    table_data = []
    header_names = []
    if len(r_table) == 0:
        return False
    parsed_table = r_table[0]
    rows = parsed_table.find("tr")
    header_row = rows[0]
    header_cols = header_row.find("th")
    header_names = [x.text for x in header_cols]
    table_data = []
    for row in rows[1:]:
        #print(row.text)
        cols = row.find("td")
        row_data = []
        for i, col in enumerate(cols):
            # print(i, col.text, '\n\n')
            row_data.append(col.text)
        table_data.append(row_data)
    df = pd.DataFrame(table_data, columns=header_names)
    filepath = os.path.join('data', f'{name}.csv')
    df.to_csv(filepath, index=False)


def run(start_year=None, years_ago=0):
    if start_year == None:
        now  =  datetime.datetime.now()
        start_year = now.year
    assert isinstance(start_year, int)
    assert isinstance(years_ago, int)
    assert len(f"{start_year}") == 4
    for i in range(0, years_ago+1):
        url = f"https://www.boxofficemojo.com/year/world/{start_year}"
        finished = parse_and_extract(url, name=start_year)
        if finished:
            print(f"Finished parsing {start_year}")
        else:
            print(f"{start_year} not finshed")
        start_year-=1

if __name__ == "__main__":
    try:
        start = int(sys.argv[1])
    except:
        start = None
    try:
        count = int(sys.argv[2])
    except:
        count = 0

    run(start_year=start, years_ago=count)
