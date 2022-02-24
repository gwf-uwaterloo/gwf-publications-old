from pybtex.database import parse_string, parse_file, parse_bytes
from glob import glob
from pathlib import Path
import json
import sys

def bibtex_to_dicts(bibtex_data):
    bib_dict_list = []
    for entry in bibtex_data.entries.values():
        bibdict = {}
        try:
            for field, value in entry.fields.items():
                if type(value) == str and len(value) > 1 and value[0] == "{" and value[-1] == "}":
                    bibdict[field] = value[1:-1]
                else:
                    bibdict[field] = value
            for key, value in entry.persons.items():
                bibdict[key] = [str(v) for v in value]
        except Exception as e:
            print (str(e))
        bib_dict_list.append(bibdict)
    return bib_dict_list

def bibdicts_to_CORES(bib_dict_list):
    CORES = []
    with open("CORE_template.json", "r") as file:
        template = json.loads(file.read())
    for bibdict in bib_dict_list:
        CORE = template.copy()
        for key, value in bibdict.items():
            try:
                if key.lower() == "url":
                    CORE["downloadUrl"] = value
                elif key.lower() == "journal":
                    CORE["journals"] = [value]
                elif key.lower() == "keywords":
                    CORE["topics"] = value.split(", ")
                elif key.lower() == "year":
                    CORE["year"] = int(value)
                elif "author" in key.lower():
                    CORE["authors"] = value
                elif key.lower() in CORE:
                    CORE[key.lower()] = value
            except Exception as e:
                print (str(e))
        CORES.append(CORE)
    return CORES

def index():
    if len(sys.argv) < 3:
        sys.exit()
    filenames = sys.argv[1]
    files = glob(filenames)
    destination = Path(sys.argv[2]) / "CORES_formated.json"

    for file in files:
        try:
            print (f"Converting for {file}...")
            bibtex_data = parse_file(file, bib_format = "bibtex")
            bib_dict_list = bibtex_to_dicts(bibtex_data)
            CORES = bibdicts_to_CORES(bib_dict_list)
            text = ""
            for CORE in CORES:
                text = text + json.dumps(CORE) + "\r\n"
            with open(destination, "a") as output_file:
                output_file.write(text)
        except Exception as e:
            print (str(e))

if __name__ == "__main__":
    index()