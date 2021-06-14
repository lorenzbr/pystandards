# pystandards

Crawl and download meta information and documents on technical standards and contributions


## Installation

You can install the development version from [GitHub](https://github.com/) with:

``` python
pip install git+https://github.com/lorenzbr/pystandards.git
```

Please make sure you have [Google Chrome](https://www.google.com/chrome/) and the corresponding chromedriver.exe (see [here](https://chromedriver.chromium.org/downloads)) installed to crawl meta information on ITU-T recommendations.


## Functions

* Crawl meta information on IEEE contributions (see [here](https://mentor.ieee.org/802))
    * You can find the name of a standard (_std_name_) by clicking on the standard of interest. The standard name can be extracted from the URL as follows: https://mentor.ieee.org/[standard name]/documents (e.g., 802.11, 802.16, ...)
    * Please specify from which pages you want to get the meta information (_start_page_ and _end_page_)
* Download IEEE contribution documents (see [here](https://mentor.ieee.org/802))
    * A data frame which contains the meta information on IEEE contributions, i.e. it has at least the three columns _dl_link_, _file_ and _doc_type_
    * A path where documents are saved
* Crawl meta information on ITU-T recommendations/standards (see [here](https://www.itu.int/ITU-T/recommendations))
    * Specify the recommendation series (e.g., A, G, H, ...)
    * Provide path and name of the Chrome driver
* Download ITU-T recommendation/standard documents (see [here](https://www.itu.int/ITU-T/recommendations))
    * A data frame which contains the meta information of ITU-T standards, i.e. it has at least the two columns _download_link_recommendation_ and _citation_
    * A path where documents are saved

To parse standard documents and for related functions (e.g., accessing ETSI standard documents), see [here](https://github.com/lorenzbr/techStandards).


## Examples

```python
## Crawl meta information and download IEEE contributions
from pystandards.ieee_contributions import ieee_contributions
ieee_contr = ieee_contributions(verbose = True)
# Name of the WiFi standard
std_name = "802.11"
# Get meta information
df_output = ieee_contr.get_meta(std_name, start_page = 1, end_page = 3)
# Download three contribution documents
df_download = df_output[0:3]
ieee_contr.download_contributions(df_download, path = "")

## Crawl meta information and download ITU-T recommendations
from pystandards.itut_standards import itut_standards
itut_std = itut_standards(verbose = True)
series = ['A']
## Specify the Chrome driver to use Selenium (Google Chrome needs to be installed)
driver_file = "chromedriver.exe"
# Get meta information
df_output = itut_std.get_meta(series, driver_file)
# Download three standard documents as PDFs
df_download = df_output[0:3]
itut_std.download_standards(df_download, path = "")
```


## License

This repository is licensed under the MIT license.

See [here](https://github.com/lorenzbr/pystandards/blob/master/LICENSE) for further information.