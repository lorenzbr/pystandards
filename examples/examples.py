#### Webscraper for meta data and download link for IEEE contributions
#### Website https://mentor.ieee.org/802/bp/StartPage


from ieee_contributions import ieee_contributions


ieee_con = ieee_contributions(verbose = True)


## 802.11: max page number 698 as of 21 Sep. 2020
## 802.15: max page number 225 as of 24 Sep. 2020
## 802.22: max page number: 47
## 802.16: max page number: 21 as of 24 Sep. 2020
## 802.24: max page number: 5
## ... see website for further standards

## name of standard
standard_name = "802.11"
# standard_name = "802.15"
# standard_name = "802.16"
# ...

## example
df_output = ieee_con.get_contributions(standard_name, start_page = 1, end_page = 5)
