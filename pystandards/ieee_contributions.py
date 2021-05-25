from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import re

class ieee_contributions:
    
    url = "https://mentor.ieee.org/"
    
    def __init__(self, verbose = False):
        """
        Initialize with list of functions
        """
        self.verbose = verbose
    
    def get_url(self):
        """
        Request data
        """
        try:
            with closing(get(self.url, stream = True)) as resp:
                if self.is_successful_request(resp):
                    return resp.content
                else:
                    print("error")
                    return get(self.url, stream = True)
                
        except RequestException as e:
            self.log_error('Error during request {} : {}'.format(self.url, str(e)))
            return None
    
    def is_successful_request(self, resp):
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find('html') > -1)
    
    def log_error(self, e):
        print(e)
    
    def df_empty(self, columns, dtypes, index = None):
        df = pd.DataFrame(index = index)
        for c, d in zip(columns, dtypes):
            df[c] = pd.Series(dtype = d)
        return df
    
    def get_page_output(self, url_to_crawl, pageno):
        pageno = str(i + 1)
        raw_html = self.get_url(url_to_crawl + pageno)
        #len(raw_html)
        
        html = BeautifulSoup(raw_html, 'html.parser')
        
        #print(html.prettify())
            
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
            df_results = pd.DataFrame({"date_time_created":date_time_created, "year":year, "dcn":dcn, "rev":rev, "group":group, "title":title, "author":author,
                                  "date_time_upload":date_time_upload, "dllink":dllink}, index = ['IDX']) 
            
            return df_results
     
        
    
    
#### webscraper for meta data and download link for ieee contributions
#### website https://mentor.ieee.org/802.11

## scraper based on https://realpython.com/python-web-scraping-practical-introduction/


## set path where to store csv
path = "F:\\Standards"

import ieee_contributions as ieee

## create empty dataframe
df_output = ieee.df_empty(['date_time_created', 'year', 'dcn', 'rev', 'group', 'title', 'author', 'date_time_upload', 'dllink'],
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
# standard_name = "80211"
standard_name = "80215"
# standard_name = "80216"

## url which shall be crawled
url_to_crawl = url80215

## maximum page number (find this manually on the corresponding website)
max_page_number = 225

for i in range(0,max_page_number):   
    
    pageno = str(i + 1)
    raw_html = get_url(url_to_crawl + pageno)
    #len(raw_html)
    
    html = BeautifulSoup(raw_html, 'html.parser')
    
    #print(html.prettify())
        
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
        ## put into dataframe
        dfres = pd.DataFrame({"date_time_created":date_time_created, "year":year, "dcn":dcn, "rev":rev, "group":group, "title":title, "author":author,
                              "date_time_upload":date_time_upload, "dllink":dllink}, index = ['IDX'])    
        ## append to dataframe
        df_output = df_output.append(dfres)
        
    print(str(pageno) + " Time: " + str(datetime.datetime.now()))



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
   
