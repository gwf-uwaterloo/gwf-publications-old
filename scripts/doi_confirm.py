import sys
import urllib.request
from urllib.error import HTTPError
import json

BASE_URL = 'http://dx.doi.org/'

def load_ref_data():
    try:
        file = open("ref_data.json", "r", errors = "ignore")
        data = file.read()
        file.close()
        ref_data, missing_DOIs = [], []
        ref_data = json.loads(data)
        
        for iter, ref in enumerate(ref_data):
            if ref["doi"] == "":
                missing_DOIs.append(iter)
        return ref_data, missing_DOIs
    except Exception as e:
        print (str(e))
        exit(1)
 
def get_bibtex(ref_data):
    found_doi = [False for i in range(len(ref_data))]
    for index in range(len(ref_data)):
        if ref_data[index]["doi"] != "":
            doi = ref_data[index]["doi"].split(";")[0]
            if doi[-1] == ".":
                doi = doi[:-1]
            url = BASE_URL + doi
            print (url)
            
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/x-bibtex')
            try:
                with urllib.request.urlopen(req) as f:
                    bibtex = f.read().decode()
                try:
                    title = bibtex.split("title = {")[1].split("}")[0]
                    found_doi[index] = title.lower() in ref_data[index]["text"].lower()
                    print (index, found_doi[index])
                    if not found_doi[index]:
                        print (title)
                        print (ref_data[index]["text"])
                except Exception as e:
                    continue
            except HTTPError as e:
                if e.code == 404:
                    print('DOI not found.')
                else:
                    print('Service unavailable.')
            print ("#"*60)
    return found_doi
        
def magic():
    a, b = load_ref_data()
    c = get_bibtex(a)
    return c
        
        