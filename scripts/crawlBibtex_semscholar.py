import os
import json
import bibtexparser
import pandas as pd
from tqdm import tqdm
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter

opts = Options()
opts.add_argument("--headless")
browser = Firefox(options=opts)


def fetch_bib(url: str, output_file: str):
    """
    Crawl the Bibtex Entry of a Publication from Semantic Search
    with Selenium.
    Args::
    url: Link to the semantic scholar landing page of the publication
    output: Output Bib file

    Example: fetch_bib("https://www.semanticscholar.org/paper/e784370c56d4eef9ddd26ed08e4cb683ff00e7c9", "sample.bib")
    """
    browser.get(url)

    try:
        # Crawl Abstract
        _ = browser.find_element_by_css_selector("button.more").click()
        abs_result = browser.find_element_by_css_selector(
            "span[data-selenium-selector=text-truncator-text]"
        ).text

        # Crawl Bibtext
        _ = browser.find_element_by_css_selector("button.cite-button").click()
        results = browser.find_element_by_tag_name("cite")
        bib_text = results.text

        with open(output_file, "w") as bibfile:
            bibfile.write(bib_text)

        with open(output_file) as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file).entries
            bib_database[0]["abstract"] = abs_result.replace("\n", " ")
            bib_database[0]["author"] = ", ".join(
                bib_database[0]["author"].split(" and ")
            )
            bib_database[0]["url"] = url

            db = BibDatabase()
            db.entries = bib_database

        writer = BibTexWriter()
        writer.indent = "  "  # indent entries with 4 spaces instead of one
        writer.comma_first = False  # place the comma at the beginning of the line

        with open(output_file, "w") as bibfile:
            bibfile.write(writer.write(db))
    except:
        return False

    return True


if __name__ == "__main__":
    csv_file = "gwf_publications.csv"
    bib_files_path = "new_bib"

    paper_df = pd.read_csv(csv_file, header=0)
    url_list = list(paper_df["semantic_scholar_url"])

    for url in tqdm(url_list):
        output_file = os.path.join(bib_files_path, url.split("/")[-1] + ".bib")
        if os.path.exists(output_file):
            fetch_bib(url, output_file)
