import os
from pprint import pprint

import pymupdf
from requests import Session

url_ar_6_report = (
    "https://www.ipcc.ch/report/ar6/syr/downloads/report/IPCC_AR6_SYR_LongerReport.pdf"
)
local_ar6_report = ".data/ar6_report.pdf"

os.makedirs(".data/images/", exist_ok=True)

# --------------------------------------------------------------------------------
# Downloading file if missing
# --------------------------------------------------------------------------------
with Session() as session:
    if os.path.exists(local_ar6_report):
        print("Skipping report download")
    else:
        print("Downloading report")
        headers = {
            "User-Agent": "Mozilla/5.0",
        }
        r = session.get(url_ar_6_report, headers=headers, allow_redirects=True)
        open(local_ar6_report, "wb").write(r.content)

        print("> Done")


# --------------------------------------------------------------------------------
# Parsing file (using PyMuPDF : https://pymupdf.readthedocs.io/en/latest/the-basics.html )
# --------------------------------------------------------------------------------


doc = pymupdf.open(local_ar6_report)  # open a document
with open(".data/out.txt", "wb") as text_file:
    for page in doc:  # iterate the document pages
        text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)
        text_file.write(text)  # write text of page
        text_file.write(bytes((12,)))  # write page delimiter (form feed 0x0C)

for page_index in range(len(doc)):  # iterate over pdf pages
    page = doc[page_index]  # get the page
    image_list = page.get_images()

    # print the number of images found on the page
    if image_list:
        print(f"Found {len(image_list)} images on page {page_index}")
    else:
        print("No images found on page", page_index)

    for image_index, img in enumerate(image_list, start=1):  # enumerate the image list
        xref = img[0]  # get the XREF of the image
        pix = pymupdf.Pixmap(doc, xref)  # create a Pixmap

        if pix.n - pix.alpha > 3:  # CMYK: convert to RGB first
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

        pix.save(
            ".data/images/page_%s-image_%s.png" % (page_index, image_index)
        )  # save the image as png
        pix = None


for page in doc:  # iterate the document pages
    tabs = page.find_tables()  # locate and extract any tables on page
    print(f"{len(tabs.tables)} found on {page}")  # display number of found tables

    for tab in tabs.tables:  # at least one table found?
        pprint(tab.extract())  # print content of first table

    out.close()

print("OK")
