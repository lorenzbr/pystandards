## Webscraper for ITU-T standard documents and metadata
## Website: https://www.itu.int/ITU-T/recommendations
## e.g., https://www.itu.int/ITU-T/recommendations/index.aspx?ser=A

from itut_standards import itut_standards

itut_std = itut_standards(verbose = True)

## all different rec series of ITU-T recommendations
# series = ['A','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','X','Y','Z']
series = ['A']

## specify which driver to use for selenium (only works with Google Chrome)
driver_file = "chromedriver.exe"


## example

# get meta information
df_output = itut_std.get_meta(series, driver_file)

df_download = df_output[0:3]

# download standard documents as PDFs
itut_std.download_standards(df_download, path = "")

