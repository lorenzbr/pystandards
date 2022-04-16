# Webscraper for meta data and download link for IEEE contributions
# Website https://mentor.ieee.org/802/

from pystandards.ieee_contributions import ieee_contributions

ieee_contr = ieee_contributions(verbose=True)

# 802.11: max page number 698 as of 21 Sep. 2020
# 802.15: max page number 225 as of 24 Sep. 2020
# 802.22: max page number: 47
# 802.16: max page number: 21 as of 24 Sep. 2020
# 802.24: max page number: 5
# ... see website for further standards

# Name of standard
standard_name = "802.11"
# standard_name = "802.15"
# standard_name = "802.16"
# ...

# Example

# Get meta information
df_output = ieee_contr.get_meta(standard_name, start_page=1, end_page=3)

df_download = df_output[0:3]

# Download contributions
ieee_contr.download_contributions(df_download, path="")
