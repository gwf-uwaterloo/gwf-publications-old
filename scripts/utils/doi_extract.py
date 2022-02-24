import re
import requests
from requests.exceptions import Timeout
import json
from google import google
import sys
import urllib.request
from urllib.error import HTTPError
from pybtex.database import parse_string

ref_data = []
missing_DOIs = []
doi_reg = r'10\.\d+/[-\.;()/:\w]+'
BASE_URL = 'http://dx.doi.org/'

def ref_extract(reftext):
    global doi_reg
    
    reftext = reftext.strip()
    reftext = reftext.replace("doi:", "")
    reftext = reftext.replace("DOI:", "")
    reftext = reftext.replace("Doi:", "")
    reftext = reftext.replace("https://doi.org/", "")
    
    extract = {"doi": "", "text": ""}
    
    m = re.findall(doi_reg, reftext)
    if m:
        extract["doi"] = m[0].strip()
        extract["text"] = reftext.split(m[0])[0].strip()
    else:
        extract["text"] = reftext
        
    return extract
    
def save_ref_data(ref_data, csv = False):
    file = open("ref_data.json", "w")
    file.write(json.dumps(ref_data, indent = 2))
    file.close()
    
    if csv:
        data = "doi,text\n"
        for ref in ref_data:
            if ref["doi"] != "" and ref["doi"][-1] == ".":
                data = data + ref["doi"][:-1] + "," + ref["text"].replace(",", ";") + "\n"
            else:
                data = data + ref["doi"] + "," + ref["text"].replace(",", ";") + "\n"
        file = open("ref_data.csv", "w")
        file.write(data)
        file.close()
        
def save_bibtex_data(bibtex_data, csv = False):
    file = open("bibtex_data.json", "w")
    file.write(json.dumps(bibtex_data, indent = 2))
    file.close()
    """
    if csv:
        data = "doi,bibtex,text\n"
        for item in bibtex_data:
            if item["doi"] != "" and item["doi"][-1] == ".":
                data = data + item["doi"][:-1] + "," + item["bibtex"].replace(",", ";") + "," + item["text"].replace(",", ";") + "\n"
            else:
                data = data + item["doi"] + "," + item["bibtex"].replace(",", ";") + "," + item["text"].replace(",", ";") + "\n"
        file = open("bibtex_data.csv", "w", encoding="utf-8")
        file.write(data)
        file.close()
    """
    if csv:
        data = "doi,text\n"
        for ref in bibtex_data:
            if ref["doi"] != "" and ref["doi"][-1] == ".":
                data = data + ref["doi"][:-1] + "," + ref["text"].replace(",", ";") + "\n"
            else:
                data = data + ref["doi"] + "," + ref["text"].replace(",", ";") + "\n"
        file = open("ref_data.csv", "w")
        file.write(data)
        file.close()
        
def load_bibtex_data():
    try:
        file = open("bibtex_data.json", "r", errors = "ignore")
        data = file.read()
        file.close()
        bibtex_data = []
        bibtex_data = json.loads(data)
        
        return bibtex_data
    except Exception as e:
        print (str(e))
        exit(1)
        
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
        
def read_ref_data(filename):
    # reads new references from a file
    try:
        file = open(filename, "r", errors = "ignore")
        data = file.read()
        file.close()
    except Exception as e:
        print (str(e))
        exit(1)
        
    data = data.splitlines()
    reftexts = [ref for ref in data if ref != ""]
    ref_data, missing_DOIs = [], []
    for iter, reftext in enumerate(reftexts):
        extract = ref_extract(reftext)
        ref_data.append(extract)
        if extract["doi"] == "":
            missing_DOIs.append(iter)  
    save_ref_data(ref_data)
    return ref_data, missing_DOIs
    
def doi_search(ref_data, missing_DOIs, num_page = 1, num_links = 2):
    try:
        for iter, index in enumerate(missing_DOIs):
            try:
                print (f"{iter} Searching Google for article at index {index}...")
                #print (ref_data[index]["text"])
                search_results = google.search(ref_data[index]["text"], num_page)
                print (f"{len(search_results)} results found")
                c = 0
                for result in search_results:
                    if result and result.link[-4:] in [".pdf", ".xls"]:
                        print ("PDF encountered and ignored")
                        continue
                    print (f"Searching link {c+1} for the DOI...")
                    print (result.link[-10:])
                    try:
                        html = requests.get(result.link, verify = False, timeout=(5, 10))
                        matches = re.findall(doi_reg, html.text)
                        if matches:
                            ref_data[index]["doi"] = matches[0]
                            save_ref_data(ref_data)
                            print (f"DOI found: {matches[0]} and saved!")
                            break
                    except Exception:
                        print('Something went wrong in http request. Skipping')
                        continue
                    c += 1
                    if c == num_links:
                        break
                print ("#"*90)
            except Exception as e:
                print (str(e))
                continue
    except Exception as e:
        print (str(e))
        exit(1)
        
def get_bibtex(ref_data):
    bibtex_data = []
    found_doi = [False for i in range(len(ref_data))]
    for index in range(len(ref_data)):
        print (index)
        bibtex_data.append({
            "doi": "",
            "text": ref_data[index]["text"],
            "bibtex": ""
        })
        if ref_data[index]["doi"] != "" and ref_data[index]["text"] != 0:
            doi = ref_data[index]["doi"].split(";")[0]
            if doi[-1] == ".":
                doi = doi[:-1]
            url = BASE_URL + doi
            
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/x-bibtex')
            try:
                with urllib.request.urlopen(req) as f:
                    bibtex = f.read().decode()
                bibtex_data[index]["doi"] = doi
                bibtex_data[index]["bibtex"] = bibtex
            except HTTPError as e:
                if e.code == 404:
                    print('DOI not found.')
                else:
                    print('Service unavailable.')
            print ("#"*60)
    return bibtex_data
    
def bibtex_to_dict(bibtex):
    try:
        bibdict = {}
        #['doi', 'url', 'year', 'month', 'publisher', 'pages', 'title', 'journal', 'volume', 'number', 'booktitle', 'keywords']
        bibtex = parse_string(bibtex, bib_format = "bibtex")
        entry = bibtex.entries.values()[0]
        
        for field in entry.fields.keys():
            bibdict[field] = entry.fields[field]
        
        for key in entry.persons.keys():
            bibdict[key] = []
            for people in entry.persons[key]:
                bibdict[key].append(str(people))
    except Exception as e:
        pass
    return bibdict
    
def bibdict_to_CORE(bibdict, coreId):
    CORE = {
        "coreId": None,
        "doi": None,  
        "oai": None, 
        "identifiers": [], 
        "title": None, 
        "authors": [], 
        "enrichments": {
            "references": [], 
            "documentType": {
                "type": None, 
                "confidence": None
            }
        }, 
        "contributors": [], 
        "datePublished": None, 
        "abstract": None, 
        "downloadUrl": None, 
        "fullTextIdentifier": None, 
        "pdfHashValue": None, 
        "publisher": None, 
        "rawRecordXml": None, 
        "journals": [], 
        "language": None, 
        "relations": [], 
        "year": None, 
        "topics": [], 
        "subjects": [], 
        "fullText": None
    }
    CORE["coreId"] = coreId
    for key in bibdict:
        if key == "url":
            CORE["downloadUrl"] = bibdict[key]
        elif key == "journal":
            CORE["journals"].append(bibdict[key])
        elif key == "keywords":
            CORE["topics"] = bibdict[key].split(", ")
        elif key in CORE:
            CORE[key] = bibdict[key]
    return CORE
    
def ref_to_CORE():
    # clear file
    with open("ref_CORE.json", "w") as file:
        file.write("")
    
    bibtex_data = load_bibtex_data()
    for iter, item in enumerate(bibtex_data):
        bibdict = bibtex_to_dict(item["bibtex"])
        CORE = bibdict_to_CORE(bibdict, iter)
        
        try:
            with open("ref_CORE.json", "a") as file:
                file.write(json.dumps(CORE) + "\n")
        except Exception as e:
            print (str(e))

def magic(fresh = False):
    if fresh:
        ref_data, missing_DOIs = read_ref_data("the_thing.txt")
    else:
        ref_data, missing_DOIs = load_ref_data()
    print (len(missing_DOIs))
    doi_search(ref_data, missing_DOIs)
    
def magic2():
    ref_data, missing_DOIs = load_ref_data()
    print (len(missing_DOIs))
    bibtex_data = get_bibtex(ref_data)
    save_bibtex_data(bibtex_data, csv = True)




        
        