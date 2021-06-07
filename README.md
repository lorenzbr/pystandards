# pystandards

Crawl and download meta information and documents on technical standards and contributions


## Installation

You can install the development version from [GitHub](https://github.com/) with:

``` python
pip install git+https://github.com/lorenzbr/pystandards.git
```

Please make sure you have [Google Chrome](https://www.google.com/chrome/) and the corresponding chromedriver.exe (see [here](https://chromedriver.chromium.org/downloads)) installed to crawl meta information on ITU-T recommendations.

## Functions

* Crawl meta information on IEEE contributions [here](https://mentor.ieee.org/802)
* Download IEEE contribution documents [here](https://mentor.ieee.org/802)
* Crawl meta information on ITU-T recommendations/standards [here](https://www.itu.int/ITU-T/recommendations)
* Download ITU-T recommendation/standard documents [here](https://www.itu.int/ITU-T/recommendations)

To parse standard documents and for related functions (e.g., accessing ETSI standard documents), see [here](https://github.com/lorenzbr/techStandards).

## Examples

```python
## Crawl meta information and download IEEE contributions
from ieee_contributions import ieee_contributions
ieee_contr = ieee_contributions(verbose = True)
# name of standard
standard_name = "802.11"
# get meta information
df_output = ieee_contr.get_meta(standard_name, start_page = 1, end_page = 3)
# download contributions
df_download = df_output[0:3]
ieee_contr.download_contributions(df_download, path = "")

## Crawl meta information and download ITU-T recommendations
from itut_standards import itut_standards
itut_std = itut_standards(verbose = True)
series = ['A']
## specify the Chrome driver to use for selenium (have Google Chrome installed)
driver_file = "chromedriver.exe"
# get meta information
df_output = itut_std.get_meta(series, driver_file)
# download standard documents as PDFs
df_download = df_output[0:3]
itut_std.download_standards(df_download, path = "")
```

## Contact

Please contact <lorenz.brachtendorf@gmx.de> if you want to contribute to this project.

You can also submit bug reports and suggestions via e-mail or <https://github.com/lorenzbr/pystandards/issues> 


## License

This repository is licensed under the MIT license.

See [here](https://github.com/lorenzbr/pystandards/blob/master/LICENSE) for further information.