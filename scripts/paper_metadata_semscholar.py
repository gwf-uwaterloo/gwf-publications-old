import requests
import time
import json
import pandas as pd

CITATION_URL = (
    "https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?fields={fields}&offset={"
    "offset}&limit=999 "
)
REFERENCES_URL = (
    "https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references?fields={"
    "fields}&offset=0&limit=999 "
)
PAPER_URL = "https://api.semanticscholar.org/v1/paper/{paper_id}"

FIELDS = [
    "authors",
    "venue",
    "title",
    "url",
    "year",
    "doi",
    "arxivId",
    "abstract",
    "citations",
]


def fetch_citations(paper_id, citation_url: str = CITATION_URL):
    offset = 0
    assert isinstance(paper_id, str)

    citation_url = citation_url.replace("{paper_id}", paper_id)
    citation_url = citation_url.replace("{fields}", ",".join(fields))

    citation_url_new = citation_url.replace("{offset}", str(offset))
    r = requests.get(url=citation_url_new)
    data = r.json()

    citation_list = []
    citation_list += [x["citingPaper"] for x in data["data"]]

    data_len = len(data["data"])

    while data_len >= 999:
        offset += 999
        citation_url_new = citation_url.replace("{offset}", str(offset))
        r = requests.get(url=citation_url_new)
        data = r.json()
        citation_list += [x["citingPaper"] for x in data["data"]]
        data_len = len(data["data"])

    return citation_list


def fetch_references(paper_id: str, references_url: str = REFERENCES_URL):
    offset = 0
    references_url = references_url.replace("{paper_id}", paper_id)
    references_url = references_url.replace("{fields}", ",".join(fields))

    references_url_new = references_url.replace("{offset}", str(offset))
    r = requests.get(url=references_url_new)
    data = r.json()

    ref_list = []
    ref_list += [x["citedPaper"] for x in data["data"]]

    data_len = len(data["data"])

    while data_len >= 999:
        offset += 999
        references_url_new = references_url.replace("{offset}", str(offset))
        r = requests.get(url=references_url_new)
        data = r.json()
        ref_list += [x["citedPaper"] for x in data["data"]]
        data_len = len(data["data"])

    return ref_list


def fetch_paper_metadata(
    paper_id: str, fields: list = FIELDS, paper_url: str = PAPER_URL
):
    print(f"paper id {paper_id}")
    paper_url = paper_url.replace("{paper_id}", paper_id)

    try:
        r = requests.get(url=paper_url)
        data = r.json()
        metadata = [data[i] for i in fields]
    except:
        try:
            time.sleep(300)
            r = requests.get(url=paper_url)
            data = r.json()
            metadata = [data[i] for i in fields]
        except:
            time.sleep(300)
            r = requests.get(url=paper_url)
            data = r.json()
            metadata = [data[i] for i in fields]
    return metadata


if __name__ == "__main__":
    df = pd.read_csv("data/gwf_2019_peer_review_articles.csv").fillna(0)
    paper_list = [
        url.split("/")[-1] for url in list(df["semantic_scholar_url"]) if url != 0
    ]

    nl_metadata = {lis: fetch_paper_metadata(lis, fields=FIELDS) for lis in paper_list}

    with open("files/gwf_paper_metadata.json", "w") as outfile:
        json.dump(nl_metadata, outfile)
