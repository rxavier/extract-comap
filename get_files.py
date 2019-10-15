import re

import requests
from bs4 import BeautifulSoup as bs

BASE_URL = "https://www.mef.gub.uy/568/7/areas/comision-de-aplicacion-de-la-ley-de-inversiones---uruguay"

page_response = requests.get(BASE_URL)

soup = bs(page_response.content, "html.parser")
for link in soup.find_all(href=re.compile("areas/comap")):
    response = requests.get(link["href"])
    with open(re.search("pdfs/Año [0-9]{4}", link.text).group(0) + ".pdf", "wb") as f:
        f.write(response.content)
