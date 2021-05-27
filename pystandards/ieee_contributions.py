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
            dl_link = entry.find_all('td', class_='list_actions')[0].find('a')['href']
            
            df_results = pd.DataFrame({"date_time_created" : date_time_created, "year" : year, "dcn" : dcn, "rev" : rev, "group" : group,
                                       "title" : title, "author" : author, "date_time_upload" : date_time_upload, "dl_link" : dl_link}, index = ['IDX']) 
            
            df_output = df_output.append(df_results)
            
        return df_output
     
    def get_contributions(self, std_name, start_page, end_page):
        
        df_output = self.init_df_output()       
        
        for page in range(start_page, end_page + 1):
            
            df_results = self.get_df_output(std_name, page = page)
            
            df_output = df_output.append(df_results)
            
            # final download link
            df_output['dl_link'] = self.url + df_output['dl_link']

            # get document type
            df_output['doctype'] = ""
            df_output['doctype'] = [re.split(r"\.(?=[^.]*$)", x)[-1] for x in df_output['dl_link']]
            
            print(str(page) + " Time: " + str(datetime.datetime.now()))
            
        return df_output
     
