from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd

class ieee_contributions:
    
    url = "https://mentor.ieee.org/"
    
    def __init__(self, verbose = False):
        """
        Initialize with list of functions
        """
        self.verbose = verbose
    
    def get_url(self, stdname, page):
        """
        Request data
        """
        
        url = self.url + stdname + "/documents?n=" + page
        
        print(url)
        
        try:
            with closing(get(url, stream = True)) as resp:
                if self.is_successful_request(resp):
                    return resp.content
                else:
                    return None
                
        except RequestException as e:
            self.log_error('Error during request {} : {}'.format(url, str(e)))
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
    
    def get_page_output(self, stdname, page):
        
        raw_html = self.get_url(stdname, page)
        #len(raw_html)
        
        html = BeautifulSoup(raw_html, 'html.parser')
        
        #print(html.prettify())
            
        entries = html.find_all('tr', class_ = 'b_data_row')
        
        ## create empty dataframe
        df_output = self.df_empty(['date_time_created', 'year', 'dcn', 'rev', 'group', 'title', 'author', 'date_time_upload', 'dllink'],
                                 dtypes = [str, str, str, str, str, str, str, str, str])
        
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
            
            df_output = df_output.append(df_results)
            
        return df_output
     
