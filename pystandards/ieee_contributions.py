#### Webscraper for meta data and download link for IEEE contributions
#### Website https://mentor.ieee.org/802/bp/StartPage


from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import re
import urllib.request
import time
import random

class ieee_contributions:
    
    url = "https://mentor.ieee.org/"
    
    def __init__(self, verbose = False):

        self.verbose = verbose
    
    def get_content(self, stdname, page):
        
        page = str(page)
        
        url = self.url + stdname + "/documents?n=" + page
        
        try:
            with closing(get(url, stream = True)) as resp:
                if self.is_successful(resp):
                    return resp.content
                else:
                    return None
                
        except RequestException as e:
            print('Error during request {} : {}'.format(url, str(e)))
            return None
    
    def is_successful(self, resp):
        
        content_type = resp.headers['Content-Type'].lower()
        return (re.match(r"2[0-9]{2}", str(200))
                and content_type is not None
                and content_type.find('html') >= 0)
    
    def init_df_output(self, index = None):
        
        df = pd.DataFrame(index = index)
        columns = ['date_time_created', 'year', 'dcn', 'rev', 'group', 'title', 'author', 'date_time_upload', 'dl_link']
        dtypes = [str, str, str, str, str, str, str, str, str]
        for c, d in zip(columns, dtypes):
            df[c] = pd.Series(dtype = d)
        return df
    
    def get_df_output(self, stdname, page):
        
        raw_html = self.get_content(stdname, page)
        
        html = BeautifulSoup(raw_html, 'html.parser')
            
        entries = html.find_all('tr', class_ = 'b_data_row')
        
        df_output = self.init_df_output()
        
        for entry in entries:
            
            date_time_created = entry.find_all('div')[0].text
            year = entry.find_all('td', class_='dcn_ordinal')[0].text
            dcn = entry.find_all('td', class_='dcn_ordinal')[1].text
            rev = entry.find_all('td', class_='dcn_ordinal')[2].text
            group = entry.find_all('td')[4].text
            title = entry.find_all('td', class_='long')[0].text
            author = entry.find_all('td', class_='long')[1].text
            date_time_upload = entry.find_all('div')[1].text
            file = entry.find_all('td', class_='list_actions')[0].find('a')['href']
            
            df_results = pd.DataFrame({"date_time_created" : date_time_created, "year" : year, "dcn" : dcn, "rev" : rev, "group" : group,
                                       "title" : title, "author" : author, "date_time_upload" : date_time_upload, "file" : file}, index = ['IDX']) 
            
            df_output = df_output.append(df_results)
            
        return df_output
     
    def get_meta(self, std_name, start_page, end_page):
        
        df_output = self.init_df_output()       
        
        for page in range(start_page, end_page + 1):
            
            df_results = self.get_df_output(std_name, page = page)
            
            df_output = df_output.append(df_results)
            
            print("Page " + str(page) + " Time: " + str(datetime.datetime.now()))

        # get document type
        df_output['doc_type'] = [re.split(r"\.(?=[^.]*$)", x)[-1] for x in df_output['file']]
            
        # link that can be used to download contributions
        df_output['dl_link'] = self.url + df_output['file']
        
        df_output.loc[:, 'file'] = [re.sub(r"^/", "", x) for x in df_output['file']]
        df_output.loc[:, 'file'] = [re.sub(r"\.([^.]*$)", "", x) for x in df_output['file']]
        df_output.loc[:, 'file'] = [re.sub(r"/|\.", "_", x) for x in df_output['file']]
            
        return df_output
    
    
    def download_contributions(self, df_metadata, path, time_sleep = 15):
        
        for j in range(0, len(df_metadata)):
            
            url = df_metadata['dl_link'][j]
            file = str(df_metadata['file'][j])
            doc_type = str(df_metadata['doc_type'][j])
            
            try:
                urllib.request.urlretrieve(url, path + file + "." + doc_type)
                
            except Exception as e:
                print(e)
                continue
            
            print(str(j) + " Time: " + str(datetime.datetime.now()))
            
            ## wait approximately 15 seconds to not overload the server
            time.sleep(time_sleep + random.randint(-5, 5))
            
        print("Download completed!")
     
