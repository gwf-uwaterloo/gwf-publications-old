import os
import re
import json
import time
import requests
import difflib
import bibtexparser
import pandas as pd
from tqdm import tqdm
import nltk
from nltk.corpus import stopwords
import selenium
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

opts = Options()
opts.add_argument("--headless")
browser = Firefox(options=opts)

nltk.download("stopwords")
list_stopwords = list(stopwords.words("english"))


def fetch_bib(url: str):
    """
    Crawl the Bibtex Entry of a Publication from Semantic Scholar
    with Selenium.
    Args::
    url: Link to the semantic scholar landing page of the publication
    output: Output Bib Text

    Example: fetch_bib("https://www.semanticscholar.org/paper/e784370c56d4eef9ddd26ed08e4cb683ff00e7c9")
    """
    print(url)
    browser.get(url)

    try:
        _ = browser.find_element_by_css_selector(
            "div.copyright-banner__dismiss-btn"
        ).click()
    except selenium.common.exceptions.NoSuchElementException as e:
        print(
            f" Copyright-Banner Absent, Element ==> (div.copyright-banner__dismiss-btn)"
        )

    try:
        # Crawl Bibtext by clicking the cite button
        _ = browser.find_element_by_css_selector("button.cite-button").click()
        results = browser.find_element_by_css_selector(
            "cite.formatted-citation--style-bibtex"
        )
        # results = browser.find_element_by_xpath("//pre[@class='bibtex-citation']")
        _ = dir(results)
        bib_text = results.text
        browser.refresh()
        print(bib_text)
    except selenium.common.exceptions.NoSuchElementException as e:
        print(
            f"Paper has no citation on Semantic Scholar, Element ==> (button.cite-button)"
        )

    try:
        # Crawl Abstract
        _ = browser.find_element_by_css_selector("button.more").click()
        abs_result = browser.find_element_by_css_selector(
            "span[data-selenium-selector=text-truncator-text]"
        ).text
        browser.refresh()
    except selenium.common.exceptions.NoSuchElementException as e:
        abs_result = None
        print(
            f"Paper has no abstract on Semantic Scholar, Element ==> (span[data-selenium-selector=text-truncator-text])"
        )

    # parse bibtex
    bib_dict = bibtexparser.loads(bib_text).entries[0]
    bib_dict["abstract"] = abs_result if abs_result is not None else ""
    bib_dict["author"] = ", ".join(bib_dict["author"].split(" and "))

    return bib_dict


def get_url_from_doi(doi: str, config: dict, retry_iter: int = 3):
    """
    This function used the article unique doi identifier to
    fetch the Semantic Scholar landing page URL using the
    Semantic Scholar API. Sometimes the API times out, the function
    automatically retries

    Arguments:
    doi: str = article unique doi number
    Returns:
    Semantic Scholar Landing Page URL
    """
    try:
        api_url = config["paper_url"] + doi
        r = requests.get(url=api_url.strip())
        data = r.json()
        if not "error" in list(data.keys()):
            sem_landing_url = data["url"]
    except KeyError as e:
        iteration = retry_iter
        sem_landing_url = None
        while iteration != 0:
            print("[ERROR] Timeout; Trying again")
            iteration -= 1
            time.sleep(500)
            api_url = config["paper_url"] + doi
            r = requests.get(url=api_url.strip())
            data = r.json()
            try:
                sem_landing_url = data["url"]
            except:
                sem_landing_url = None
            print(iteration)
            if sem_landing_url != None:
                break

    return sem_landing_url


def extract_dois(publication: str, config, split_string: str):
    """
    This function extracts the doi number from a piece of string
    and then calls the `get_url_from_doi` to generate the landing
    page of the article
    """

    def publist2url(publication_list: list):
        publication_list = [
            item for item in publication_list[1:] if item.find("10.") != -1
        ]
        doi = publication_list[0].split()[0]

        doi = (
            doi
            if not (doi.endswith(".") or doi.endswith(",") or doi.endswith(")"))
            else doi[:-1]
        )
        doi = doi[doi.find("10.") :]
        return doi

    try:
        publication_list = publication.split(split_string)
        doi = publist2url(publication_list)
        sem_landing_url = get_url_from_doi(doi, config)
    except:
        try:
            publication_list = publication.replace(" ", "").split(split_string)
            doi = publist2url(publication_list)
            sem_landing_url = get_url_from_doi(doi, config)
        except:
            print("Could not fetch semantic scholar landing url")
            sem_landing_url = None

    return sem_landing_url


def fetch_url_no_doi(publication: str):
    """
    Fetch the Semantic Scholar landing page url for  an Article
    without a doi link
    """
    string_check = re.compile("[@_!#$%^&*()<>?/\|}{~:-]")
    paper_url = "https://api.semanticscholar.org/v1/paper/"
    search_url = "https://api.semanticscholar.org/graph/v1/paper/search?"
    print(publication)

    pub = re.sub("([A-Z][.][A-Z][.][,])", "", publication)
    pub = re.sub("([A-Z][.][,])", "", publication)
    pub = re.sub("([A-Z][.][A-Z][.])", "", pub).replace(".", "").replace('"', "")
    pub = re.sub("([A-Z][.])", "", pub).replace("’", "").replace("'", "")
    pub = re.sub("([(][0-9]{4}[)])", "", pub)

    pub = [i for item in pub.split(",") for i in item.strip().split()]
    pub = [item for item in pub if item.lower() not in list_stopwords and len(item) > 2]

    pub = [
        item
        for item in pub
        if (string_check.search(item) == None) and not bool(re.search(r"\d", item))
    ]

    i = 6
    while True:
        try:
            query = "+".join(pub[:i]).lower()
            break
        except:
            i -= 1
    print("[Query]:  " + query)

    PARAMS = {"offset": 0, "limit": 50, "query": query}

    r = requests.get(url=search_url, params=PARAMS)
    try:
        data = r.json()
        if data["total"] > 1:
            score = []
            for paper in data["data"]:
                temp = difflib.SequenceMatcher(None, paper["title"], publication)
                score.append(temp.ratio())

            url2 = paper_url + data["data"][score.index(max(score))]["paperId"]
        else:
            url2 = paper_url + data["data"][0]["paperId"]

        r2 = requests.get(url=url2)
        data2 = r2.json()
        sem_landing_url = data2["url"]
    except:
        sem_landing_url = None

    return sem_landing_url
