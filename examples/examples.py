#### webscraper for meta data and download link for ieee contributions
#### website https://mentor.ieee.org/802.11

## scraper based on https://realpython.com/python-web-scraping-practical-introduction/


from ieee_contributions import ieee_contributions
import datetime
import re

## set path where to store csv
path = "F:\\Standards"

## initiate instance of class geocoding_functions
# verbose=True ... so the print statements are shown here
ieee_con = ieee_contributions(verbose = True)


## create empty dataframe
df_output = ieee_con.df_empty(['date_time_created', 'year', 'dcn', 'rev', 'group', 'title', 'author', 'date_time_upload', 'dllink'],
                                 dtypes = [str, str, str, str, str, str, str, str, str])

## for loop over all pages
## 802.11: 578 is maximum page number right now on ieee website (max number 698 on 21 Sep. 2020)
url80211 = "https://mentor.ieee.org/802.11/documents?n="
## 802.15: 210 max page number (max number 225 as of 24 Sep. 2020)
url80215 = "https://mentor.ieee.org/802.15/documents?n="
## max page: 47
url80222 = "https://mentor.ieee.org/802.22/documents?n="
## max page: 21 (max number the same, i.e. 21, as of 24 Sep. 2020)
url80216 = "https://mentor.ieee.org/802.16/documents?n="
## max page: 5
url80224 = "https://mentor.ieee.org/802.24/documents?n="

## name of standard
# standard_name = "802.11"
standard_name = "802.15"
# standard_name = "802.16"

## url which shall be crawled
url_to_crawl = url80215

## maximum page number (find this manually on the corresponding website)
max_page_number = 225


for i in range(0, 2):
    
    pageno = str(i + 1)
    
    df_results = ieee_con.get_page_output(stdname = standard_name, page = pageno)
    
    df_output = df_output.append(df_results)
        
    print(str(pageno) + " Time: " + str(datetime.datetime.now()))





from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd

from ieee_contributions import ieee_contributions
ieee_con = ieee_contributions(verbose = True)

pageno = str(1)

raw_html = ieee_con.get_url(standard_name, pageno)

html = BeautifulSoup(raw_html, 'html.parser')


entries = html.find_all('tr', class_ = 'b_data_row')

for entry in entries:
    date_time_created = entry.find_all('div')[0].text
    year = entry.find_all('td', class_='dcn_ordinal')[0].text
    dcn = entry.find_all('td', class_='dcn_ordinal')[1].text
    rev = entry.find_all('td', class_='dcn_ordinal')[2].text
    group = entry.find_all('td')[4].text
    title = entry.find_all('td', class_='long')[0].text
    author = entry.find_all('td', class_='long')[1].text
    date_time_upload = entry.find_all('div')[1].text
    dllink = entry.find_all('td', class_='list_actions')[0].find('a')['href']
    df_results = pd.DataFrame({"date_time_created" : date_time_created, "year" : year, "dcn" : dcn, "rev" : rev, "group" : group,
                               "title" : title, "author" : author, "date_time_upload" : date_time_upload, "dllink" : dllink}, index = ['IDX']) 



## prepare downloadlink to get final download link
df_output['dllink_ready'] = 'https://mentor.ieee.org' + df_output['dllink']

## create unique contr_doc_id
df_output['contr_doc_id'] = list(reversed(range(len(df_output))))
df_output.dtypes
df_output[['contr_doc_id']] = df_output[['contr_doc_id']].astype(str)
df_output.dtypes
## get unique id
df_output['contr_doc_id'] = str(5) + standard_name + df_output['contr_doc_id']

## write type of document into new column
df_output['doctype'] = ""
df_output['doctype'] = [re.split(r"\.(?=[^.]*$)", x)[-1] for x in df_output['dllink']]


## dataframe to list
#listresults = list(df_output.values.tolist())

## type of document: substring after last dot
#df_output.dtypes
#df_output['dllink'][1]

## store dfdocid and dfresults as csv file
current_time = str(datetime.datetime.now())
current_time = current_time.replace(".", "-")
current_time = current_time.replace(":", "-")
df_output.to_csv(path + '\\IEEE\\contributions\\' + standard_name + '\\ieee_metadata_contributions_' + standard_name + '_' + current_time  + '.csv', sep = ';')
