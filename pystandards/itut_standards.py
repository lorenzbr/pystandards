# Webscraper for ITU-T standard documents and metadata
# Website: https://www.itu.int/ITU-T/recommendations
# e.g., https://www.itu.int/ITU-T/recommendations/index.aspx?ser=A


from requests import get
from requests.exceptions import RequestException
import urllib.request
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time
import random
import re
import os
from selenium import webdriver


class itut_standards:

    url_main = "https://www.itu.int/ITU-T/recommendations"

    def __init__(self, verbose=False):
        self.verbose = verbose

    def get_content(self, url):
        try:
            with closing(get(url, stream=True)) as resp:
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

    def df_empty(self, columns, dtypes, index=None):
        df = pd.DataFrame(index=index)
        for c, d in zip(columns, dtypes):
            df[c] = pd.Series(dtype=d)
        return df

    # to do: modularize this function (right now: 3 for loops)
    def get_meta(self, series, driver_file):
        """ Get meta information on ITU-T standards        

        Parameters
        ----------
        series : list
            A list containing the recommendation series (e.g, A, G, H, ...).
        driver_file : str
            Path and name of the Chrome driver exe.

        Returns
        -------
        df_output : DataFrame
            A data frame containing meta information on ITU-T standards.

        Examples
        ----------
        See https://github.com/lorenzbr/pystandards#readme

        """

        # create empty data frame for output table
        df_output = self.df_empty(["recommendation_number", "edition_number",
                                   "recommendation_title", "status",
                                   "approval_date", "approval_process",
                                   "identical_standard", "recommendation_link",
                                   "link_summary",
                                   "summary_text", "link_toc", "toc_text",
                                   "provisional_name", "observation",
                                   "citation", "maintenance_responsibility",
                                   "maintenance_responsibility_link",
                                   "further_details", "further_details_link",
                                   "download_link_recommendation"],
                                  dtypes=['str', 'str', 'str', 'str', 'str',
                                          'str', 'str', 'str', 'str', 'str',
                                          'str', 'str', 'str', 'str', 'str',
                                          'str', 'str', 'str', 'str', 'str'])

        # create empty data frame for recommendation classification
        df_rec_classif = self.df_empty(
            ["rec_name", "rec_num"], dtypes=['str', 'str'])

        # for loop over recommendation series
        for serie in range(0, len(series)):

            id_series = series[serie]
            print("Now getting recommendation series: " +
                  id_series + " Time: " + str(datetime.datetime.now()))
            url = self.url_main + '/index.aspx?ser=' + id_series

            # get selenium started and open url
            print(url)
            print(driver_file)
            driver = webdriver.Chrome(executable_path=driver_file)
            driver.get(url)

            # expand tree
            j = 1
            elem = driver.find_elements_by_tag_name('b')
            len_elem = len(elem)
            while (j != len_elem):
                elem[j].click()
                time.sleep(2)
                elem = driver.find_elements_by_tag_name('b')
                len_elem = len(elem)
                j += 1

            # get html code for page with expanded tree of recommendations
            raw_html = driver.page_source

            # close browser
            driver.quit()

            # parse html code from that webpage
            soup = BeautifulSoup(raw_html, 'html.parser')

            # get specific part of html code
            html = soup.find_all(id='ctl00_content_result_table_hidden')

            # get all rows in that table
            recommendations = html[0].find_all('tr')

            # get rid of first row?
            recommendations = recommendations[1:len(recommendations)]

            # for loop over all recommendations
            for recommendation in recommendations:

                # get recommendation classification just row by row
                try:
                    rec_name = recommendation.text
                    rec_num = '-'
                except:
                    pass

                try:
                    rec_name = recommendation.find('a')['title']
                    rec_num = recommendation.find('a').find('u').text
                except:
                    pass

                # store in data frame
                df_rec_class = pd.DataFrame(
                    {"rec_name": rec_name, "rec_num": rec_num}, index=['IDX'])

                # append to dataframe
                df_rec_classif = df_rec_classif.append(df_rec_class)

                # if substring of nextlink jump over to next link
                if 'rec.aspx' in recommendation.find('a')['href']:

                    try:
                        print("Current rec number: " + str(recommendation.find('a').find(
                            'u').text) + " Time: " + str(datetime.datetime.now()))
                    except:
                        print("No current rec number found!")

                    # next link to get further metadata and download link for recommendation
                    nextlink = self.url_main + '/' + \
                        recommendation.find('a')['href']

                    # get raw html code to get further information for recommendation
                    raw_html2 = self.get_content(nextlink)

                    # parse html code of that webpage
                    soup2 = BeautifulSoup(raw_html2, 'html.parser')

                    # get specific tables of html code
                    # <table style="border: solid 1px #003366;">
                    html2 = soup2.find_all(
                        'table', attrs={'style': 'border: solid 1px #003366;'})

                    # number three is the table with all recommendation documents
                    rows = html2[3].find_all('tr')

                    # skip first row because it only contains column names and stuff
                    rows = rows[1:len(rows)]

                    # for loop over all versions of the focal recommendation
                    for row in rows:

                        # reduce html code of each row
                        entry = row.find_all('span')

                        # get link for recommendation metadata
                        recommendation_link = self.url_main + \
                            re.sub('^./', '/', entry[1].find('a')['href'])

                        # LOAD RECOMMENDATION LINK
                        # get html code for page with download link for recommendatoin
                        raw_html3 = self.get_content(recommendation_link)

                        # parse html code
                        soup3 = BeautifulSoup(raw_html3, 'html.parser')

                        # identify table which contains download link
                        html3 = soup3.find_all(
                            'table', attrs={'style': 'border: solid 1px #003366;'})

                        # GET INFORMATION

                        # get download link for recommendation
                        try:
                            download_link_recommendation = html3[1].find('a')[
                                'href']
                        except:
                            download_link_recommendation = '-'

                        # get table for meta data on recommendations and go into rows
                        html_meta = html3[2].find_all('tr')

                        # check variable name and store information
                        # identify which row in html_meta contains 'Citation'
                        rec_meta = []
                        meta = 0

                        for html_meta_row in html_meta:
                            try:
                                colname = html_meta_row.find(
                                    'td', class_='cell_left').text
                            except:
                                colname = '-'

                            rec_meta.append([meta, colname])
                            meta += 1

                        rec_meta2 = [rec_meta2entry[1]
                                     for rec_meta2entry in rec_meta]

                        # determine number of entry for specific columns
                        try:
                            idx_cit = [idx for idx, s in enumerate(
                                rec_meta2) if 'Citation' in s][0]
                            citation = html_meta[idx_cit].find('span').text
                        except:
                            citation = '-'

                        try:
                            idx_date = [idx for idx, s in enumerate(
                                rec_meta2) if 'date' in s][0]
                            approval_date = html_meta[idx_date].find(
                                'span').text
                        except:
                            approval_date = '-'

                        try:
                            idx_identical = [idx for idx, s in enumerate(
                                rec_meta2) if 'Identical' in s][0]
                            identical_standard = html_meta[idx_identical].find(
                                'td', class_='cell_right').text
                        except:
                            identical_standard = '-'

                        try:
                            idx_name = [idx for idx, s in enumerate(
                                rec_meta2) if 'Provisional' in s][0]
                            provisional_name = html_meta[idx_name].find(
                                'td', class_='cell_right').text
                        except:
                            provisional_name = '-'

                        try:
                            idx_process = [idx for idx, s in enumerate(
                                rec_meta2) if 'process' in s][0]
                            approval_process = html_meta[idx_process].find(
                                'td', class_='cell_right').text
                        except:
                            approval_process = '-'

                        try:
                            idx_observation = [idx for idx, s in enumerate(
                                rec_meta2) if 'Observation' in s][0]
                            observation = html_meta[idx_observation].find(
                                'td', class_='cell_right').text
                        except:
                            observation = '-'

                        try:
                            idx_maintenance = [idx for idx, s in enumerate(
                                rec_meta2) if 'Maintenance' in s][0]
                            maintenance_responsibility = html_meta[idx_maintenance].find(
                                'span').text
                            maintenance_responsibility_link = html_meta[idx_maintenance].find('a')[
                                'href']
                        except:
                            maintenance_responsibility = '-'
                            maintenance_responsibility_link = '-'

                        try:
                            idx_details = [idx for idx, s in enumerate(
                                rec_meta2) if 'Further' in s][0]
                            further_details = html_meta[idx_details].find(
                                'span').text
                            further_details_link = self.url_main + \
                                re.sub(
                                    '^./', '/', html_meta[idx_details].find('a')['href'])
                        except:
                            further_details = '-'
                            further_details_link = '-'

                        # get info from rows in table
                        try:
                            edition_number = entry[0].find('b').text
                        except:
                            edition_number = entry[0].text

                        recommendation_title = entry[1].find('a')['title']
                        recommendation_number = entry[1].find('a').text
                        recommendation_link = self.url_main + \
                            re.sub('^./', '/', entry[1].find('a')['href'])
                        status = entry[2].text

                        print("Current rec number with version: " +
                              recommendation_number + " Time: " + str(datetime.datetime.now()))

                        try:
                            link_summary_raw = entry[3].find('div')['onclick']
                            link_summary_regex = re.compile(
                                "(?<=window.open\(')(.*)(?=', 'Summary')")
                            link_summary = link_summary_regex.findall(link_summary_raw)[
                                0]

                            # get content of link_summary
                            raw_html_sum = self.get_content(link_summary)
                            soup_sum = BeautifulSoup(
                                raw_html_sum, 'html.parser')
                            summary_text = soup_sum.find(
                                'p', class_='MsoNormal').text
                        except:
                            link_summary = "-"
                            summary_text = "-"

                        try:
                            link_toc_raw = entry[4].find('div')['onclick']
                            link_toc_regex = re.compile(
                                "(?<=window.open\(')(.*)(?=', 'ToC')")
                            link_toc = link_toc_regex.findall(link_toc_raw)[0]
                            raw_html_toc = self.get_content(link_toc)
                            soup_toc = BeautifulSoup(
                                raw_html_toc, 'html.parser')
                            toc_text = soup_toc.find(
                                'p', class_='MsoNormal').text
                        except:
                            link_toc = "-"
                            toc_text = "-"

                        # store in data frame
                        df_res = pd.DataFrame({"recommendation_number": recommendation_number,
                                               "edition_number": edition_number,
                                              "recommendation_title": recommendation_title,
                                               "status": status, "approval_date": approval_date,
                                               "approval_process": approval_process,
                                               "identical_standard": identical_standard,
                                               "recommendation_link": recommendation_link,
                                               "link_summary": link_summary,
                                               "summary_text": summary_text,
                                               "link_toc": link_toc,
                                               "toc_text": toc_text,
                                               "provisional_name": provisional_name,
                                               "observation": observation,
                                               "citation": citation,
                                               "maintenance_responsibility": maintenance_responsibility,
                                               "maintenance_responsibility_link": maintenance_responsibility_link,
                                               "further_details": further_details,
                                               "further_details_link": further_details_link,
                                               "download_link_recommendation": download_link_recommendation},
                                              index=['IDX'])

                        # append to data frame
                        df_output = df_output.append(df_res)

                        # rearrange order of columns
                        cols = ["recommendation_number", "edition_number",
                                "recommendation_title", "status",
                                "approval_date", "approval_process",
                                "identical_standard", "recommendation_link",
                                "link_summary",
                                "summary_text", "link_toc", "toc_text",
                                "provisional_name", "observation",
                                "citation", "maintenance_responsibility",
                                "maintenance_responsibility_link",
                                "further_details", "further_details_link",
                                "download_link_recommendation"]

                        df_output = df_output[cols]

        return df_output

    def download_standards(self, df_metadata, path, time_sleep=15):
        """Download standard documents        

        Parameters
        ----------
        df_metadata : DataFrame
            A data frame containing meta information on ITU-T standards. 
            Can be obtained from the function get_meta().
        path : str
            A path where documents are saved.
        time_sleep : int, optional
            Time to wait in seconds after each document download. The default is 15.

        Returns
        -------
        None.

        Examples
        ----------
        See https://github.com/lorenzbr/pystandards#readme

        """

        for j in range(0, len(df_metadata)):

            url = df_metadata['download_link_recommendation'][j]
            file = str(os.path.basename(df_metadata['citation'][j]))

            try:
                urllib.request.urlretrieve(url, path + file + ".pdf")

            except Exception as e:
                print(e)
                continue

            print(str(j) + " Time: " + str(datetime.datetime.now()))

            # wait approximately 15 seconds to not overload the server
            time.sleep(time_sleep + random.randint(-5, 5))

        print("Download completed!")
