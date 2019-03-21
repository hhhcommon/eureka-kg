"""
This is a module to get information of companies from wikipedia
"""

import numpy as np
import pandas as pd
import os
import json


_PATH = './json_folder'


def _get(url):
    try:
        import requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
        return requests.get(url, headers=headers)
    except ImportError:
        pass
    except Exception as e:
        print(e, 'from', url)


def _parse(r):
    if r is None:
        return
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, 'lxml')
    [c.extract() for c in soup('sup')]
    s = ''
    metadata = []
    for content in soup.select("[class~=mw-parser-output]"):
        s += content.p.get_text()
        for tr in content.select("tr"):
            t = []
            for th in tr.select("th[scope='row']"):
                t.append(th.get_text())
            for td in tr.select("td"):
                td_list = []
                for con in td.contents:
                    if con.string is None:
                        continue
                    td_list.append(con.string)
                td_str = " ".join(td_list)
                td_str = td_str.replace("  ", " ")
                t.append(td_str)
            metadata.append(t)

    return (s.strip(), pd.DataFrame(metadata).replace(to_replace=r'^\s*$', value=np.nan,
                                                      regex=True).dropna(axis=0))


def get_companies_info(url_list=None):
    if url_list is None:
        raise ValueError('The url list should not be empty.')
    for url in url_list:
        par = _parse(_get(url))
        data = {
            'url': url,
            'name': url.split('/')[-1],
            'description': par[0],
            'metadata': par[1].to_dict()
        }
        print(data)
        if not os.path.exists(_PATH):
            os.makedirs(_PATH)
        os.chdir(_PATH)
        with open(url.split('/')[-1]+'.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)


get_companies_info(["https://en.wikipedia.org/wiki/JD.com",
                    "https://en.wikipedia.org/wiki/Ant_Financial"])
