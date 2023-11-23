#!/usr/bin/env python3
import os
from datetime import datetime
from pathlib import Path

from lxml import etree

curPath = os.getcwd()
docPath = os.getenv("docPath", "docs")
docFile = Path(f"{curPath}/{docPath}/macwinnie_pyhelpers.html")

insert = etree.fromstring(
    Path(f"{curPath}/docs_author_info.html").read_text(), parser=etree.HTMLParser()
)
contents = etree.fromstring(
    docFile.read_text(),
    parser=etree.HTMLParser(),
)

date = datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
insert.find('.//span[@id="update_date"]').text = date

main = contents.find(".//main")
main.append(insert)

with docFile.open(mode="w", encoding="utf-8") as file:
    file.write(etree.tostring(contents).decode())
    file.close()
