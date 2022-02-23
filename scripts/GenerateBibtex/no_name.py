import yaml
import pandas as pd
from typing import Any
from typing import Dict
from utils import extract_dois, fetch_bib
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter


class GenerateBibtex:
    def __init__(self, config_path: str = "scripts/GenerateBibtex/config.yaml"):
        self.config_path = config_path
        self.config_dict = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        loads yaml configuration file.
        """
        conf_file = yaml.full_load(open(self.config_path, "r"))
        return conf_file

    def generate_bib(self, bib_path: str):
        bib_collection = [fetch_bib(url) for url in self.url_list if url is not None]
        db = BibDatabase()
        db.entries = bib_collection
        writer = BibTexWriter()
        writer.indent = "    "  # indent entries with 4 spaces instead of one
        writer.comma_first = False  # place the comma at the beginning of the line
        with open(bib_path, "w") as bibfile:
            bibfile.write(writer.write(db))

    def fetch_semantic_scholar(self, file_path: str):
        """
        This function generates the semantic scholar landing page URL for
        Articles in a CSV/XLSX file with a doi link

        Args:
        Input: csv/xlsx file containing the publications in the first column
        The publications should contain a doi link in any of the formats
        'doi:10.2134/jeq2018.07.0280.' or 'https://doi.org/10.1016/j.jhydrol.2020.124541.'

        e.g of publication ==>
        "Wilson, H., Elliott, J., Macrae, M. and Glenn, A. (2019).
        Near-surface soils as a source of phosphorus in snowmelt runoff from cropland.
        Journal of Environmental Quality, 48(4):921-930. doi:10.2134/jeq2019.04.0155."

        """
        paper_df = (
            pd.read_excel(file_path, header=0).fillna("")
            if file_path.endswith(".xlsx")
            else pd.read_csv(file_path, header=0, encoding="iso8859_16").fillna("")
        )

        if "semantic_scholar_url" in list(paper_df.columns):
            url_list = paper_df["semantic_scholar_url"].tolist()
        else:
            url_list = [None] * len(paper_df)
            paper_df["semantic_scholar_url"] = url_list
            paper_df = paper_df.fillna("")

        for i in range(len(paper_df)):
            publication = paper_df.loc[i][0].lower().strip()

            if paper_df.loc[i]["semantic_scholar_url"] == "":
                if publication.find("doi.org/", 0) != -1:
                    print(f"[INFO] Article {i + 2}: doi number present in string")
                    sem_landing_url = extract_dois(
                        publication, self.config_dict, "doi.org/"
                    )
                elif publication.find("doi:", 0) != -1:
                    print(f"[INFO] Article {i + 2}: doi number present in string")
                    sem_landing_url = extract_dois(
                        publication, self.config_dict, "doi:"
                    )
                else:
                    publication = paper_df.loc[i][0]
                    print(f"[INFO] Article {i + 2}: doi number absent in string")
                    sem_landing_url = None  # fetch_url_no_doi(publication)

                print(sem_landing_url)
                url_list[i] = sem_landing_url
            else:
                pass

        paper_df["semantic_scholar_url"] = url_list
        self.url_list = url_list
        return paper_df


if __name__ == "__main__":
    excel_file = "/Users/mac/Desktop/gwf_publications.csv"
    generator = GenerateBibtex()
    df = generator.fetch_semantic_scholar(excel_file)
    generator.generate_bib("output.bib")
